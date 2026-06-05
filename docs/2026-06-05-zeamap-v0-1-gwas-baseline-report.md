# ZEAMAP v0.1 covariate-adjusted GWAS baseline

日期：2026-06-05

## Purpose

This is the paper-oriented v0.1 GWAS baseline for the strongest ZEAMAP traits. It uses all non-missing accessions for each trait, adjusts phenotype and SNP dosage for population covariates, applies genome-wide multiple-testing thresholds, performs LD clumping, maps lead SNPs to B73 RefGen_v4 genes, and writes Manhattan/QQ plots.

## Setup

- Target family/tier: oil / high
- Traits: 10
- Covariates: PC1,PC2,PC3,K1,K2,K3
- SNPs tested per trait: 199,856
- Bonferroni threshold: 0.05 / tested SNPs
- FDR: Benjamini-Hochberg q <= 0.05
- LD clumping: +/- 250000 bp, r2 < 0.2, max 100 lead SNPs per trait
- Gene mapping: B73 RefGen_v4 gene/promoter/cis windows, cis threshold 10000 bp

## Target Traits

```text
agri_aa_oil__Oil_OIL
agri_aa_oil__Oil_C18_1
agri_aa_oil__Oil_C18_2
agri_aa_oil__Oil_C20_1
agri_aa_oil__Oil_C20_0
agri_aa_oil__Oil_C18_0
agri_aa_oil__Oil_C16_0
agri_aa_oil__Oil_C200_C220
agri_aa_oil__Oil_C182_C183
agri_aa_oil__Oil_C16_1
```

## Trait-Level Summary

```text
                     trait  n_non_missing  variants_tested  bonferroni_0_05  fdr_0_05_hits  bonferroni_hits  min_p_value  lambda_gc
      agri_aa_oil__Oil_OIL            440           199856     2.501801e-07          42981             4316 2.762556e-54   3.970422
    agri_aa_oil__Oil_C18_1            440           199856     2.501801e-07          39399             3603 1.713449e-51   3.720343
    agri_aa_oil__Oil_C18_2            440           199856     2.501801e-07          38639             3441 1.696169e-42   3.756583
    agri_aa_oil__Oil_C20_1            440           199856     2.501801e-07          33044             2944 1.348755e-40   3.298848
    agri_aa_oil__Oil_C20_0            440           199856     2.501801e-07          33490             2599 5.377956e-43   3.496820
    agri_aa_oil__Oil_C18_0            440           199856     2.501801e-07          34705             2455 1.765848e-44   3.496141
    agri_aa_oil__Oil_C16_0            440           199856     2.501801e-07          29981             2229 4.096988e-34   3.225205
agri_aa_oil__Oil_C200_C220            440           199856     2.501801e-07          27376             1477 6.368169e-52   3.160989
agri_aa_oil__Oil_C182_C183            440           199856     2.501801e-07          12109              635 6.304783e-21   2.405460
    agri_aa_oil__Oil_C16_1            440           199856     2.501801e-07          22306              970 5.887690e-24   2.978063
```

## Top Lead SNPs

