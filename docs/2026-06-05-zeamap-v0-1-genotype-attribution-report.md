# ZEAMAP v0.1 genotype attribution screen

日期：2026-06-05

## Setup

- Target traits: top 15 final benchmark traits by ridge median Pearson
- Seeds: 20260605,20260606,20260607,20260608,20260609
- Per seed: top 200 SNPs by absolute train-split SNP-trait correlation
- Output per trait: top 50 stable SNPs after seed aggregation
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
agri_aa_oil__kernellength
agri_aa_oil__Oil_C182_C183
agri_aa_oil__Oil_C18_3P
agri_aa_oil__Oil_C16_1
agri_aa_oil__Headingdate
agri_aa_oil__Oil_C22_0
agri_aa_oil__Oil_C24_0P
```

## Top SNP Candidates

```text
                   trait  variant_index  chrom       pos        variant_id ref alt  info_maf  info_ns  selected_seeds  mean_train_correlation  mean_abs_train_correlation  max_abs_train_correlation  median_seed_rank nearest_gene_id gene_relation  distance_to_gene_bp
agri_aa_oil__Headingdate          79230      4   1056408    chr4.s_1056408   T   C  0.459566      507               5                0.424929                    0.424929                   0.440033               2.0  Zm00001d048603     gene_body                    0
agri_aa_oil__Headingdate         160511      8  86442889   chr8.s_86442889   C   T  0.133136      507               5                0.402306                    0.402306                   0.464147               9.0  Zm00001d009872    cis_window                 2628
agri_aa_oil__Headingdate         160529      8  86616046   chr8.s_86616046   G   A  0.135108      507               5                0.398944                    0.398944                   0.457278              10.0  Zm00001d009873     gene_body                    0
agri_aa_oil__Headingdate         160525      8  86597172   chr8.s_86597172   T   C  0.134122      507               5                0.398915                    0.398915                   0.465299              22.0  Zm00001d009873     gene_body                    0
agri_aa_oil__Headingdate         160481      8  85585634   chr8.s_85585634   G   A  0.178501      507               5                0.398145                    0.398145                   0.444755               7.0  Zm00001d009860      promoter                    0
agri_aa_oil__Headingdate         167160      8 161299368  chr8.s_161299368   C   T  0.415187      507               5                0.393153                    0.393153                   0.402129               9.0  Zm00001d011774     gene_body                    0
agri_aa_oil__Headingdate         160479      8  85575476   chr8.s_85575476   C   T  0.175542      507               5                0.386113                    0.386113                   0.426463              12.0  Zm00001d009859     gene_body                    0
agri_aa_oil__Headingdate         160504      8  86348003   chr8.s_86348003   G   A  0.129191      507               5                0.384981                    0.384981                   0.446248              32.0  Zm00001d009871       nearest                60404
agri_aa_oil__Headingdate         193039     10 104219821 chr10.s_104219821   C   T  0.430966      507               5                0.382770                    0.382770                   0.410958              18.0  Zm00001d025103     gene_body                    0
agri_aa_oil__Headingdate          76259      3 219821962  chr3.s_219821962   A   G  0.432939      507               5                0.376418                    0.376418                   0.393696              26.0  Zm00001d044119     gene_body                    0
agri_aa_oil__Headingdate          65576      3 134685666  chr3.s_134685666   G   T  0.273176      507               5                0.374126                    0.374126                   0.395761              37.0  Zm00001d041714     gene_body                    0
agri_aa_oil__Headingdate          99389      5   1350288    chr5.s_1350288   T   C  0.095661      507               5                0.372631                    0.372631                   0.407812              39.0  Zm00001d012865     gene_body                    0
agri_aa_oil__Headingdate          65575      3 134685556  chr3.s_134685556   A   T  0.267258      507               5                0.372129                    0.372129                   0.392998              38.0  Zm00001d041714     gene_body                    0
agri_aa_oil__Headingdate         189965     10  56708916  chr10.s_56708916   T   G  0.409270      507               5                0.371675                    0.371675                   0.388228              20.0  Zm00001d024211       nearest                16642
agri_aa_oil__Headingdate          80795      4  11761937   chr4.s_11761937   T   G  0.425049      507               5                0.371112                    0.371112                   0.385517              30.0  Zm00001d048991       nearest                19937
agri_aa_oil__Headingdate         160408      8  83975765   chr8.s_83975765   G   C  0.081854      507               5                0.360776                    0.360776                   0.401851              69.0  Zm00001d009824     gene_body                    0
agri_aa_oil__Headingdate         160579      8  88479938   chr8.s_88479938   C   G  0.059172      507               5                0.360164                    0.360164                   0.413158              68.0  Zm00001d009902       nearest                58645
agri_aa_oil__Headingdate         159596      8  68445120   chr8.s_68445120   A   G  0.368836      507               5                0.359443                    0.359443                   0.377511              65.0  Zm00001d009513     gene_body                    0
agri_aa_oil__Headingdate          77213      3 224388792  chr3.s_224388792   C   T  0.210059      507               5               -0.358334                    0.358334                   0.395352             116.0  Zm00001d044291     gene_body                    0
agri_aa_oil__Headingdate         160442      8  84948982   chr8.s_84948982   A   T  0.086785      507               5                0.357458                    0.357458                   0.386062              66.0  Zm00001d009848     gene_body                    0
agri_aa_oil__Headingdate          81698      4  20260380   chr4.s_20260380   C   T  0.149901      507               5                0.357117                    0.357117                   0.371761              52.0  Zm00001d049201       nearest                40097
agri_aa_oil__Headingdate          95289      4 223588780  chr4.s_223588780   T   C  0.142012      507               5                0.357000                    0.357000                   0.402640              70.0  Zm00001d053273     gene_body                    0
agri_aa_oil__Headingdate         123145      6   1745044    chr6.s_1745044   G   A  0.346154      507               5                0.355940                    0.355940                   0.370174              75.0  Zm00001d035012       nearest                11991
agri_aa_oil__Headingdate          54838      2 233610015  chr2.s_233610015   G   C  0.431953      507               5                0.355179                    0.355179                   0.376726              70.0  Zm00001d007514      promoter                    0
agri_aa_oil__Headingdate         119006      5 208266055  chr5.s_208266055   T   C  0.483235      507               5               -0.355053                    0.355053                   0.372727              53.0  Zm00001d017834     gene_body                    0
agri_aa_oil__Headingdate          74431      3 208853350  chr3.s_208853350   T   C  0.256410      507               5                0.353606                    0.353606                   0.374017              51.0  Zm00001d043743    cis_window                 1928
agri_aa_oil__Headingdate         174640      9  23152997   chr9.s_23152997   C   A  0.394477      507               5                0.351524                    0.351524                   0.363276              98.0  Zm00001d045463     gene_body                    0
agri_aa_oil__Headingdate          35591      2  12652822   chr2.s_12652822   C   T  0.203156      507               5                0.349699                    0.349699                   0.361803              76.0  Zm00001d002440     gene_body                    0
agri_aa_oil__Headingdate         160409      8  83977684   chr8.s_83977684   A   C  0.082840      507               5                0.349361                    0.349361                   0.382043             158.0  Zm00001d009824      promoter                    0
agri_aa_oil__Headingdate           8844      1  57695792   chr1.s_57695792   G   A  0.460552      507               5                0.343549                    0.343549                   0.361803             119.0  Zm00001d029095     gene_body                    0
```

## Top Gene Candidates

```text
                   trait nearest_gene_id gene_relation  variants  max_selected_seeds  mean_abs_train_correlation  min_distance_to_gene_bp
