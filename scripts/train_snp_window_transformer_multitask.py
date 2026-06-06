#!/usr/bin/env python3
"""GPU training script for a window-token SNP Transformer.

The model is intentionally designed for 2 x A100 40GB:
- compress contiguous SNPs into window tokens with a learnable projection;
- train a Transformer encoder over windows rather than over 199k raw SNPs;
- support masked genotype pretraining and supervised multi-trait fine-tuning;
- evaluate with missing-target masks.

Example:
CUDA_VISIBLE_DEVICES=1,2 python scripts/train_snp_window_transformer_multitask.py \
  --data-dir data/deep_model/v0_1 --out-dir results/deep_model/windowformer_v0_1 \
  --mode supervised --epochs 300 --batch-size 32 --window-size 256
"""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data/deep_model/v0_1")
    parser.add_argument("--out-dir", default="results/deep_model/windowformer_v0_1")
    parser.add_argument("--mode", choices=["supervised", "pretrain", "finetune"], default="supervised")
    parser.add_argument("--pretrained-checkpoint", default="")
    parser.add_argument("--seed", type=int, default=20260606)
    parser.add_argument("--split-seed", type=int, default=20260605)
    parser.add_argument("--window-size", type=int, default=256)
    parser.add_argument("--d-model", type=int, default=192)
    parser.add_argument("--nhead", type=int, default=6)
    parser.add_argument("--layers", type=int, default=6)
    parser.add_argument("--dropout", type=float, default=0.15)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=300)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--mask-window-frac", type=float, default=0.15)
    parser.add_argument("--patience", type=int, default=40)
    return parser.parse_args()


def require_torch():
    try:
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader, Dataset
    except ImportError as exc:
        raise SystemExit(
            "PyTorch is not installed in this environment. Install a CUDA build first, for example:\n"
            "mamba run -n yumi python -m pip install torch --index-url https://download.pytorch.org/whl/cu121"
        ) from exc
    return torch, nn, DataLoader, Dataset


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def pearsonr_np(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) < 3:
        return float("nan")
    if np.std(y_true) <= 0 or np.std(y_pred) <= 0:
        return float("nan")
    return float(np.corrcoef(y_true, y_pred)[0, 1])


