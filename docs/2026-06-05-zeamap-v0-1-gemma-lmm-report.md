# ZEAMAP v0.1 GEMMA LMM GWAS

日期：2026-06-05

## Purpose

This is the paper-oriented mixed-linear-model GWAS upgrade for the ZEAMAP v0.1 oil-trait analysis. It uses GEMMA with a genotype-derived relatedness matrix, population covariates, multiple-testing correction, LD clumping, B73 RefGen_v4 gene mapping, and Manhattan/QQ plots.

## Setup

- Raw GEMMA directory: `results/v0_1_baseline/gemma_v0_1`
- Summary directory: `results/v0_1_baseline/gemma_lmm_v0_1`
- Traits: 10
- SNPs tested per trait: 199856
- GEMMA p-value column used: `p_lrt`
- Bonferroni threshold: 0.05 / tested SNPs
- FDR: Benjamini-Hochberg q <= 0.05
- LD clumping: +/- 250000 bp, r2 < 0.2, max 100 lead SNPs per trait
- Gene mapping: B73 RefGen_v4 gene/promoter/cis windows, cis threshold 10000 bp

## Trait-Level Summary

```text
                     trait  n_non_missing  variants_tested p_source_column  bonferroni_0_05  fdr_0_05_hits  bonferroni_hits  min_p_value  lambda_gc
agri_aa_oil__Oil_C200_C220            440           199856           p_lrt     2.501801e-07             25               19 2.348284e-25   1.009050
    agri_aa_oil__Oil_C18_1            440           199856           p_lrt     2.501801e-07             43               18 4.545209e-19   1.001425
    agri_aa_oil__Oil_C18_0            440           199856           p_lrt     2.501801e-07             53               21 4.249377e-17   0.984793
    agri_aa_oil__Oil_C16_0            440           199856           p_lrt     2.501801e-07             37               12 7.764919e-17   0.998323
      agri_aa_oil__Oil_OIL            440           199856           p_lrt     2.501801e-07             78               17 1.516051e-14   0.983963
agri_aa_oil__Oil_C182_C183            440           199856           p_lrt     2.501801e-07              4                4 1.867187e-13   1.010604
    agri_aa_oil__Oil_C20_0            440           199856           p_lrt     2.501801e-07             27               13 3.922545e-12   0.998100
    agri_aa_oil__Oil_C20_1            440           199856           p_lrt     2.501801e-07             33               12 2.007069e-11   0.995874
    agri_aa_oil__Oil_C18_2            440           199856           p_lrt     2.501801e-07             35                9 7.432554e-10   0.993735
    agri_aa_oil__Oil_C16_1            440           199856           p_lrt     2.501801e-07              3                1 2.081623e-07   1.018433
```

## Lambda GC Assessment

- GEMMA LMM lambda GC range: 0.984-1.018
- GEMMA LMM median lambda GC: 0.998
- Interpretation rule for manuscript use: lambda GC close to 1 with clean QQ plots is acceptable; persistent inflation requires stricter model/QC before making locus claims.

## Covariate LM vs GEMMA LMM

```text
                     trait  lambda_gc_covariate_lm  bonferroni_hits_covariate_lm  fdr_0_05_hits_covariate_lm  lambda_gc_gemma_lmm  bonferroni_hits_gemma_lmm  fdr_0_05_hits_gemma_lmm
      agri_aa_oil__Oil_OIL                3.970422                          4316                       42981             0.983963                         17                       78
    agri_aa_oil__Oil_C18_1                3.720343                          3603                       39399             1.001425                         18                       43
    agri_aa_oil__Oil_C18_2                3.756583                          3441                       38639             0.993735                          9                       35
    agri_aa_oil__Oil_C20_1                3.298848                          2944                       33044             0.995874                         12                       33
    agri_aa_oil__Oil_C20_0                3.496820                          2599                       33490             0.998100                         13                       27
    agri_aa_oil__Oil_C18_0                3.496141                          2455                       34705             0.984793                         21                       53
    agri_aa_oil__Oil_C16_0                3.225205                          2229                       29981             0.998323                         12                       37
agri_aa_oil__Oil_C200_C220                3.160989                          1477                       27376             1.009050                         19                       25
agri_aa_oil__Oil_C182_C183                2.405460                           635                       12109             1.010604                          4                        4
    agri_aa_oil__Oil_C16_1                2.978063                           970                       22306             1.018433                          1                        3
```

