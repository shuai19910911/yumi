# ZEAMAP v0.1 gene methylation PCA experiment

日期：2026-06-05

## Setup

- Annotation: Ensembl Plants release 47 `Zea_mays.B73_RefGen_v4.47.chr.gff3.gz`
- Genes: 39005
- Region types: gene body, promoter upstream 2000 bp, cis-window +/- 10000 bp
- Methylation contexts: mCG, mCHG, mCHH
- Methylation-covered accessions: 236
- PCA features: 90
- Seeds: 20260605, 20260606, 20260607, 20260608, 20260609
- Traits: 66 robust selected traits

## Model Summary

```text
                                         model  seeds  traits_evaluated  median_r2  mean_r2  median_pearson  mean_pearson  positive_r2_fraction
genotype_population_gene_methylation_pca_ridge      5                66   0.198767 0.210253        0.496372      0.486469              0.818182
                     genotype_population_ridge      5                66   0.172664 0.195843        0.489870      0.479428              0.830303
```

## Top 10 Trait Gains From Gene Methylation PCA

```text
                            trait  median_pearson_gain  mean_pearson_gain  median_r2_gain  mean_r2_gain  gene_methylation_better_pearson_seeds  gene_methylation_better_r2_seeds
  agri_aa_oil__Kernernumberperrow             0.089802           0.073335        0.058809      0.041723                                      4                                 4
   metabolite__L_Glutamic_acid_E1             0.074778          -0.009254       -0.023248     -0.031680                                      3                                 1
          agri_aa_oil__Oil_C20_1P             0.069462           0.032214        0.029167      0.038901                                      3                                 4
 metabolite__Norcinnamolaurine_E1             0.068844           0.079143        0.031935      0.002226                                      5                                 4
           agri_aa_oil__Oil_C18_0             0.059052           0.050267        0.061106      0.063254                                      5                                 5
      agri_aa_oil__100grainweight             0.054570           0.057481        0.046522      0.035718                                      5                                 4
           metabolite__Pro_Leu_E1             0.053327           0.056490        0.073430      0.033307                                      3                                 3
         agri_aa_oil__Plantheight             0.049854           0.026561        0.046223      0.035943                                      4                                 4
metabolite__Feruloyltryptamine_E1             0.046517           0.015043       -0.003114     -0.038651                                      3                                 2
       agri_aa_oil__Oil_C200_C220             0.045872           0.066942        0.051629      0.057619                                      5                                 4
```

## PCA Variance Summary

```text
context region_type  components  final_cumulative_variance
    mCG         cis          10                   0.218907
    mCG        gene          10                   0.231734
    mCG    promoter          10                   0.220255
   mCHG         cis          10                   0.221424
   mCHG        gene          10                   0.238847
   mCHG    promoter          10                   0.223030
   mCHH         cis          10                   0.207287
   mCHH        gene          10                   0.246528
   mCHH    promoter          10                   0.228917
```

## Interpretation

- This uses gene/promoter/cis-window methylation aggregation compressed by PCA.
- If this does not materially improve over genotype+population, methylation likely needs trait-specific sparse feature selection or higher-resolution promoter/gene windows instead of more global PCs.

## Outputs

- `data/processed/v0_1/b73_refgen_v4_gene_windows.tsv`
- `data/processed/v0_1/methylation_gene_region_pca.tsv`
- `data/processed/v0_1/methylation_gene_region_pca_variance.tsv`
- `results/v0_1_baseline/gene_methylation_pca_metrics.tsv`
- `results/v0_1_baseline/gene_methylation_pca_model_summary.tsv`
- `results/v0_1_baseline/gene_methylation_pca_trait_summary.tsv`