```text
                 trait  lead_rank  variant_index  chrom       pos        variant_id ref alt  info_maf  info_ns  n_non_missing  beta_residual_scale  partial_correlation    t_stat      p_value   q_value_bh  minus_log10_p nearest_gene_id gene_relation  distance_to_gene_bp
agri_aa_oil__Oil_C16_0          1         104549      5  22604388   chr5.s_22604388   A   G  0.052268      507            440             0.539282             0.539282 13.310091 4.096988e-34 8.188077e-29      33.387535  Zm00001d013849    cis_window                 5032
agri_aa_oil__Oil_C16_0          2         158581      8  39633330   chr8.s_39633330   C   T  0.055227      507            440             0.529035             0.529035 12.957577 1.141742e-32 6.689010e-28      31.942432  Zm00001d009150     gene_body                    0
agri_aa_oil__Oil_C16_0          3          82605      4  30481469   chr4.s_30481469   G   A  0.052268      507            440             0.528950             0.528950 12.954670 1.173317e-32 6.689010e-28      31.930585  Zm00001d049442    cis_window                 6677
agri_aa_oil__Oil_C16_0          4         105099      5  27296743   chr5.s_27296743   C   T  0.054241      507            440             0.519712             0.519712 12.643656 2.139854e-31 5.345784e-27      30.669616  Zm00001d013983     gene_body                    0
agri_aa_oil__Oil_C16_0          5         148220      7 144353418  chr7.s_144353418   G   A  0.064103      507            440             0.510323             0.510323 12.333817 3.739886e-30 5.749528e-26      29.427142  Zm00001d021162     gene_body                    0
agri_aa_oil__Oil_C16_0          6          82770      4  32894031   chr4.s_32894031   G   A  0.094675      507            440             0.506597             0.506597 12.212521 1.135952e-29 1.513513e-25      28.944640  Zm00001d049511     gene_body                    0
agri_aa_oil__Oil_C16_0          7         129013      6 108212118  chr6.s_108212118   G   C  0.068047      507            440             0.500971             0.500971 12.031107 5.926068e-29 7.402251e-25      28.227233  Zm00001d036981    cis_window                  247
agri_aa_oil__Oil_C16_0          8         103301      5  15089795   chr5.s_15089795   A   G  0.053254      507            440             0.491184             0.491184 11.720348 9.759716e-28 1.147375e-23      27.010563  Zm00001d013595     gene_body                    0
agri_aa_oil__Oil_C16_0          9          91617      4 183828966  chr4.s_183828966   C   T  0.054241      507            440             0.473081             0.473081 11.160726 1.377852e-25 1.147384e-21      24.860797  Zm00001d052227    cis_window                 6066
agri_aa_oil__Oil_C16_0         10         194017     10 118153332 chr10.s_118153332   C   A  0.061144      507            440             0.460365             0.460365 10.778625 3.753995e-24 2.587098e-20      23.425506  Zm00001d025421    cis_window                 1773
agri_aa_oil__Oil_C16_0         11         157774      8  23814651   chr8.s_23814651   C   G  0.051282      507            440             0.456217             0.456217 10.655845 1.070978e-23 6.932458e-20      22.970219  Zm00001d008883     gene_body                    0
agri_aa_oil__Oil_C16_0         12         192678     10  98280209  chr10.s_98280209   C   T  0.051282      507            440             0.456201             0.456201 10.655372 1.075305e-23 6.932458e-20      22.968468  Zm00001d024995      promoter                    0
agri_aa_oil__Oil_C16_0         13         104612      5  23154994   chr5.s_23154994   G   C  0.064103      507            440             0.451758             0.451758 10.524803 3.254139e-23 2.032373e-19      22.487564  Zm00001d013861     gene_body                    0
agri_aa_oil__Oil_C16_0         14          15485      1 172833339  chr1.s_172833339   G   A  0.061144      507            440             0.448907             0.448907 10.441566 6.564974e-23 3.748713e-19      22.182767  Zm00001d031002     gene_body                    0
agri_aa_oil__Oil_C16_0         15          22906      1 241512051  chr1.s_241512051   C   T  0.051282      507            440             0.444698             0.444698 10.319388 1.828394e-22 9.616198e-19      21.737930  Zm00001d032887     gene_body                    0
agri_aa_oil__Oil_C16_0         16           3498      1  17949282   chr1.s_17949282   A   G  0.059172      507            440             0.444498             0.444498 10.313606 1.918878e-22 9.833317e-19      21.716953  Zm00001d027934     gene_body                    0
agri_aa_oil__Oil_C16_0         17         188283     10  16235157  chr10.s_16235157   G   A  0.067061      507            440             0.443829             0.443829 10.294265 2.255079e-22 1.112538e-18      21.646838  Zm00001d023703      promoter                    0
agri_aa_oil__Oil_C16_0         18         148431      7 146492766  chr7.s_146492766   C   T  0.093688      507            440             0.443590             0.443590 10.287373 2.388517e-22 1.118630e-18      21.621872  Zm00001d021221     gene_body                    0
agri_aa_oil__Oil_C16_0         19         104091      5  19732503   chr5.s_19732503   G   A  0.066075      507            440             0.443559             0.443559 10.286459 2.406787e-22 1.118630e-18      21.618562  Zm00001d013767     gene_body                    0
agri_aa_oil__Oil_C16_0         20         162786      8 121752076  chr8.s_121752076   G   A  0.058185      507            440             0.441255             0.441255 10.220075 4.182121e-22 1.889402e-18      21.378603  Zm00001d010607     gene_body                    0
agri_aa_oil__Oil_C16_0         21          17201      1 192621307  chr1.s_192621307   A   T  0.061144      507            440             0.441183             0.441183 10.218017 4.254217e-22 1.889402e-18      21.371180  Zm00001d031518     gene_body                    0
agri_aa_oil__Oil_C16_0         22          45460      2 154108264  chr2.s_154108264   C   T  0.061144      507            440             0.436329             0.436329 10.078956 1.344076e-21 5.596283e-18      20.871576  Zm00001d005018     gene_body                    0
agri_aa_oil__Oil_C16_0         23         104199      5  20164742   chr5.s_20164742   A   G  0.087771      507            440             0.435150             0.435150 10.045369 1.772048e-21 7.083088e-18      20.751525  Zm00001d013787     gene_body                    0
agri_aa_oil__Oil_C16_0         24          65767      3 136775175  chr3.s_136775175   C   T  0.056213      507            440             0.434909             0.434909 10.038502 1.874955e-21 7.347472e-18      20.727009  Zm00001d041768     gene_body                    0
agri_aa_oil__Oil_C16_0         25         160892      8  94987397   chr8.s_94987397   C   T  0.061144      507            440             0.431344             0.431344  9.937323 4.295663e-21 1.619838e-17      20.366970  Zm00001d010009     gene_body                    0
agri_aa_oil__Oil_C16_0         26         105005      5  26236965   chr5.s_26236965   T   C  0.151874      507            440             0.427716             0.427716  9.834917 9.889406e-21 3.593558e-17      20.004830  Zm00001d013958    cis_window                  360
agri_aa_oil__Oil_C16_0         27          59069      3  13691003   chr3.s_13691003   G   T  0.065089      507            440             0.427217             0.427217  9.820865 1.108357e-20 3.955567e-17      19.955320  Zm00001d039747     gene_body                    0
agri_aa_oil__Oil_C16_0         28         145534      7 112561538  chr7.s_112561538   A   G  0.055227      507            440            -0.425681            -0.425681 -9.777745 1.571606e-20 5.415431e-17      19.803656  Zm00001d020417      promoter                    0
agri_aa_oil__Oil_C16_0         29          91775      4 185644876  chr4.s_185644876   C   T  0.066075      507            440             0.425471             0.425471  9.771850 1.648331e-20 5.583539e-17      19.782956  Zm00001d052276     gene_body                    0
agri_aa_oil__Oil_C16_0         30           8371      1  54036091   chr1.s_54036091   C   A  0.089744      507            440             0.424464             0.424464  9.743640 2.070169e-20 6.895596e-17      19.683994  Zm00001d028995     gene_body                    0
agri_aa_oil__Oil_C16_0         31         128903      6 107402136  chr6.s_107402136   G   A  0.065089      507            440             0.424303             0.424303  9.739120 2.147064e-20 7.034486e-17      19.668155  Zm00001d036959     gene_body                    0
agri_aa_oil__Oil_C16_0         32         104350      5  21345555   chr5.s_21345555   C   G  0.057199      507            440             0.420874             0.420874  9.643397 4.636779e-20 1.470933e-16      19.333784  Zm00001d013818     gene_body                    0
agri_aa_oil__Oil_C16_0         33          18716      1 204437858  chr1.s_204437858   A   G  0.104536      507            440             0.416839             0.416839  9.531376 1.134724e-19 3.488944e-16      18.945110  Zm00001d031860     gene_body                    0
agri_aa_oil__Oil_C16_0         34          97470      4 241402734  chr4.s_241402734   C   T  0.050296      507            440             0.416752             0.416752  9.528965 1.156711e-19 3.502661e-16      18.936775  Zm00001d053802    cis_window                 1172
agri_aa_oil__Oil_C16_0         35          68909      3 170135187  chr3.s_170135187   G   A  0.052268      507            440             0.415510             0.415510  9.494626 1.519767e-19 4.533351e-16      18.818223  Zm00001d042508     gene_body                    0
agri_aa_oil__Oil_C16_0         36          91609      4 183713852  chr4.s_183713852   T   A  0.078895      507            440             0.413129             0.413129  9.428995 2.556253e-19 7.512977e-16      18.592396  Zm00001d052225     gene_body                    0
agri_aa_oil__Oil_C16_0         37          23175      1 244289648  chr1.s_244289648   T   G  0.142998      507            440            -0.412412            -0.412412 -9.409259 2.987567e-19 8.653379e-16      18.524682  Zm00001d032944     gene_body                    0
agri_aa_oil__Oil_C16_0         38          23896      1 252140053  chr1.s_252140053   G   A  0.068047      507            440             0.411463             0.411463  9.383206 3.669156e-19 1.047575e-15      18.435434  Zm00001d033150    cis_window                  294
agri_aa_oil__Oil_C16_0         39         164289      8 138009085  chr8.s_138009085   C   T  0.056213      507            440             0.410332             0.410332  9.352179 4.684341e-19 1.282457e-15      18.329352  Zm00001d011068    cis_window                  371
agri_aa_oil__Oil_C16_0         40         103516      5  15984296   chr5.s_15984296   T   C  0.088757      507            440             0.408513             0.408513  9.302387 6.924888e-19 1.845307e-15      18.159587  Zm00001d013638    cis_window                  181
```