agri_aa_oil__Headingdate  Zm00001d012865     gene_body         3                   5                    0.368988                        0
agri_aa_oil__Headingdate  Zm00001d009873     gene_body         2                   5                    0.398929                        0
agri_aa_oil__Headingdate  Zm00001d041714     gene_body         2                   5                    0.373127                        0
agri_aa_oil__Headingdate  Zm00001d048603     gene_body         1                   5                    0.424929                        0
agri_aa_oil__Headingdate  Zm00001d009872    cis_window         1                   5                    0.402306                     2628
agri_aa_oil__Headingdate  Zm00001d009860      promoter         1                   5                    0.398145                        0
agri_aa_oil__Headingdate  Zm00001d011774     gene_body         1                   5                    0.393153                        0
agri_aa_oil__Headingdate  Zm00001d009859     gene_body         1                   5                    0.386113                        0
agri_aa_oil__Headingdate  Zm00001d009871       nearest         1                   5                    0.384981                    60404
agri_aa_oil__Headingdate  Zm00001d025103     gene_body         1                   5                    0.382770                        0
agri_aa_oil__Headingdate  Zm00001d044119     gene_body         1                   5                    0.376418                        0
agri_aa_oil__Headingdate  Zm00001d024211       nearest         1                   5                    0.371675                    16642
agri_aa_oil__Headingdate  Zm00001d048991       nearest         1                   5                    0.371112                    19937
agri_aa_oil__Headingdate  Zm00001d009824     gene_body         1                   5                    0.360776                        0
agri_aa_oil__Headingdate  Zm00001d009902       nearest         1                   5                    0.360164                    58645
agri_aa_oil__Headingdate  Zm00001d009513     gene_body         1                   5                    0.359443                        0
agri_aa_oil__Headingdate  Zm00001d044291     gene_body         1                   5                    0.358334                        0
agri_aa_oil__Headingdate  Zm00001d009848     gene_body         1                   5                    0.357458                        0
agri_aa_oil__Headingdate  Zm00001d049201       nearest         1                   5                    0.357117                    40097
agri_aa_oil__Headingdate  Zm00001d053273     gene_body         1                   5                    0.357000                        0
agri_aa_oil__Headingdate  Zm00001d035012       nearest         1                   5                    0.355940                    11991
agri_aa_oil__Headingdate  Zm00001d007514      promoter         1                   5                    0.355179                        0
agri_aa_oil__Headingdate  Zm00001d017834     gene_body         1                   5                    0.355053                        0
agri_aa_oil__Headingdate  Zm00001d043743    cis_window         1                   5                    0.353606                     1928
agri_aa_oil__Headingdate  Zm00001d045463     gene_body         1                   5                    0.351524                        0
agri_aa_oil__Headingdate  Zm00001d002440     gene_body         1                   5                    0.349699                        0
agri_aa_oil__Headingdate  Zm00001d009824      promoter         1                   5                    0.349361                        0
agri_aa_oil__Headingdate  Zm00001d029095     gene_body         1                   5                    0.343549                        0
agri_aa_oil__Headingdate  Zm00001d024910    cis_window         1                   4                    0.384846                      435
agri_aa_oil__Headingdate  Zm00001d026585     gene_body         1                   4                    0.383357                        0
```

## Interpretation

- This is an exploratory attribution screen, not a formal GWAS.
- Correlations are computed only on train splits for each seed and then aggregated, reducing direct test-set leakage.
- Stable SNP/gene candidates should be treated as hypotheses for later validation with stricter association models or external biological evidence.
- Summary: 750 SNP-trait candidates were retained across 15 traits; 674 SNPs were selected in all 5 seeds and 745 in at least 4 seeds.
- Gene mapping summary: 488 candidates fall in gene body, 59 in promoter, 147 in 10kb cis-window, and 56 are nearest-gene mappings outside the 10kb window.
- Next stricter analysis should add LD clumping, population covariate residualization/permutation, and gene annotation before making biological claims.

## Outputs

- `results/v0_1_baseline/genotype_attribution_snp_summary.tsv`
- `results/v0_1_baseline/genotype_attribution_gene_summary.tsv`
