# ZEAMAP second batch download check

检查日期：2026-06-04

## 结论

- 第二批 manifest 目标文件数：2126
- 本地缺失文件数：0
- 本地 0 字节文件数：0
- md5 复核：2118 OK，0 BAD
- VCF gzip 完整性：OK
- VCF samples：507
- VCF variants：1186632
- VCF 与第一阶段 accession index 交集：507
- `genotype + population + 任一 phenotype/metabolome` 强配对 accession：461
- `genotype + population + metabolite`：320
- `genotype + population + agri/AA/Oil`：459
- `genotype + population + 两类 phenotype/metabolome`：318
- 任一 DNA methylation 文件覆盖 accession：263
- `genotype + population + phenotype/metabolome + 任一 methylation`：236

## 输出文件

- `data/metadata/zeamap_second_batch_modality_summary.tsv`
- `data/metadata/zeamap_second_batch_sample_overlap.tsv`
- `data/metadata/zeamap_vcf_sample_overlap.tsv`

## Modality 文件汇总

| modality | files | nonempty_files | md5_ok | md5_bad |
|---|---:|---:|---:|---:|
| variation | 2 | 2 |  |  |
| mCG_regions | 527 | 527 | 526 | 0 |
| mCHG_regions | 527 | 527 | 526 | 0 |
| mCHH_regions | 527 | 527 | 526 | 0 |
| methylC_sites | 527 | 527 | 526 | 0 |
| chromatin_accessibility | 5 | 5 | 4 | 0 |
| chromatin_interaction | 11 | 11 | 10 | 0 |

## VCF 说明

- 文件：`variation/AMP_SNP_anno.vcf.gz`
- 索引：`variation/AMP_SNP_anno.vcf.gz.tbi`
- VCF header reference: `/public/home/stgui/work/ref/Zea_mays.AGPv4.dna.toplevel.fa`
- VEP annotation assembly: `B73 RefGen_v4`
- `bcftools/tabix` 可读取该 VCF 和索引。
- 当前有 warning：`.tbi` 文件 mtime 比 `.vcf.gz` 旧。这通常来自下载/拷贝时间戳，不代表索引不可用；tabix region query 已成功返回记录。若后续工具严格检查 mtime，可重新生成 index。

## Epigenome 样本覆盖

| methylation modality | samples |
|---|---:|
| mCG regions | 263 |
| mCHG regions | 263 |
| mCHH regions | 263 |
| methylC sites | 263 |
| union | 263 |

Chromatin accessibility 当前文件：

- `MNase_root_heavy.bw`
- `MNase_root_light.bw`
- `MNase_shoot_heavy.bw`
- `MNase_shoot_light.bw`

Chromatin interaction 当前文件数：6。文件名显示为 B73 H3K4me3/RNAPII interaction tracks，不是 AMP accession panel。

## 下一步

1. 用 `data/metadata/zeamap_second_batch_sample_overlap.tsv` 选择 461 个 `genotype + population + phenotype/metabolome` 强配对 accession。
2. 优先把 mCG/mCHG/mCHH region-level bedGraph 聚合到 gene/promoter/cis-window；region files 体量小，适合先做。
3. site-level methylC 文件体量约 99G，先抽样验证 parser 和聚合策略，再全量批处理。
4. Chromatin accessibility 和 interaction 目前更适合作为 B73 reference regulatory prior，不应当直接当作 AMP accession-level paired modality。