## Top Lead SNPs

```text
      variant_id  lead_rank  variant_index  n_miss allele1 allele0    af      beta       se  logl_H1   l_remle    l_mle       p_wald      p_value      p_score  chrom       pos                  trait  minus_log10_p   q_value_bh nearest_gene_id gene_relation  distance_to_gene_bp
 chr9.s_20246143          1         174304       0       C       T 0.839  0.074661 0.008626 362.1594  95.49727 100000.0 9.786869e-17 7.764919e-17 1.028594e-14      9  20246143 agri_aa_oil__Oil_C16_0      16.109863 1.551866e-11  Zm00001d045383     gene_body                    0
chr6.s_108218435          2         129018       0       C       T 0.180  0.060053 0.010235 343.5283  75.56241 100000.0 8.827897e-09 1.386503e-08 4.420232e-08      6 108218435 agri_aa_oil__Oil_C16_0       7.858079 6.927524e-04  Zm00001d036982     gene_body                    0
chr1.s_172833339          3          15485       0       A       G 0.066  0.090672 0.016539 341.8011  92.47222 100000.0 7.147120e-08 8.227436e-08 2.096927e-07      1 172833339 agri_aa_oil__Oil_C16_0       7.084735 3.288605e-03  Zm00001d031002     gene_body                    0
 chr4.s_32830369          4          82762       0       T       G 0.082  0.079739 0.015122 340.8453  99.57203 100000.0 2.126722e-07 2.209856e-07 5.024517e-07      4  32830369 agri_aa_oil__Oil_C16_0       6.655636 4.015027e-03  Zm00001d049510     gene_body                    0
 chr4.s_30481469          5          82605       0       A       G 0.059  0.097734 0.018670 340.3312  81.09954 100000.0 2.583127e-07 3.763461e-07 8.070439e-07      4  30481469 agri_aa_oil__Oil_C16_0       6.424413 5.528413e-03  Zm00001d049442    cis_window                 6677
chr7.s_146342995          6         148406       0       C       A 0.078  0.070274 0.013665 340.2773 107.42290 100000.0 4.118436e-07 3.979572e-07 8.482681e-07      7 146342995 agri_aa_oil__Oil_C16_0       6.400164 5.528413e-03  Zm00001d021214      promoter                    0
chr9.s_120520656          7         179530       0       G       A 0.136  0.056638 0.011099 340.2370 122.24620 100000.0 5.015572e-07 4.149297e-07 8.804882e-07      9 120520656 agri_aa_oil__Oil_C16_0       6.382025 5.528413e-03  Zm00001d047166     gene_body                    0
chr7.s_144353418          8         148220       0       A       G 0.074  0.069181 0.013606 339.7437  87.29129 100000.0 5.501665e-07 6.921142e-07 1.391630e-06      7 144353418 agri_aa_oil__Oil_C16_0       6.159822 7.280167e-03  Zm00001d021162     gene_body                    0
 chr6.s_94233130          9         127755       0       A       C 0.099  0.058791 0.012122 339.0702 129.00100 100000.0 1.727314e-06 1.393270e-06 2.610704e-06      6  94233130 agri_aa_oil__Oil_C16_0       5.855965 1.392267e-02  Zm00001d036608     gene_body                    0
  chr5.s_4796079         10         100823       0       G       C 0.067  0.059485 0.012350 338.6357 100.64840 100000.0 2.024155e-06 2.189659e-06 3.927925e-06      5   4796079 agri_aa_oil__Oil_C16_0       5.659624 1.902680e-02  Zm00001d013111    cis_window                   73
 chr9.s_20392814         11         174350       0       G       A 0.392  0.031953 0.006733 338.5051 121.73600 100000.0 2.830826e-06 2.508584e-06 4.442746e-06      9  20392814 agri_aa_oil__Oil_C16_0       5.600571 2.005422e-02  Zm00001d045389     gene_body                    0
 chr5.s_22604388         12         104549       0       G       A 0.058  0.081561 0.016900 338.3870  81.04039 100000.0 1.933775e-06 2.837298e-06 4.967545e-06      5  22604388 agri_aa_oil__Oil_C16_0       5.547095 2.180965e-02  Zm00001d013849    cis_window                 5032
 chr7.s_99517059         13         144703       0       A       G 0.107       NaN      NaN 338.0046       NaN 100000.0          NaN 4.227652e-06 7.137254e-06      7  99517059 agri_aa_oil__Oil_C16_0       5.373901 2.989741e-02  Zm00001d020206       nearest               195787
chr2.s_174573534         14          46718       0       T       A 0.074  0.063530 0.013651 337.9632 105.35300 100000.0 4.336165e-06 4.414325e-06 7.423614e-06      2 174573534 agri_aa_oil__Oil_C16_0       5.355136 2.989741e-02  Zm00001d005450     gene_body                    0
chr9.s_118648499         15         179378       0       G       A 0.065  0.069849 0.014895 337.9473  93.41672 100000.0 3.678808e-06 4.487843e-06 7.536121e-06      9 118648499 agri_aa_oil__Oil_C16_0       5.347962 2.989741e-02  Zm00001d047102    cis_window                  439
chr7.s_144660660         16         148226       0       A       T 0.065  0.068968 0.015043 337.6562 106.00350 100000.0 5.961940e-06 6.082683e-06 9.944153e-06      7 144660660 agri_aa_oil__Oil_C16_0       5.215905 3.798940e-02  Zm00001d021167     gene_body                    0
 chr8.s_39585362         17         158571       0       G       A 0.062  0.086508 0.018734 337.4757  83.54672 100000.0 5.126067e-06 7.345724e-06 1.181518e-05      8  39585362 agri_aa_oil__Oil_C16_0       5.133965 4.448749e-02  Zm00001d009147     gene_body                    0
chr4.s_243763709         18          98230       0       G       A 0.150  0.048382 0.010936 337.3177 174.88560 100000.0 1.226249e-05 8.665546e-06 1.374390e-05      4 243763709 agri_aa_oil__Oil_C16_0       5.062204 4.743381e-02  Zm00001d053931     gene_body                    0
chr7.s_146492766         19         148431       0       T       C 0.101  0.060840 0.013823 336.5969  87.35068 100000.0 1.357121e-05 1.844547e-05 2.751125e-05      7 146492766 agri_aa_oil__Oil_C16_0       4.734110 7.828143e-02  Zm00001d021221     gene_body                    0
 chr8.s_39847237         20         158593       0       A       G 0.060  0.084365 0.019180 336.5787  86.73486 100000.0 1.374156e-05 1.880108e-05 2.799971e-05      8  39847237 agri_aa_oil__Oil_C16_0       4.725817 7.828143e-02  Zm00001d009152    cis_window                  212
chr3.s_233925852         21          78860       0       A       T 0.208  0.032917 0.007707 336.5454 139.76500 100000.0 2.396771e-05 1.946952e-05 2.891610e-05      3 233925852 agri_aa_oil__Oil_C16_0       4.710645 7.941021e-02  Zm00001d044646     gene_body                    0
 chr5.s_15089795         22         103301       0       G       A 0.059  0.083996 0.019436 336.4723 102.37820 100000.0 1.923250e-05 2.102358e-05 3.103834e-05      5  15089795 agri_aa_oil__Oil_C16_0       4.677293 8.238605e-02  Zm00001d013595     gene_body                    0
 chr2.s_51361383         23          40776       0       T       A 0.131  0.044146 0.010313 336.4050 111.92860 100000.0 2.297835e-05 2.256436e-05 3.313175e-05      2  51361383 agri_aa_oil__Oil_C16_0       4.646577 8.508722e-02  Zm00001d003641    cis_window                 7504
chr2.s_154108264         24          45460       0       T       C 0.068  0.054808 0.013042 336.3057 138.91590 100000.0 3.211379e-05 2.504647e-05 3.648385e-05      2 154108264 agri_aa_oil__Oil_C16_0       4.601253 9.101250e-02  Zm00001d005018     gene_body                    0
 chr7.s_15677686         25         141027       0       A       C 0.061  0.057779 0.013643 336.2746 118.91310 100000.0 2.793824e-05 2.587969e-05 3.760395e-05      7  15677686 agri_aa_oil__Oil_C16_0       4.587041 9.236092e-02  Zm00001d019083     gene_body                    0
 chr9.s_18176195         26         174044       0       C       G 0.320 -0.028506 0.006820 336.1284 132.10640 100000.0 3.537135e-05 3.018102e-05 4.334946e-05      9  18176195 agri_aa_oil__Oil_C16_0       4.520266 1.058221e-01  Zm00001d045298    cis_window                   35
 chr2.s_25679602         27          37806       0       C       T 0.353  0.031527 0.007452 336.0293  96.95535 100000.0 2.845363e-05 3.349802e-05 4.774264e-05      2  25679602 agri_aa_oil__Oil_C16_0       4.474981 1.154272e-01  Zm00001d002884    cis_window                  380
chr3.s_213461451         28          75137       0       G       A 0.848 -0.041685 0.009987 335.9694 112.38630 100000.0 3.623080e-05 3.567980e-05 5.061658e-05      3 213461451 agri_aa_oil__Oil_C16_0       4.447578 1.208614e-01  Zm00001d043905     gene_body                    0
chr10.s_18681256         29         188432       0       T       C 0.742 -0.037607 0.009240 335.9352 255.69800 100000.0 5.585900e-05 3.698730e-05 5.233335e-05     10  18681256 agri_aa_oil__Oil_C16_0       4.431947 1.211825e-01  Zm00001d023753      promoter                    0
chr2.s_194058222         30          48732       0       T       C 0.609  0.030238 0.007214 335.8943 100.17380 100000.0 3.362242e-05 3.861536e-05 5.446555e-05      2 194058222 agri_aa_oil__Oil_C16_0       4.413240 1.244760e-01  Zm00001d005964     gene_body                    0
 chr3.s_12898900         31          58977       0       C       A 0.739  0.031644 0.007782 335.8160 165.08300 100000.0 5.673572e-05 4.193750e-05 5.879879e-05      3  12898900 agri_aa_oil__Oil_C16_0       4.377397 1.309603e-01  Zm00001d039717     gene_body                    0
chr1.s_276987614         32          26855       0       A       G 0.083  0.055602 0.013350 335.7674  99.16746 100000.0 3.763229e-05 4.413957e-05 6.165890e-05      1 276987614 agri_aa_oil__Oil_C16_0       4.355172 1.348749e-01  Zm00001d033872     gene_body                    0
 chr5.s_27759907         33         105124       0       T       C 0.091  0.052242 0.012707 335.7541 116.00740 100000.0 4.712289e-05 4.476401e-05 6.246827e-05      5  27759907 agri_aa_oil__Oil_C16_0       4.349071 1.348749e-01  Zm00001d013992     gene_body                    0
chr4.s_197014924         34          93027       0       C       G 0.341  0.030409 0.007417 335.7377 122.35370 100000.0 4.937505e-05 4.554684e-05 6.348192e-05      4 197014924 agri_aa_oil__Oil_C16_0       4.341542 1.348749e-01  Zm00001d052677      promoter                    0
chr1.s_295615070         35          30005       0       T       G 0.056  0.057474 0.013930 335.7066 106.65630 100000.0 4.432395e-05 4.706599e-05 6.544591e-05      1 295615070 agri_aa_oil__Oil_C16_0       4.327293 1.363249e-01  Zm00001d034522     gene_body                    0
 chr1.s_13075919         36           2745       0       A       C 0.436 -0.026584 0.006641 335.6089 188.90740 100000.0 7.354552e-05 5.217369e-05 7.202086e-05      1  13075919 agri_aa_oil__Oil_C16_0       4.282548 1.489604e-01  Zm00001d027764       nearest                15407
 chr6.s_92450649         37         127645       0       A       G 0.197  0.038011 0.009334 335.5840 113.56930 100000.0 5.532846e-05 5.356190e-05 7.380077e-05      6  92450649 agri_aa_oil__Oil_C16_0       4.271144 1.507700e-01  Zm00001d036563     gene_body                    0
chr6.s_106780881         38         128859       0       G       A 0.058  0.066648 0.016350 335.5540 111.06220 100000.0 5.445538e-05 5.528682e-05 7.600841e-05      6 106780881 agri_aa_oil__Oil_C16_0       4.257378 1.534639e-01  Zm00001d036933    cis_window                  424
 chr5.s_27296743         39         105099       0       T       C 0.056  0.077557 0.018859 335.5294  94.87729 100000.0 4.685464e-05 5.673946e-05 7.786429e-05      5  27296743 agri_aa_oil__Oil_C16_0       4.246115 1.553387e-01  Zm00001d013983     gene_body                    0
  chr7.s_9140798         40         140355       0       C       T 0.381  0.028228 0.007116 335.4966 200.09500 100000.0 8.531861e-05 5.874139e-05 8.041718e-05      7   9140798 agri_aa_oil__Oil_C16_0       4.231056 1.586462e-01  Zm00001d018913     gene_body                    0
```

