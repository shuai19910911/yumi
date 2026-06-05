#!/usr/bin/env python3
"""Select stable ZEAMAP v0.1 traits from baseline benchmark results."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


RESULTS = Path("results/v0_1_baseline")
DOC = Path("docs/2026-06-05-zeamap-v0-1-selected-traits.md")

MIN_PEARSON = 0.30
MIN_R2 = 0.0
MIN_PEARSON_GAIN = 0.02
MIN_R2_GAIN = 0.0


def trait_family(trait: str) -> str:
    if trait.startswith("agri_aa_oil__Oil_"):
        return "oil"
    if trait.startswith("agri_aa_oil__AA_"):
        return "amino_acid"
    if trait.startswith("agri_aa_oil__"):
        return "agronomic"
    if trait.startswith("metabolite__"):
        return "metabolite"
    return "other"


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    top = pd.read_csv(RESULTS / "top_predictable_traits.tsv", sep="\t")
    qc = pd.read_csv(RESULTS / "trait_qc.tsv", sep="\t")

    merged = top.merge(qc, on=["trait", "trait_group"], how="left")
    gp_pearson = "pearson__genotype_pca_population_ridge"
    g_pearson = "pearson__genotype_pca_ridge"
    p_pearson = "pearson__population_ridge"
    gp_r2 = "r2__genotype_pca_population_ridge"
    g_r2 = "r2__genotype_pca_ridge"
    p_r2 = "r2__population_ridge"

    for col in [gp_pearson, g_pearson, p_pearson, gp_r2, g_r2, p_r2]:
        merged[col] = pd.to_numeric(merged[col], errors="coerce")

    merged["trait_family"] = merged["trait"].map(trait_family)
    merged["pearson_gain_vs_population"] = merged[gp_pearson] - merged[p_pearson]
    merged["r2_gain_vs_population"] = merged[gp_r2] - merged[p_r2]
    merged["pearson_gain_vs_genotype_only"] = merged[gp_pearson] - merged[g_pearson]
    merged["r2_gain_vs_genotype_only"] = merged[gp_r2] - merged[g_r2]

    selected = merged[
        (merged[gp_pearson] >= MIN_PEARSON)
        & (merged[gp_r2] > MIN_R2)
        & (
            (merged["pearson_gain_vs_population"] >= MIN_PEARSON_GAIN)
            | (merged["r2_gain_vs_population"] > MIN_R2_GAIN)
        )
        & (merged["used_for_baseline"].astype(bool))
    ].copy()
    selected = selected.sort_values([gp_pearson, gp_r2], ascending=False)

    priority = selected.copy()
    priority["priority_tier"] = np.select(
        [
            (priority[gp_pearson] >= 0.70) & (priority[gp_r2] >= 0.45),
            (priority[gp_pearson] >= 0.50) & (priority[gp_r2] >= 0.20),
        ],
        ["high", "medium"],
        default="watch",
    )

    family_summary = (
        selected.groupby("trait_family", dropna=False)
        .agg(
            selected_traits=("trait", "count"),
            median_pearson=(gp_pearson, "median"),
            max_pearson=(gp_pearson, "max"),
            median_r2=(gp_r2, "median"),
            max_r2=(gp_r2, "max"),
            median_pearson_gain_vs_population=("pearson_gain_vs_population", "median"),
        )
        .reset_index()
        .sort_values(["selected_traits", "median_pearson"], ascending=False)
    )
    tier_summary = (
        priority.groupby(["trait_family", "priority_tier"], dropna=False)
        .size()
        .reset_index(name="traits")
        .sort_values(["trait_family", "priority_tier"])
    )

    selected.to_csv(RESULTS / "selected_traits.tsv", sep="\t", index=False)
    family_summary.to_csv(RESULTS / "selected_trait_family_summary.tsv", sep="\t", index=False)
    tier_summary.to_csv(RESULTS / "selected_trait_tier_summary.tsv", sep="\t", index=False)

    top10_cols = [
        "trait",
        "trait_family",
        gp_pearson,
        gp_r2,
        p_pearson,
        p_r2,
        "pearson_gain_vs_population",
        "r2_gain_vs_population",
        "total_non_missing",
        "test_non_missing",
    ]
    top10 = selected[top10_cols].head(10)

    report = f"""# ZEAMAP v0.1 selected traits

日期：2026-06-05

## Selection rule

从 `results/v0_1_baseline/top_predictable_traits.tsv` 和 `trait_qc.tsv` 中筛选：

- `genotype_pca_population_ridge` test Pearson >= {MIN_PEARSON}
- `genotype_pca_population_ridge` test R2 > {MIN_R2}
- 相比 `population_ridge` 至少满足 Pearson gain >= {MIN_PEARSON_GAIN} 或 R2 gain > {MIN_R2_GAIN}
- trait 通过 baseline QC

## Result

- baseline evaluated traits：{len(merged)}
- selected traits：{len(selected)}
- high-priority traits：{int((priority["priority_tier"] == "high").sum())}
- medium-priority traits：{int((priority["priority_tier"] == "medium").sum())}
- watch traits：{int((priority["priority_tier"] == "watch").sum())}

## Family summary

```text
{family_summary.to_string(index=False)}
```

## Top 10 selected traits

```text
{top10.to_string(index=False)}
```

## Interpretation

- 第一版 selected traits 主要由 oil、agronomic、metabolite 和 amino acid traits 构成。
- Oil traits 的最高 Pearson 和 R2 最强，适合作为下一阶段模型 sanity-check 和主评估集合。
- Metabolite traits 数量较多，但整体信号弱于 oil traits，后续需要 multi-seed robustness 再确认。
- 这些 selected traits 应作为阶段 3.2 多随机种子稳健性验证的输入，不建议直接把全部 318 个 trait 都作为后续主目标。

## Outputs

- `results/v0_1_baseline/selected_traits.tsv`
- `results/v0_1_baseline/selected_trait_family_summary.tsv`
- `results/v0_1_baseline/selected_trait_tier_summary.tsv`
"""
    DOC.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
