# ZEAMAP v0.1 sparse methylation feature selection

日期：2026-06-05

## Setup

- Target traits: 10
- Candidate methylation features: 4500
- Candidate rule: top 500 variable genes per methylation context x region type
- Train-only correlation prefilter per trait/seed: top 200
- Sparse model: genotype+population features plus selected gene-window methylation features, ElasticNetCV
- Seeds: 20260605,20260606,20260607,20260608,20260609

## Target Traits

```text
agri_aa_oil__Kernernumberperrow
agri_aa_oil__Oil_C20_1P
metabolite__Norcinnamolaurine_E1
agri_aa_oil__Oil_C18_0
agri_aa_oil__100grainweight
metabolite__Pro_Leu_E1
agri_aa_oil__Plantheight
agri_aa_oil__Oil_C200_C220
agri_aa_oil__Oil_C16_1
agri_aa_oil__Oil_C180_C200
```

## Model Summary

```text
                                            model  seeds  traits_evaluated  median_r2   mean_r2  median_pearson  mean_pearson  positive_r2_fraction
   genotype_population_gene_methylation_pca_ridge      5                10   0.159932  0.174987        0.448749      0.456377                  0.86
                        genotype_population_ridge      5                10   0.106324  0.128903        0.414277      0.402479                  0.76
genotype_population_sparse_methylation_elasticnet      5                10   0.024821 -0.000615        0.337505      0.359863                  0.58
```

## Trait Summary

```text
                           trait  median_pearson_gain_sparse_vs_base  median_r2_gain_sparse_vs_base  median_pearson_gain_sparse_vs_pca  median_r2_gain_sparse_vs_pca  sparse_better_than_base_pearson_seeds  sparse_better_than_pca_pearson_seeds
      agri_aa_oil__Oil_C180_C200                            0.073192                       0.030692                          -0.029728                     -0.062420                                      3                                     1
 agri_aa_oil__Kernernumberperrow                            0.030465                      -0.036853                          -0.050125                     -0.087884                                      3                                     0
          metabolite__Pro_Leu_E1                            0.000844                      -0.044609                           0.002611                     -0.086389                                      3                                     3
      agri_aa_oil__Oil_C200_C220                           -0.017767                      -0.015703                          -0.121923                     -0.086348                                      1                                     0
         agri_aa_oil__Oil_C20_1P                           -0.025751                      -0.021317                          -0.005721                     -0.043228                                      2                                     2
        agri_aa_oil__Plantheight                           -0.037897                      -0.020084                          -0.109980                     -0.109515                                      1                                     0
          agri_aa_oil__Oil_C18_0                           -0.081139                      -0.073165                          -0.148043                     -0.131591                                      0                                     0
          agri_aa_oil__Oil_C16_1                           -0.094140                      -0.157505                          -0.108131                     -0.171100                                      1                                     0
     agri_aa_oil__100grainweight                           -0.098776                      -0.090212                          -0.161476                     -0.155498                                      1                                     0
metabolite__Norcinnamolaurine_E1                           -0.119003                      -0.213600                          -0.176049                     -0.247339                                      1                                     1
```

## Top Selected Methylation Features