## Top Lead Genes

```text
                 trait nearest_gene_id gene_relation  lead_snps  min_p_value  min_q_value_bh  max_minus_log10_p  min_distance_to_gene_bp
agri_aa_oil__Oil_C16_0  Zm00001d045383     gene_body          1 7.764919e-17    1.551866e-11          16.109863                        0
agri_aa_oil__Oil_C16_0  Zm00001d036982     gene_body          1 1.386503e-08    6.927524e-04           7.858079                        0
agri_aa_oil__Oil_C16_0  Zm00001d031002     gene_body          1 8.227436e-08    3.288605e-03           7.084735                        0
agri_aa_oil__Oil_C16_0  Zm00001d049510     gene_body          1 2.209856e-07    4.015027e-03           6.655636                        0
agri_aa_oil__Oil_C16_0  Zm00001d049442    cis_window          1 3.763461e-07    5.528413e-03           6.424413                     6677
agri_aa_oil__Oil_C16_0  Zm00001d021214      promoter          1 3.979572e-07    5.528413e-03           6.400164                        0
agri_aa_oil__Oil_C16_0  Zm00001d047166     gene_body          1 4.149297e-07    5.528413e-03           6.382025                        0
agri_aa_oil__Oil_C16_0  Zm00001d021162     gene_body          1 6.921142e-07    7.280167e-03           6.159822                        0
agri_aa_oil__Oil_C16_0  Zm00001d036608     gene_body          1 1.393270e-06    1.392267e-02           5.855965                        0
agri_aa_oil__Oil_C16_0  Zm00001d013111    cis_window          1 2.189659e-06    1.902680e-02           5.659624                       73
agri_aa_oil__Oil_C16_0  Zm00001d045389     gene_body          1 2.508584e-06    2.005422e-02           5.600571                        0
agri_aa_oil__Oil_C16_0  Zm00001d013849    cis_window          1 2.837298e-06    2.180965e-02           5.547095                     5032
agri_aa_oil__Oil_C16_0  Zm00001d020206       nearest          1 4.227652e-06    2.989741e-02           5.373901                   195787
agri_aa_oil__Oil_C16_0  Zm00001d005450     gene_body          1 4.414325e-06    2.989741e-02           5.355136                        0
agri_aa_oil__Oil_C16_0  Zm00001d047102    cis_window          1 4.487843e-06    2.989741e-02           5.347962                      439
agri_aa_oil__Oil_C16_0  Zm00001d021167     gene_body          1 6.082683e-06    3.798940e-02           5.215905                        0
agri_aa_oil__Oil_C16_0  Zm00001d009147     gene_body          1 7.345724e-06    4.448749e-02           5.133965                        0
agri_aa_oil__Oil_C16_0  Zm00001d053931     gene_body          1 8.665546e-06    4.743381e-02           5.062204                        0
agri_aa_oil__Oil_C16_0  Zm00001d021221     gene_body          1 1.844547e-05    7.828143e-02           4.734110                        0
agri_aa_oil__Oil_C16_0  Zm00001d009152    cis_window          1 1.880108e-05    7.828143e-02           4.725817                      212
agri_aa_oil__Oil_C16_0  Zm00001d044646     gene_body          1 1.946952e-05    7.941021e-02           4.710645                        0
agri_aa_oil__Oil_C16_0  Zm00001d013595     gene_body          1 2.102358e-05    8.238605e-02           4.677293                        0
agri_aa_oil__Oil_C16_0  Zm00001d003641    cis_window          1 2.256436e-05    8.508722e-02           4.646577                     7504
agri_aa_oil__Oil_C16_0  Zm00001d005018     gene_body          1 2.504647e-05    9.101250e-02           4.601253                        0
agri_aa_oil__Oil_C16_0  Zm00001d019083     gene_body          1 2.587969e-05    9.236092e-02           4.587041                        0
agri_aa_oil__Oil_C16_0  Zm00001d045298    cis_window          1 3.018102e-05    1.058221e-01           4.520266                       35
agri_aa_oil__Oil_C16_0  Zm00001d002884    cis_window          1 3.349802e-05    1.154272e-01           4.474981                      380
agri_aa_oil__Oil_C16_0  Zm00001d043905     gene_body          1 3.567980e-05    1.208614e-01           4.447578                        0
agri_aa_oil__Oil_C16_0  Zm00001d023753      promoter          1 3.698730e-05    1.211825e-01           4.431947                        0
agri_aa_oil__Oil_C16_0  Zm00001d005964     gene_body          1 3.861536e-05    1.244760e-01           4.413240                        0
agri_aa_oil__Oil_C16_0  Zm00001d039717     gene_body          1 4.193750e-05    1.309603e-01           4.377397                        0
agri_aa_oil__Oil_C16_0  Zm00001d033872     gene_body          1 4.413957e-05    1.348749e-01           4.355172                        0
agri_aa_oil__Oil_C16_0  Zm00001d013992     gene_body          1 4.476401e-05    1.348749e-01           4.349071                        0
agri_aa_oil__Oil_C16_0  Zm00001d052677      promoter          1 4.554684e-05    1.348749e-01           4.341542                        0
agri_aa_oil__Oil_C16_0  Zm00001d034522     gene_body          1 4.706599e-05    1.363249e-01           4.327293                        0
agri_aa_oil__Oil_C16_0  Zm00001d027764       nearest          1 5.217369e-05    1.489604e-01           4.282548                    15407
agri_aa_oil__Oil_C16_0  Zm00001d036563     gene_body          1 5.356190e-05    1.507700e-01           4.271144                        0
agri_aa_oil__Oil_C16_0  Zm00001d036933    cis_window          1 5.528682e-05    1.534639e-01           4.257378                      424
agri_aa_oil__Oil_C16_0  Zm00001d013983     gene_body          1 5.673946e-05    1.553387e-01           4.246115                        0
agri_aa_oil__Oil_C16_0  Zm00001d018913     gene_body          1 5.874139e-05    1.586462e-01           4.231056                        0
```

## Paper-Readiness Assessment

- GEMMA LMM is the current manuscript-facing GWAS baseline; the earlier covariate-only linear GWAS is kept only as a diagnostic baseline.
- Lead SNPs are manuscript candidates only if lambda GC/QQ are acceptable and the locus remains after LD clumping.
- Final paper claims still need biological interpretation, candidate-gene literature checks, and preferably an external or split/cohort replication strategy.

## Outputs

- `results/v0_1_baseline/gemma_lmm_v0_1/gemma_lmm_summary.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/gemma_lmm_lead_snps.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/gemma_lmm_gene_summary.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/figures/*manhattan.png`
- `results/v0_1_baseline/gemma_lmm_v0_1/figures/*qq.png`