## Paper-Readiness Assessment

- This is a reproducible v0.1 covariate-adjusted GWAS baseline, but it is not yet sufficient as a final manuscript GWAS result.
- Lambda GC is high across all 10 oil traits (2.41-3.97), meaning PC/K covariates do not fully control relatedness, LD, or residual population structure.
- The large number of Bonferroni/FDR hits should be treated as evidence of inflation, not as thousands of independent robust loci.
- Before a final manuscript claim, run a mixed-linear-model GWAS with kinship correction, compare lambda GC/QQ plots, and require lead loci to replicate across model specifications.
- Lead SNPs and mapped genes are paper candidates for follow-up, not causal claims by themselves.

## Required Upgrade For Paper-Level GWAS

1. Install/run a mixed-linear-model GWAS tool such as GEMMA, EMMAX, GAPIT, or equivalent.
2. Build a kinship matrix from the filtered genotype set.
3. Re-run the 10 high-priority oil traits with MLM/LMM.
4. Compare covariate-adjusted linear model vs MLM for lambda GC, QQ plots, and lead SNP overlap.
5. Only loci stable after MLM and LD clumping should enter a manuscript candidate-gene table.

## Outputs

- `results/v0_1_baseline/gwas_v0_1/gwas_summary.tsv`
- `results/v0_1_baseline/gwas_v0_1/gwas_lead_snps.tsv`
- `results/v0_1_baseline/gwas_v0_1/gwas_gene_summary.tsv`
- `results/v0_1_baseline/gwas_v0_1/per_trait/*.tsv` (local only; ignored by git because each table is large)
- `results/v0_1_baseline/gwas_v0_1/figures/*manhattan.png`
- `results/v0_1_baseline/gwas_v0_1/figures/*qq.png`
