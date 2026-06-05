# ZEAMAP v0.1 baseline benchmark report

Run date: 2026-06-05

## Inputs

- `data/processed/v0_1/genotype_dosage_int8.npz`
- `data/processed/v0_1/phenotype.tsv`
- `data/processed/v0_1/population.tsv`

## Environment

- mamba environment: `yumi`
- CPU job: Slurm `q07`, job `8438902`

## Split

- train: 322
- val: 69
- test: 70

## Genotype PCA

- requested PCs: 100
- output PCs: 100
- cumulative explained variance: 0.504527

## Trait filtering

- total traits: 318
- traits used for baseline: 317
- minimum total non-missing: 80
- minimum train non-missing: 30
- minimum val/test non-missing: 10

## Model comparison

```text
                        model  traits_evaluated  median_r2   mean_r2  median_pearson  mean_pearson  positive_r2_traits  pearson_gt_0_2_traits
genotype_pca_population_ridge               317   0.033692 -0.016162        0.331314      0.321527                 204                    226
           genotype_pca_ridge               317   0.020537 -0.017032        0.298415      0.293565                 180                    206
             population_ridge               317   0.004931 -0.096238        0.237233      0.229182                 172                    182
                mean_baseline               317  -0.014445 -0.079186             NaN           NaN                   0                      0
```

## Interpretation

- `genotype_pca_population_ridge` is the best overall baseline by test median Pearson.
- Genotype adds useful signal beyond population covariates: median Pearson improves from 0.237 for `population_ridge` to 0.331 for `genotype_pca_population_ridge`.
- 204 of 317 evaluated traits have positive test R2 under `genotype_pca_population_ridge`.
- The strongest predictable traits are mostly oil-related traits, with top test Pearson above 0.9.
- Mean R2 is still slightly negative because many traits are noisy or weakly predictable; downstream modeling should focus on the stable trait subset rather than all 318 traits.
- Trait subset selection was run after this benchmark; see `docs/2026-06-05-zeamap-v0-1-selected-traits.md`.

## Outputs

- `data/processed/v0_1/splits/split_assignments.tsv`
- `data/processed/v0_1/genotype_pca.tsv`
- `data/processed/v0_1/genotype_pca_variance.tsv`
- `results/v0_1_baseline/trait_qc.tsv`
- `results/v0_1_baseline/trait_metrics.tsv`
- `results/v0_1_baseline/model_comparison.tsv`
- `results/v0_1_baseline/top_predictable_traits.tsv`

## Notes

- All results use accession-level splits.
- `mean_baseline` predicts the training mean for each trait.
- Ridge models standardize features inside the training fold.
- Ridge alpha is selected with `RidgeCV(cv=None)` for a fast deterministic CPU baseline.
- Expression is not used because current expression files are reference/tissue matrices rather than AMP accession-level expression.