def r2_np(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    denom = float(np.sum((y_true - np.mean(y_true)) ** 2))
    if denom <= 0:
        return float("nan")
    return float(1.0 - np.sum((y_true - y_pred) ** 2) / denom)


def main() -> None:
    args = parse_args()
    torch, nn, DataLoader, Dataset = require_torch()
    set_seed(args.seed)

    data_dir = Path(args.data_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    genotype = np.load(data_dir / "genotype_samples_by_variants.int8.npy")
    targets = np.load(data_dir / "phenotype_targets.float32.npy")
    target_mask = np.load(data_dir / "phenotype_observed_mask.bool.npy")
    population = np.load(data_dir / "population_covariates.float32.npy")
    splits = np.genfromtxt(data_dir / "splits.tsv", delimiter="\t", dtype=str, names=True)
    split_rows = splits[splits["seed"].astype(int) == args.split_seed]
    split_map = {a: s for a, s in zip(split_rows["accession_id_norm"], split_rows["split"])}
    accessions = np.genfromtxt(data_dir / "accessions.tsv", delimiter="\t", dtype=str, names=True)["accession_id_norm"]
    split = np.array([split_map[str(a)] for a in accessions])

    n_samples, n_variants = genotype.shape
    n_traits = targets.shape[1]
    n_pop = population.shape[1]
    pad = (-n_variants) % args.window_size
    if pad:
        genotype = np.pad(genotype, ((0, 0), (0, pad)), constant_values=3)
    n_windows = genotype.shape[1] // args.window_size

    class ZeaDataset(Dataset):
        def __init__(self, indices: np.ndarray):
            self.indices = indices

        def __len__(self):
            return len(self.indices)

        def __getitem__(self, i):
            idx = int(self.indices[i])
            x = genotype[idx].reshape(n_windows, args.window_size).astype(np.int64)
            x = np.where((x >= 0) & (x <= 2), x, 3)
            return {
                "x": torch.from_numpy(x),
                "pop": torch.from_numpy(population[idx]),
                "y": torch.from_numpy(targets[idx]),
                "mask": torch.from_numpy(target_mask[idx].astype(np.float32)),
            }

    class SNPWindowFormer(nn.Module):
        def __init__(self):
            super().__init__()
            self.snp_embed = nn.Embedding(5, args.d_model)
            self.window_proj = nn.Sequential(
                nn.Linear(args.window_size * args.d_model, args.d_model),
                nn.LayerNorm(args.d_model),
                nn.GELU(),
                nn.Dropout(args.dropout),
            )
            self.pos = nn.Parameter(torch.zeros(1, n_windows, args.d_model))
            enc_layer = nn.TransformerEncoderLayer(
                d_model=args.d_model,
                nhead=args.nhead,
                dim_feedforward=args.d_model * 4,
                dropout=args.dropout,
                activation="gelu",
                batch_first=True,
                norm_first=True,
            )
            self.encoder = nn.TransformerEncoder(enc_layer, num_layers=args.layers)
            self.pop_proj = nn.Sequential(nn.Linear(n_pop, args.d_model), nn.LayerNorm(args.d_model), nn.GELU())
            self.head = nn.Sequential(
                nn.LayerNorm(args.d_model * 2),
                nn.Linear(args.d_model * 2, args.d_model),
                nn.GELU(),
                nn.Dropout(args.dropout),
                nn.Linear(args.d_model, n_traits),
            )
            self.reconstruct = nn.Linear(args.d_model, args.window_size * 3)

        def encode(self, x, pop, pretrain_mask=False):
            if pretrain_mask:
                mask = torch.rand(x.shape[:2], device=x.device) < args.mask_window_frac
                x = x.clone()
                x[mask] = 4
            else:
                mask = None
            z = self.snp_embed(x).reshape(x.shape[0], x.shape[1], -1)
            z = self.window_proj(z) + self.pos
            z = self.encoder(z)
            pooled = z.mean(dim=1)
            pop_z = self.pop_proj(pop)
            return z, torch.cat([pooled, pop_z], dim=1), mask

        def forward(self, x, pop):
            _, pooled, _ = self.encode(x, pop, pretrain_mask=False)
            return self.head(pooled)

        def pretrain_forward(self, x, pop):
            z, _, mask = self.encode(x, pop, pretrain_mask=True)
            logits = self.reconstruct(z).reshape(x.shape[0], x.shape[1], args.window_size, 3)
            return logits, mask

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SNPWindowFormer().to(device)
    if torch.cuda.device_count() > 1:
        model = nn.DataParallel(model)

    if args.pretrained_checkpoint:
        state = torch.load(args.pretrained_checkpoint, map_location="cpu")
        model.load_state_dict(state["model"], strict=False)

    train_idx = np.where(split == "train")[0]
    val_idx = np.where(split == "val")[0]
    test_idx = np.where(split == "test")[0]
    loaders = {
        "train": DataLoader(ZeaDataset(train_idx), batch_size=args.batch_size, shuffle=True, num_workers=2),
        "val": DataLoader(ZeaDataset(val_idx), batch_size=args.batch_size, shuffle=False, num_workers=2),
        "test": DataLoader(ZeaDataset(test_idx), batch_size=args.batch_size, shuffle=False, num_workers=2),
    }

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    best_val = math.inf
    stale = 0
    history = []

    def run_epoch(loader, train: bool):
        model.train(train)
        total = 0.0
        n = 0
        preds = []
        obs = []
        masks = []
        for batch in loader:
            x = batch["x"].to(device)
            pop = batch["pop"].to(device)
            y = batch["y"].to(device)
            mask = batch["mask"].to(device)
            with torch.set_grad_enabled(train):
                if args.mode == "pretrain":
                    logits, win_mask = model.module.pretrain_forward(x, pop) if hasattr(model, "module") else model.pretrain_forward(x, pop)
                    target = torch.clamp(x, 0, 2)
                    loss_mat = torch.nn.functional.cross_entropy(
                        logits.reshape(-1, 3),
                        target.reshape(-1),
                        reduction="none",
                    ).reshape(x.shape[0], x.shape[1], x.shape[2])
                    if win_mask is not None and win_mask.any():
                        loss = loss_mat[win_mask].mean()
                    else:
                        loss = loss_mat.mean()
                else:
                    pred = model(x, pop)
                    loss = (((pred - y) ** 2) * mask).sum() / mask.sum().clamp_min(1.0)
                    preds.append(pred.detach().cpu().numpy())
                    obs.append(y.detach().cpu().numpy())
                    masks.append(mask.detach().cpu().numpy())
                if train:
                    optimizer.zero_grad()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                    optimizer.step()
            total += float(loss.detach().cpu()) * len(x)
            n += len(x)
        metrics = {"loss": total / max(n, 1)}
        if args.mode != "pretrain" and preds:
            pred = np.concatenate(preds, axis=0)
            y = np.concatenate(obs, axis=0)
            m = np.concatenate(masks, axis=0).astype(bool)
            trait_r = []
            trait_r2 = []
            for j in range(y.shape[1]):
                keep = m[:, j]
                if keep.sum() >= 5:
                    trait_r.append(pearsonr_np(y[keep, j], pred[keep, j]))
                    trait_r2.append(r2_np(y[keep, j], pred[keep, j]))
            metrics["median_pearson"] = float(np.nanmedian(trait_r))
            metrics["median_r2"] = float(np.nanmedian(trait_r2))
        return metrics

    for epoch in range(1, args.epochs + 1):
        train_metrics = run_epoch(loaders["train"], True)
        val_metrics = run_epoch(loaders["val"], False)
        row = {"epoch": epoch, **{f"train_{k}": v for k, v in train_metrics.items()}, **{f"val_{k}": v for k, v in val_metrics.items()}}
        history.append(row)
        score = val_metrics["loss"]
        if score < best_val:
            best_val = score
            stale = 0
            torch.save({"model": model.state_dict(), "args": vars(args), "epoch": epoch}, out_dir / "best.pt")
        else:
            stale += 1
        print(json.dumps(row), flush=True)
        if stale >= args.patience:
            break

    state = torch.load(out_dir / "best.pt", map_location=device)
    model.load_state_dict(state["model"])
    test_metrics = run_epoch(loaders["test"], False)
    (out_dir / "history.json").write_text(json.dumps(history, indent=2) + "\n")
    (out_dir / "test_metrics.json").write_text(json.dumps(test_metrics, indent=2) + "\n")
    print("TEST", json.dumps(test_metrics, indent=2), flush=True)


if __name__ == "__main__":
    main()
