# ZEAMAP v0.1 final benchmark

日期：2026-06-05

## Scope

- Dataset: v0.1 processed ZEAMAP accession-level dataset
- Main paired samples: 461 accessions
- Main evaluation traits: 66 robust selected traits
- Main model: `genotype_population_ridge`
- Auxiliary analyses: ElasticNet, small MLP, methylation global summary, methylation PCA, sparse methylation selection

## Final Model Choice

```text
                         model  seeds  traits_evaluated  median_r2   mean_r2  median_pearson  mean_pearson  positive_r2_fraction  pearson_gt_0_3_fraction
     genotype_population_ridge      5                66   0.203811  0.263065        0.497904      0.519866              0.978788                 0.951515
genotype_population_elasticnet      5                66   0.170526  0.231809        0.482682      0.500602              0.930303                 0.842424
 genotype_population_small_mlp      5                66  -0.190655 -0.219977        0.351305      0.369436              0.303030                 0.603030
              population_ridge      5                66   0.085142  0.100831        0.332147      0.336523              0.818182                 0.603030
```

Best overall model by median Pearson/R2:

```text
model: genotype_population_ridge
median Pearson: 0.498
median R2: 0.204
positive R2 fraction: 0.979
```

## Trait Family Summary

```text
trait_family  traits  high_priority  medium_priority  watch_priority  median_ridge_pearson  median_ridge_r2  median_elasticnet_pearson  median_mlp_pearson
         oil      29             10               13               6              0.595848         0.321419                   0.538792            0.451685
   agronomic      15              1                5               9              0.498393         0.189754                   0.494625            0.372918
  metabolite      16              0                3              13              0.389434         0.115579                   0.346989            0.205543
  amino_acid       6              0                1               5              0.367408         0.130633                   0.365020            0.211428
```

## Top 15 Main-Model Traits

```text
                     trait trait_family priority_tier  ridge_median_pearson  ridge_median_r2 best_model_by_pearson
      agri_aa_oil__Oil_OIL          oil          high              0.924294         0.823807            elasticnet
    agri_aa_oil__Oil_C18_1          oil          high              0.877590         0.767657            elasticnet
    agri_aa_oil__Oil_C18_2          oil          high              0.869161         0.737586            elasticnet
    agri_aa_oil__Oil_C20_1          oil          high              0.837581         0.700775            elasticnet
    agri_aa_oil__Oil_C20_0          oil          high              0.826603         0.679208            elasticnet
    agri_aa_oil__Oil_C18_0          oil          high              0.813682         0.661115            elasticnet
    agri_aa_oil__Oil_C16_0          oil          high              0.781459         0.587562            elasticnet
agri_aa_oil__Oil_C200_C220          oil          high              0.743427         0.528411                 ridge
 agri_aa_oil__kernellength    agronomic          high              0.738321         0.509565                 ridge
agri_aa_oil__Oil_C182_C183          oil          high              0.736620         0.520524                 ridge
   agri_aa_oil__Oil_C18_3P          oil        medium              0.672869         0.442733                 ridge
    agri_aa_oil__Oil_C16_1          oil          high              0.671396         0.427597            elasticnet
  agri_aa_oil__Headingdate    agronomic        medium              0.627570         0.385799                 ridge
    agri_aa_oil__Oil_C22_0          oil        medium              0.619722         0.365109                 ridge
   agri_aa_oil__Oil_C24_0P          oil        medium              0.605171         0.321419                 ridge
```

## Epigenome Decision

- Global methylation summary did not materially improve performance.
- Gene/promoter/cis-window methylation PCA gave a small R2 gain on the methylation-covered subset.
- Sparse raw gene-window methylation underperformed both methylation PCA and genotype+population baseline.
- Therefore methylation remains an auxiliary ablation/interpretation modality in v0.1, not a default main model input.

## Outputs

- `results/v0_1_baseline/final_v0_1_trait_benchmark.tsv`
- `results/v0_1_baseline/final_v0_1_family_summary.tsv`
