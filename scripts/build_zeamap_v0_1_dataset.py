#!/usr/bin/env python3
"""Build ZEAMAP v0.1 processed dataset.

Outputs are written locally under data/processed/v0_1 and intentionally ignored
by git. The repository tracks this script and the dataset manifest/report only.
"""

from __future__ import annotations

import json
import math
import re
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd


LOCAL_ROOT = Path("/home/user/zhangzhishuai/data/plantDB/maize_ZEAMAP")
PROJECT_ROOT = Path(".")
METADATA = PROJECT_ROOT / "data/metadata"
OUT = PROJECT_ROOT / "data/processed/v0_1"
REPORT = PROJECT_ROOT / "docs/2026-06-04-zeamap-v0-1-build-report.md"
BCFTOOLS = Path("/home/user/zhangzhishuai/.local/share/mamba/envs/bio3/bin/bcftools")
VCF = LOCAL_ROOT / "variation/AMP_SNP_anno.vcf.gz"

MAX_GENOTYPE_VARIANTS = 200_000
MIN_INFO_MAF = 0.05
MIN_INFO_NS = 450


def norm_id(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0") and re.fullmatch(r"\d+\.0", text):
        text = text[:-2]
    return re.sub(r"\s+", "", text).upper()


def clean_trait_name(prefix: str, col: str) -> str:
    col = str(col).lstrip("#")
    col = re.sub(r"[^0-9A-Za-z_]+", "_", col)
    col = re.sub(r"_+", "_", col).strip("_")
    return f"{prefix}__{col}"


def read_population(strong_ids: list[str]) -> pd.DataFrame:
    pca = pd.read_csv(LOCAL_ROOT / "population/amp_pca.txt", sep="\t", dtype=str)
    struct = pd.read_csv(LOCAL_ROOT / "population/amp_str.txt", sep="\t", dtype=str)
    pca["accession_id_norm"] = pca["sample"].map(norm_id)
    struct["accession_id_norm"] = struct["Sample"].map(norm_id)

    pca = pca.rename(columns={"sample": "population_pca_sample", "POP": "population_group"})
    struct = struct.rename(columns={"Sample": "population_structure_sample", "Group": "structure_group"})
    merged = pca.merge(struct, on="accession_id_norm", how="outer")
    merged = merged[merged["accession_id_norm"].isin(strong_ids)].copy()

    for col in ["PC1", "PC2", "PC3", "K1", "K2", "K3"]:
        if col in merged.columns:
            merged[col] = pd.to_numeric(merged[col], errors="coerce")
    return merged.set_index("accession_id_norm").loc[strong_ids].reset_index()


def read_phenotype_table(path: Path, prefix: str, strong_ids: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(path, sep="\t", dtype=str)
    id_col = "sample_id_norm" if "sample_id_norm" in df.columns else "stock_name_norm"
    df["accession_id_norm"] = df[id_col].map(norm_id)
    trait_cols = [c for c in df.columns if str(c).startswith("#")]

    data = df[["accession_id_norm"] + trait_cols].copy()
    rename = {c: clean_trait_name(prefix, c) for c in trait_cols}
    data = data.rename(columns=rename)
    for col in rename.values():
        data[col] = pd.to_numeric(data[col], errors="coerce")
    data = data.drop_duplicates("accession_id_norm").set_index("accession_id_norm")
    data = data.reindex(strong_ids).reset_index()

    descriptor_path = path.with_name(path.name.replace("phenotype", "descriptor"))
    desc = pd.read_csv(descriptor_path, sep="\t", dtype=str)
    desc = desc.rename(columns={"*descriptor_name": "descriptor_name"})
    desc["processed_trait_name"] = desc["descriptor_name"].map(lambda x: clean_trait_name(prefix, f"#{x}"))
    desc["source_prefix"] = prefix
    return data, desc


def build_phenotypes(strong_ids: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    met, met_desc = read_phenotype_table(METADATA / "phenotype_sheets/metabolite_phenotype.tsv", "metabolite", strong_ids)
    agri, agri_desc = read_phenotype_table(METADATA / "phenotype_sheets/agri_aa_oil_phenotype.tsv", "agri_aa_oil", strong_ids)
    merged = met.merge(agri, on="accession_id_norm", how="outer")
    merged = merged.set_index("accession_id_norm").loc[strong_ids].reset_index()
    desc = pd.concat([met_desc, agri_desc], ignore_index=True)
    return merged, desc


def get_subset_sample_order(sample_file: Path) -> list[str]:
    proc = subprocess.run(
        [str(BCFTOOLS), "view", "-S", str(sample_file), "-h", str(VCF)],
        text=True,
        capture_output=True,
        check=True,
    )
    for line in proc.stdout.splitlines():
        if line.startswith("#CHROM"):
            return [norm_id(x) for x in line.split("\t")[9:]]
    raise RuntimeError("Could not find VCF #CHROM header line")


def count_filtered_variants(sample_file: Path) -> int:
    cmd = [
        str(BCFTOOLS),
        "view",
        "-S",
        str(sample_file),
        "-m2",
        "-M2",
        "-v",
        "snps",
        "-i",
        f"MAF>={MIN_INFO_MAF} && NS>={MIN_INFO_NS}",
        "-H",
        str(VCF),
    ]
    proc = subprocess.Popen(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    count = 0
    assert proc.stdout is not None
    for _ in proc.stdout:
        count += 1
    _, stderr = proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"bcftools variant count failed: {stderr}")
    return count


def dosage(gt: str) -> int:
    gt = gt.split(":", 1)[0]
    if "." in gt:
        return -1
    alleles = re.split(r"[|/]", gt)
    value = 0
    for allele in alleles:
        if allele == ".":
            return -1
        value += int(allele)
    return value


def build_genotype_matrix(strong_ids: list[str]) -> dict[str, object]:
    sample_file = OUT / "genotype_samples.txt"
    sample_file.write_text("\n".join(strong_ids) + "\n", encoding="utf-8")
    sample_order = get_subset_sample_order(sample_file)
    if set(sample_order) != set(strong_ids):
        missing = sorted(set(strong_ids) - set(sample_order))
        raise RuntimeError(f"VCF sample subset does not match strong_ids; missing={missing[:10]}")

    filtered_count = count_filtered_variants(sample_file)
    stride = max(1, math.ceil(filtered_count / MAX_GENOTYPE_VARIANTS))

    view_cmd = [
        str(BCFTOOLS),
        "view",
        "-S",
        str(sample_file),
        "-m2",
        "-M2",
        "-v",
        "snps",
        "-i",
        f"MAF>={MIN_INFO_MAF} && NS>={MIN_INFO_NS}",
        "-Ou",
        str(VCF),
    ]
    query_cmd = [
        str(BCFTOOLS),
        "query",
        "-f",
        "%CHROM\t%POS\t%ID\t%REF\t%ALT\t%INFO/MAF\t%INFO/NS[\t%GT]\n",
        "-",
    ]
    view = subprocess.Popen(view_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    query = subprocess.Popen(query_cmd, stdin=view.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert view.stdout is not None
    view.stdout.close()
    assert query.stdout is not None

    variant_rows: list[dict[str, object]] = []
    dosage_rows: list[np.ndarray] = []
    seen = 0
    kept = 0
    for line in query.stdout:
        seen += 1
        if (seen - 1) % stride != 0:
            continue
        parts = line.rstrip("\n").split("\t")
        meta = parts[:7]
        gts = parts[7:]
        if len(gts) != len(sample_order):
            raise RuntimeError(f"GT field count mismatch at variant {meta[:3]}")
        variant_rows.append(
            {
                "variant_index": kept,
                "chrom": meta[0],
                "pos": int(meta[1]),
                "variant_id": meta[2],
                "ref": meta[3],
                "alt": meta[4],
                "info_maf": float(meta[5]) if meta[5] not in {".", ""} else np.nan,
                "info_ns": int(float(meta[6])) if meta[6] not in {".", ""} else np.nan,
            }
        )
        dosage_rows.append(np.fromiter((dosage(gt) for gt in gts), dtype=np.int8, count=len(gts)))
        kept += 1
        if kept >= MAX_GENOTYPE_VARIANTS:
            break

    query_stdout, query_stderr = query.communicate()
    view_stderr = view.stderr.read().decode() if view.stderr is not None else ""
    view.wait()
    if query.returncode not in (0, None):
        raise RuntimeError(f"bcftools query failed: {query_stderr}")
    if view.returncode not in (0, None):
        raise RuntimeError(f"bcftools view failed: {view_stderr}")

    matrix = np.vstack(dosage_rows)
    variants = pd.DataFrame(variant_rows)
    variants.to_csv(OUT / "genotype_variants.tsv", sep="\t", index=False)
    pd.DataFrame({"sample_index": range(len(sample_order)), "accession_id_norm": sample_order}).to_csv(
        OUT / "genotype_samples.tsv", sep="\t", index=False
    )
    np.savez_compressed(
        OUT / "genotype_dosage_int8.npz",
        dosage=matrix,
        samples=np.array(sample_order, dtype=object),
        variant_id=variants["variant_id"].astype(str).to_numpy(),
    )
    return {
        "filtered_variant_count": filtered_count,
        "stride": stride,
        "kept_variant_count": kept,
        "sample_count": len(sample_order),
        "matrix_shape": list(matrix.shape),
        "missing_genotype_count": int((matrix < 0).sum()),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    overlap = pd.read_csv(METADATA / "zeamap_second_batch_sample_overlap.tsv", sep="\t")
    strong = overlap[overlap["strong_pair_genotype_population_phenotype"]].copy()
    strong_ids = sorted(strong["accession_id_norm"].map(norm_id).tolist())

    accessions = strong[strong["accession_id_norm"].map(norm_id).isin(strong_ids)].copy()
    accessions["accession_id_norm"] = accessions["accession_id_norm"].map(norm_id)
    accessions = accessions.drop_duplicates("accession_id_norm").set_index("accession_id_norm").loc[strong_ids].reset_index()
    accessions.to_csv(OUT / "accessions.tsv", sep="\t", index=False)

    modality_mask_cols = [
        "accession_id_norm",
        "in_vcf",
        "has_population",
        "has_metabolite",
        "has_agri_aa_oil",
        "strong_pair_population_phenotype",
        "strong_pair_genotype_population_phenotype",
        "has_mCG_regions",
        "has_mCHG_regions",
        "has_mCHH_regions",
        "has_methylC_sites",
        "has_any_methylation",
        "strong_pair_genotype_population_phenotype_methylation",
    ]
    accessions[modality_mask_cols].to_csv(OUT / "modality_mask.tsv", sep="\t", index=False)

    population = read_population(strong_ids)
    phenotype, trait_desc = build_phenotypes(strong_ids)
    population.to_csv(OUT / "population.tsv", sep="\t", index=False)
    phenotype.to_csv(OUT / "phenotype.tsv", sep="\t", index=False)
    trait_desc.to_csv(OUT / "phenotype_trait_descriptors.tsv", sep="\t", index=False)

    # Parquet copies are useful for model code; TSV remains the transparent exchange format.
    population.to_parquet(OUT / "population.parquet", index=False)
    phenotype.to_parquet(OUT / "phenotype.parquet", index=False)

    genotype_stats = build_genotype_matrix(strong_ids)

    manifest_rows = []
    for p in sorted(OUT.glob("*")):
        if p.is_file():
            manifest_rows.append({"file": str(p), "size_bytes": p.stat().st_size})
    manifest = pd.DataFrame(manifest_rows)
    manifest.to_csv(OUT / "manifest.tsv", sep="\t", index=False)

    numeric_trait_cols = [c for c in phenotype.columns if c != "accession_id_norm"]
    met_cols = [c for c in numeric_trait_cols if c.startswith("metabolite__")]
    agri_cols = [c for c in numeric_trait_cols if c.startswith("agri_aa_oil__")]
    report = f"""# ZEAMAP v0.1 processed dataset build report

构建日期：2026-06-04

## 输入

- 第一批 phenotype/population metadata
- 第二批 `AMP_SNP_anno.vcf.gz`
- 第二批 methylation coverage metadata

## 输出目录

```text
{OUT}
```

## 样本

- v0.1 accession 数：{len(strong_ids)}
- 选择标准：`genotype + population + 任一 phenotype/metabolome`
- 带任一 DNA methylation 的 v0.1 accession 数：{int(accessions["has_any_methylation"].sum())}

## phenotype/population

- population rows：{len(population)}
- phenotype rows：{len(phenotype)}
- metabolite trait columns：{len(met_cols)}
- agri/AA/Oil trait columns：{len(agri_cols)}
- total phenotype trait columns：{len(numeric_trait_cols)}

## genotype

- VCF filter：biallelic SNP, `MAF >= {MIN_INFO_MAF}`, `NS >= {MIN_INFO_NS}`
- filtered variants before thinning：{genotype_stats["filtered_variant_count"]}
- thinning stride：{genotype_stats["stride"]}
- kept variants：{genotype_stats["kept_variant_count"]}
- genotype samples：{genotype_stats["sample_count"]}
- dosage matrix shape：{genotype_stats["matrix_shape"]}
- missing genotype entries encoded as `-1`：{genotype_stats["missing_genotype_count"]}
- dosage encoding：`0`, `1`, `2` ALT allele dosage; `-1` missing

## files

- `accessions.tsv`
- `modality_mask.tsv`
- `population.tsv`
- `population.parquet`
- `phenotype.tsv`
- `phenotype.parquet`
- `phenotype_trait_descriptors.tsv`
- `genotype_samples.tsv`
- `genotype_variants.tsv`
- `genotype_dosage_int8.npz`
- `manifest.tsv`

## validation

- `genotype_dosage_int8.npz` sample order is stored in `genotype_samples.tsv`.
- `genotype_dosage_int8.npz` variant rows correspond to `genotype_variants.tsv`.
- Matrix orientation is `[variants, samples]`.

## Notes

- `data/processed/` is ignored by git because it contains local training matrices.
- Expression files from the first batch remain reference/tissue expression priors, not accession-level paired expression.
- Chromatin accessibility and interaction are not included as paired accession-level v0.1 modalities.
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