```text
                      trait                                 feature  selected_seeds  mean_coefficient  mean_abs_coefficient context region_type        gene_id chrom  start_1based  end_1based strand  variance_rank_within_combo  variance  missing_fraction_before_impute
agri_aa_oil__100grainweight methwin__mCHG__promoter__Zm00001d042164               5          0.041861              0.041861    mCHG    promoter Zm00001d042164     3     154317876   154325586      +                         243  0.116221                             0.0
agri_aa_oil__100grainweight  methwin__mCG__promoter__Zm00001d042164               5          0.032796              0.032796     mCG    promoter Zm00001d042164     3     154317876   154325586      +                         345  0.143415                             0.0
agri_aa_oil__100grainweight     methwin__mCHH__gene__Zm00001d020234               5         -0.019040              0.019040    mCHH        gene Zm00001d020234     7     101492829   101504550      -                         234  0.006728                             0.0
agri_aa_oil__100grainweight     methwin__mCHH__gene__Zm00001d007923               4         -0.076618              0.076618    mCHH        gene Zm00001d007923     2     242818296   242819090      -                         474  0.002971                             0.0
agri_aa_oil__100grainweight      methwin__mCHG__cis__Zm00001d046722               4         -0.061213              0.061213    mCHG         cis Zm00001d046722     9     103539957   103559119      +                         277  0.132244                             0.0
agri_aa_oil__100grainweight      methwin__mCHH__cis__Zm00001d008543               4         -0.054476              0.054476    mCHH         cis Zm00001d008543     8      12496738    12498216      -                         305  0.027814                             0.0
agri_aa_oil__100grainweight       methwin__mCG__cis__Zm00001d040396               4          0.046285              0.046285     mCG         cis Zm00001d040396     3      41248476    41249543      -                         159  0.173740                             0.0
agri_aa_oil__100grainweight  methwin__mCG__promoter__Zm00001d046714               4         -0.039727              0.039727     mCG    promoter Zm00001d046714     9     103118697   103123559      +                         440  0.136769                             0.0
agri_aa_oil__100grainweight      methwin__mCG__gene__Zm00001d039417               4          0.036386              0.036386     mCG        gene Zm00001d039417     3       3828028     3837246      +                         287  0.139616                             0.0
agri_aa_oil__100grainweight  methwin__mCG__promoter__Zm00001d008878               4         -0.026711              0.026711     mCG    promoter Zm00001d008878     8      23569227    23569865      -                         198  0.155492                             0.0
agri_aa_oil__100grainweight      methwin__mCG__gene__Zm00001d020562               4         -0.026108              0.026108     mCG        gene Zm00001d020562     7     122351840   122352624      -                         212  0.146712                             0.0
agri_aa_oil__100grainweight  methwin__mCG__promoter__Zm00001d020562               4         -0.026106              0.026106     mCG    promoter Zm00001d020562     7     122351840   122352624      -                         297  0.146712                             0.0
agri_aa_oil__100grainweight     methwin__mCHH__gene__Zm00001d018731               4         -0.015055              0.015055    mCHH        gene Zm00001d018731     7       3330940     3335717      +                         127  0.009951                             0.0
agri_aa_oil__100grainweight      methwin__mCHH__cis__Zm00001d029104               4          0.013748              0.013748    mCHH         cis Zm00001d029104     1      58176945    58182237      +                         216  0.032830                             0.0
agri_aa_oil__100grainweight      methwin__mCHH__cis__Zm00001d029103               4          0.013748              0.013748    mCHH         cis Zm00001d029103     1      58170770    58174845      +                         215  0.032830                             0.0
agri_aa_oil__100grainweight  methwin__mCG__promoter__Zm00001d042856               4         -0.013567              0.013567     mCG    promoter Zm00001d042856     3     182225599   182227138      +                         154  0.159172                             0.0
agri_aa_oil__100grainweight       methwin__mCG__cis__Zm00001d042856               4         -0.013565              0.013565     mCG         cis Zm00001d042856     3     182225599   182227138      +                         405  0.159172                             0.0
agri_aa_oil__100grainweight       methwin__mCG__cis__Zm00001d042857               4         -0.013556              0.013556     mCG         cis Zm00001d042857     3     182227464   182227670      -                         404  0.159172                             0.0
agri_aa_oil__100grainweight methwin__mCHH__promoter__Zm00001d010143               3          0.086871              0.086871    mCHH    promoter Zm00001d010143     8     101193687   101196577      +                         453  0.011514                             0.0
agri_aa_oil__100grainweight     methwin__mCHH__gene__Zm00001d049980               3         -0.075862              0.075862    mCHH        gene Zm00001d049980     4      56787786    56805442      +                         495  0.002599                             0.0
agri_aa_oil__100grainweight methwin__mCHH__promoter__Zm00001d016311               3          0.072188              0.072188    mCHH    promoter Zm00001d016311     5     156652377   156668073      -                         461  0.011377                             0.0
agri_aa_oil__100grainweight      methwin__mCHG__cis__Zm00001d046460               3         -0.061599              0.061599    mCHG         cis Zm00001d046460     9      90925903    90927321      +                         490  0.125103                             0.0
agri_aa_oil__100grainweight      methwin__mCHG__cis__Zm00001d003192               3          0.048093              0.048093    mCHG         cis Zm00001d003192     2      35226569    35229786      -                          41  0.154044                             0.0
agri_aa_oil__100grainweight     methwin__mCHG__gene__Zm00001d003192               3          0.048093              0.048093    mCHG        gene Zm00001d003192     2      35226569    35229786      -                          14  0.154044                             0.0
agri_aa_oil__100grainweight      methwin__mCG__gene__Zm00001d044581               3          0.041027              0.041027     mCG        gene Zm00001d044581     3     232470618   232478894      +                         229  0.144645                             0.0
agri_aa_oil__100grainweight      methwin__mCHG__cis__Zm00001d030856               3         -0.036714              0.036714    mCHG         cis Zm00001d030856     1     163637977   163639965      -                         243  0.134348                             0.0
agri_aa_oil__100grainweight      methwin__mCG__gene__Zm00001d034043               3         -0.035334              0.035334     mCG        gene Zm00001d034043     1     282043067   282045983      -                         284  0.139931                             0.0
agri_aa_oil__100grainweight      methwin__mCG__gene__Zm00001d018731               3         -0.032094              0.032094     mCG        gene Zm00001d018731     7       3330940     3335717      +                         129  0.155127                             0.0
agri_aa_oil__100grainweight  methwin__mCG__promoter__Zm00001d042171               3          0.021214              0.021214     mCG    promoter Zm00001d042171     3     154796683   154797198      -                         229  0.152017                             0.0
agri_aa_oil__100grainweight      methwin__mCG__gene__Zm00001d042171               3          0.021213              0.021213     mCG        gene Zm00001d042171     3     154796683   154797198      -                         152  0.152017                             0.0
```

## Interpretation

- This is a trait-specific sparse screen, not a final biological claim.
- A useful methylation signal should beat genotype+population across multiple seeds and repeatedly select the same gene/context/region features.
- If sparse methylation does not beat the PCA methylation result, the current methylation modality is best kept as low-priority auxiliary metadata in v0.1.
- Actual result: sparse methylation underperforms both gene methylation PCA and genotype+population baseline overall, so raw gene-window methylation should not be promoted to the v0.1 main model input.
- The selected feature table remains useful as an exploratory candidate gene/window list for follow-up, especially for traits with small positive sparse gains such as `agri_aa_oil__Oil_C180_C200`.

## Outputs

- `data/processed/v0_1/methylation_gene_window_sparse_candidates.tsv`
- `data/processed/v0_1/methylation_gene_window_sparse_candidate_metadata.tsv`
- `results/v0_1_baseline/sparse_methylation_selection_metrics.tsv`
- `results/v0_1_baseline/sparse_methylation_selection_model_summary.tsv`
- `results/v0_1_baseline/sparse_methylation_selection_trait_summary.tsv`
- `results/v0_1_baseline/sparse_methylation_selected_features.tsv`
