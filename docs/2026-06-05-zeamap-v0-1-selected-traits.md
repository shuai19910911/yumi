# ZEAMAP v0.1 selected traits

日期：2026-06-05

## Selection rule

从 `results/v0_1_baseline/top_predictable_traits.tsv` 和 `trait_qc.tsv` 中筛选：

- `genotype_pca_population_ridge` test Pearson >= 0.3
- `genotype_pca_population_ridge` test R2 > 0.0
- 相比 `population_ridge` 至少满足 Pearson gain >= 0.02 或 R2 gain > 0.0
- trait 通过 baseline QC

## Result

- baseline evaluated traits：317
- selected traits：130
- high-priority traits：11
- medium-priority traits：28
- watch traits：91

## Family summary

```text
trait_family  selected_traits  median_pearson  max_pearson  median_r2   max_r2  median_pearson_gain_vs_population
  metabolite               76        0.431271     0.691350   0.108227 0.338155                           0.130208
         oil               29        0.597021     0.924294   0.337875 0.827152                           0.296521
   agronomic               16        0.481782     0.749839   0.215855 0.509565                           0.122205
  amino_acid                9        0.370541     0.524026   0.121627 0.272153                           0.176169
```

## Top 10 selected traits

```text
                     trait trait_family  pearson__genotype_pca_population_ridge  r2__genotype_pca_population_ridge  pearson__population_ridge  r2__population_ridge  pearson_gain_vs_population  r2_gain_vs_population  total_non_missing  test_non_missing
      agri_aa_oil__Oil_OIL          oil                                0.924294                           0.827152                   0.508632              0.244081                    0.415662               0.583071                440                67
    agri_aa_oil__Oil_C18_2          oil                                0.894542                           0.793232                   0.599769              0.325117                    0.294772               0.468116                440                67
    agri_aa_oil__Oil_C18_1          oil                                0.877590                           0.767657                   0.386022              0.131408                    0.491568               0.636250                440                67
    agri_aa_oil__Oil_C20_0          oil                                0.848665                           0.695268                   0.510189              0.218698                    0.338476               0.476570                440                67
    agri_aa_oil__Oil_C20_1          oil                                0.837581                           0.700775                   0.486769              0.227952                    0.350812               0.472822                440                67
    agri_aa_oil__Oil_C16_0          oil                                0.826132                           0.677789                   0.431937              0.181975                    0.394195               0.495814                440                67
    agri_aa_oil__Oil_C18_0          oil                                0.812624                           0.577828                   0.530134              0.227727                    0.282490               0.350101                440                67
 agri_aa_oil__kernellength    agronomic                                0.749839                           0.509565                   0.619107              0.379386                    0.130732               0.130179                458                70
    agri_aa_oil__Oil_C16_1          oil                                0.744593                           0.525729                   0.237233              0.030288                    0.507360               0.495441                440                67
agri_aa_oil__Oil_C200_C220          oil                                0.743427                           0.528411                   0.446905              0.172289                    0.296521               0.356122                440                67
```

## Interpretation

- 第一版 selected traits 主要由 oil、agronomic、metabolite 和 amino acid traits 构成。
- Oil traits 的最高 Pearson 和 R2 最强，适合作为下一阶段模型 sanity-check 和主评估集合。
- Metabolite traits 数量较多，但整体信号弱于 oil traits，后续需要 multi-seed robustness 再确认。
- 这些 selected traits 应作为阶段 3.2 多随机种子稳健性验证的输入，不建议直接把全部 318 个 trait 都作为后续主目标。

## Outputs

- `results/v0_1_baseline/selected_traits.tsv`
- `results/v0_1_baseline/selected_trait_family_summary.tsv`
- `results/v0_1_baseline/selected_trait_tier_summary.tsv`
