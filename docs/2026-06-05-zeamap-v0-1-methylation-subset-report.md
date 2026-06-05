# ZEAMAP v0.1 methylation subset experiment

日期：2026-06-05

## Setup

- Methylation source: DNA methylation `01_regions` bedgraph files
- Contexts: mCG, mCHG, mCHH
- Features per accession: region count, mean, median, length-weighted mean, zero fraction, high fraction, total bp
- Methylation-covered accessions in feature table: 236
- Methylation-covered v0.1 accessions used: 236
- Traits: 66 robust selected traits
- Seeds: 20260605, 20260606, 20260607, 20260608, 20260609

## Model Summary

```text
                                model  seeds  traits_evaluated  median_r2  mean_r2  median_pearson  mean_pearson  positive_r2_fraction
genotype_population_methylation_ridge      5                66   0.172969 0.195455        0.495797      0.477902              0.848485
            genotype_population_ridge      5                66   0.172664 0.195843        0.489870      0.479428              0.830303
```

## Top 10 Trait Gains From Methylation Summary

```text
                               trait  median_pearson_gain  mean_pearson_gain  median_r2_gain  mean_r2_gain  methylation_better_pearson_seeds  methylation_better_r2_seeds
   metabolite__Feruloyltryptamine_E1             0.114078           0.096245        0.069151      0.077445                                 5                            5
metabolite__N_Coumaroyltryptamine_E1             0.061075           0.074041        0.048115      0.046780                                 5                            5
              agri_aa_oil__Oil_C18_3             0.034227           0.040763        0.033273      0.049806                                 5                            5
          agri_aa_oil__Oil_C180_C200             0.026762           0.048370        0.008959      0.079679                                 3                            3
              agri_aa_oil__Earlength             0.021132           0.007163        0.010233      0.006195                                 3                            4
     agri_aa_oil__Kernernumberperrow             0.019991           0.011117        0.005718      0.006211                                 3                            3
    metabolite__Norcinnamolaurine_E2             0.019470           0.014883        0.005798      0.005930                                 4                            5
             agri_aa_oil__Oil_C22_0P             0.018479           0.008804        0.001944     -0.005095                                 4                            3
            agri_aa_oil__Plantheight             0.017330           0.005170       -0.008017     -0.007611                                 3                            2
              agri_aa_oil__Earheight             0.015096           0.007431        0.012903      0.002510                                 4                            3
```

## Interpretation

- This is a coarse accession-level methylation summary test, not a gene/promoter methylation model.
- If global methylation summaries do not improve over genotype+population, the next useful methylation step should be gene/promoter/cis-window aggregation, not larger models.

## Outputs

- `data/processed/v0_1/methylation_region_summary.tsv`
- `results/v0_1_baseline/methylation_subset_metrics.tsv`
- `results/v0_1_baseline/methylation_subset_model_summary.tsv`
- `results/v0_1_baseline/methylation_subset_trait_summary.tsv`
