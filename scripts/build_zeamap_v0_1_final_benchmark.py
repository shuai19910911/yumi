#!/usr/bin/env python3
"""Build final ZEAMAP v0.1 benchmark summary tables from completed runs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


RESULTS = Path("results/v0_1_baseline")
REPORT = Path("docs/2026-06-05-zeamap-v0-1-final-benchmark.md")


def read_tsv(name: str) -> pd.DataFrame:
    return pd.read_csv(RESULTS / name, sep="\t")


def main() -> None:
    robust = read_tsv("robust_selected_traits.tsv")
    light_trait = read_tsv("lightweight_trait_summary.tsv")
    light_model = read_tsv("lightweight_model_summary.tsv")
    meth_pca = read_tsv("gene_methylation_pca_trait_summary.tsv")
    sparse = read_tsv("sparse_methylation_selection_trait_summary.tsv")

    final_traits = robust.merge(light_trait, on=["trait", "trait_family", "priority_tier"], how="left")
    final_traits = final_traits.merge(
        meth_pca[
            [
                "trait",
                "median_pearson_gain",
                "median_r2_gain",
                "gene_methylation_better_pearson_seeds",
                "gene_methylation_better_r2_seeds",
            ]
        ].rename(
            columns={
                "median_pearson_gain": "methylation_pca_median_pearson_gain",
                "median_r2_gain": "methylation_pca_median_r2_gain",
                "gene_methylation_better_pearson_seeds": "methylation_pca_better_pearson_seeds",
                "gene_methylation_better_r2_seeds": "methylation_pca_better_r2_seeds",
            }
        ),
        on="trait",
        how="left",
    )
    final_traits = final_traits.merge(
        sparse[
            [
                "trait",
                "median_pearson_gain_sparse_vs_base",
                "median_r2_gain_sparse_vs_base",
                "median_pearson_gain_sparse_vs_pca",
                "median_r2_gain_sparse_vs_pca",
            ]
        ],
        on="trait",
        how="left",
    )

    final_traits["main_model"] = "genotype_population_ridge"
    final_traits["methylation_role"] = "not_tested"
    has_meth = final_traits["methylation_pca_median_pearson_gain"].notna()
    final_traits.loc[has_meth, "methylation_role"] = "auxiliary_pca_ablation"
    sparse_bad = final_traits["median_pearson_gain_sparse_vs_pca"].notna() & (final_traits["median_pearson_gain_sparse_vs_pca"] <= 0)
    final_traits.loc[sparse_bad, "methylation_role"] = "auxiliary_pca_only_sparse_rejected"

    final_traits = final_traits.sort_values(
        ["ridge_median_pearson", "ridge_median_r2", "trait"],
        ascending=[False, False, True],
    )

    family_summary = (
        final_traits.groupby("trait_family")
        .agg(
            traits=("trait", "nunique"),
            high_priority=("priority_tier", lambda x: int((x == "high").sum())),
            medium_priority=("priority_tier", lambda x: int((x == "medium").sum())),
            watch_priority=("priority_tier", lambda x: int((x == "watch").sum())),
            median_ridge_pearson=("ridge_median_pearson", "median"),
            median_ridge_r2=("ridge_median_r2", "median"),
            median_elasticnet_pearson=("elasticnet_median_pearson", "median"),
            median_mlp_pearson=("mlp_median_pearson", "median"),
        )
        .reset_index()
        .sort_values(["median_ridge_pearson", "traits"], ascending=False)
    )

    final_traits.to_csv(RESULTS / "final_v0_1_trait_benchmark.tsv", sep="\t", index=False)
    family_summary.to_csv(RESULTS / "final_v0_1_family_summary.tsv", sep="\t", index=False)

    best_model = light_model.sort_values(["median_pearson", "median_r2"], ascending=False).iloc[0]
    top_traits = final_traits.head(15)[
        ["trait", "trait_family", "priority_tier", "ridge_median_pearson", "ridge_median_r2", "best_model_by_pearson"]
    ]
    report = f"""# ZEAMAP v0.1 final benchmark

日期：2026-06-05

## Scope

- Dataset: v0.1 processed ZEAMAP accession-level dataset
- Main paired samples: 461 accessions
- Main evaluation traits: 66 robust selected traits
- Main model: `genotype_population_ridge`
- Auxiliary analyses: ElasticNet, small MLP, methylation global summary, methylation PCA, sparse methylation selection

## Final Model Choice

```text
{light_model.to_string(index=False)}
```

Best overall model by median Pearson/R2:

```text
model: {best_model['model']}
median Pearson: {best_model['median_pearson']:.3f}
median R2: {best_model['median_r2']:.3f}
positive R2 fraction: {best_model['positive_r2_fraction']:.3f}
```

## Trait Family Summary

```text
{family_summary.to_string(index=False)}
```

## Top 15 Main-Model Traits

```text
{top_traits.to_string(index=False)}
```

## Epigenome Decision

- Global methylation summary did not materially improve performance.
- Gene/promoter/cis-window methylation PCA gave a small R2 gain on the methylation-covered subset.
- Sparse raw gene-window methylation underperformed both methylation PCA and genotype+population baseline.
- Therefore methylation remains an auxiliary ablation/interpretation modality in v0.1, not a default main model input.

## Outputs

- `results/v0_1_baseline/final_v0_1_trait_benchmark.tsv`
- `results/v0_1_baseline/final_v0_1_family_summary.tsv`
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
