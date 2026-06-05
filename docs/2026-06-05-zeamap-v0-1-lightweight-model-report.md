# ZEAMAP v0.1 lightweight model comparison

日期：2026-06-05

## Setup

- Input traits: 66 robust selected traits
- Seeds: 20260605, 20260606, 20260607, 20260608, 20260609
- Models: population ridge, genotype+population ridge, genotype+population ElasticNet, genotype+population small MLP
- Feature input: fixed `genotype_pca.tsv` plus population covariates

## Model Summary

```text
                         model  seeds  traits_evaluated  median_r2   mean_r2  median_pearson  mean_pearson  positive_r2_fraction  pearson_gt_0_3_fraction
     genotype_population_ridge      5                66   0.203811  0.263065        0.497904      0.519866              0.978788                 0.951515
genotype_population_elasticnet      5                66   0.170526  0.231809        0.482682      0.500602              0.930303                 0.842424
 genotype_population_small_mlp      5                66  -0.190655 -0.219977        0.351305      0.369436              0.303030                 0.603030
              population_ridge      5                66   0.085142  0.100831        0.332147      0.336523              0.818182                 0.603030
```

## Best Model Counts

```text
     model  traits
     ridge      43
elasticnet      23
```

## Top 10 Traits By Ridge Pearson

```text
                     trait  ridge_median_pearson  elasticnet_median_pearson  mlp_median_pearson  ridge_median_r2  elasticnet_median_r2  mlp_median_r2 trait_family priority_tier best_model_by_pearson
      agri_aa_oil__Oil_OIL              0.924294                   0.928733            0.838860         0.823807              0.832705       0.659669          oil          high            elasticnet
    agri_aa_oil__Oil_C18_1              0.877590                   0.884698            0.733648         0.767657              0.743425       0.446381          oil          high            elasticnet
    agri_aa_oil__Oil_C18_2              0.869161                   0.895069            0.800043         0.737586              0.790913       0.578251          oil          high            elasticnet
    agri_aa_oil__Oil_C20_1              0.837581                   0.843227            0.698717         0.700775              0.682800       0.294478          oil          high            elasticnet
    agri_aa_oil__Oil_C20_0              0.826603                   0.845155            0.741680         0.679208              0.676426       0.466706          oil          high            elasticnet
    agri_aa_oil__Oil_C18_0              0.813682                   0.836506            0.749474         0.661115              0.633299       0.494841          oil          high            elasticnet
    agri_aa_oil__Oil_C16_0              0.781459                   0.811327            0.746468         0.587562              0.608421       0.465370          oil          high            elasticnet
agri_aa_oil__Oil_C200_C220              0.743427                   0.698890            0.614849         0.528411              0.457549       0.196348          oil          high                 ridge
 agri_aa_oil__kernellength              0.738321                   0.724359            0.539703         0.509565              0.489577       0.136977    agronomic          high                 ridge
agri_aa_oil__Oil_C182_C183              0.736620                   0.693282            0.605016         0.520524              0.409389       0.227774          oil          high                 ridge
```

## Interpretation

- This comparison tests whether a non-linear small MLP or sparse ElasticNet improves over the ridge baseline.
- If ridge remains competitive, the next stage should prioritize feature engineering or methylation subset features rather than larger models.

## Outputs

- `results/v0_1_baseline/lightweight_model_metrics.tsv`
- `results/v0_1_baseline/lightweight_model_summary.tsv`
- `results/v0_1_baseline/lightweight_trait_summary.tsv`
