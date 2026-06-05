# ZEAMAP v0.1 multi-seed robustness report

日期：2026-06-05

## Setup

- Seeds: 20260605, 20260606, 20260607, 20260608, 20260609
- Traits tested: 130
- Models: mean, population ridge, genotype PCA ridge, genotype PCA + population ridge
- Genotype PCA is fixed from `data/processed/v0_1/genotype_pca.tsv`; this checks split robustness, not PCA refitting robustness.

## Model Summary

```text
                        model  seeds  traits_evaluated  median_r2   mean_r2  median_pearson  mean_pearson  positive_r2_fraction  pearson_gt_0_3_fraction
genotype_pca_population_ridge      5               130   0.109433  0.128821        0.395783      0.392578              0.801538                 0.703077
           genotype_pca_ridge      5               130   0.091962  0.111409        0.372115      0.367670              0.750769                 0.643077
             population_ridge      5               130   0.032790  0.036574        0.273840      0.266252              0.655385                 0.438462
                mean_baseline      5               130  -0.012576 -0.033159             NaN           NaN              0.000000                 0.000000
```

## Robust Trait Rule

For `genotype_pca_population_ridge`:

- evaluated in all 5 seeds
- median Pearson >= 0.3
- median R2 > 0
- positive R2 in at least 4 seeds
- Pearson > 0.3 in at least 4 seeds

## Robust Traits

- robust selected traits: 66

```text
trait_family  robust_traits  median_pearson  median_r2
         oil             29        0.595848   0.321419
  metabolite             16        0.389434   0.115579
   agronomic             15        0.498393   0.189754
  amino_acid              6        0.367408   0.130633
```

## Top 10 Robust Traits

```text
                     trait trait_family priority_tier  median_pearson  min_pearson  median_r2   min_r2  positive_r2_seeds  pearson_gt_0_3_seeds
      agri_aa_oil__Oil_OIL          oil          high        0.924294     0.869360   0.823807 0.753515                  5                     5
    agri_aa_oil__Oil_C18_1          oil          high        0.877590     0.833315   0.767657 0.692427                  5                     5
    agri_aa_oil__Oil_C18_2          oil          high        0.869161     0.820311   0.737586 0.667331                  5                     5
    agri_aa_oil__Oil_C20_1          oil          high        0.837581     0.709459   0.700775 0.458110                  5                     5
    agri_aa_oil__Oil_C20_0          oil          high        0.826603     0.796109   0.679208 0.630101                  5                     5
    agri_aa_oil__Oil_C18_0          oil          high        0.813682     0.811749   0.661115 0.577828                  5                     5
    agri_aa_oil__Oil_C16_0          oil          high        0.781459     0.729487   0.587562 0.518162                  5                     5
agri_aa_oil__Oil_C200_C220          oil          high        0.743427     0.650738   0.528411 0.409750                  5                     5
 agri_aa_oil__kernellength    agronomic          high        0.738321     0.589030   0.509565 0.339344                  5                     5
agri_aa_oil__Oil_C182_C183          oil          high        0.736620     0.583446   0.520524 0.314854                  5                     5
```

## Interpretation

- Robust traits are the preferred target set for lightweight MLP, ElasticNet comparison, and later methylation subset experiments.
- Traits that passed single-split selection but failed robustness should remain watch-list traits, not primary model targets.

## Outputs

- `results/v0_1_baseline/robustness_metrics.tsv`
- `results/v0_1_baseline/robustness_model_summary.tsv`
- `results/v0_1_baseline/robustness_trait_summary.tsv`
- `results/v0_1_baseline/robust_selected_traits.tsv`
