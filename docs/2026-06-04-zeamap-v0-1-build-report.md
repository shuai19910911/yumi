# ZEAMAP v0.1 processed dataset build report

构建日期：2026-06-04

## 输入

- 第一批 phenotype/population metadata
- 第二批 `AMP_SNP_anno.vcf.gz`
- 第二批 methylation coverage metadata

## 输出目录

```text
data/processed/v0_1
```

## 样本

- v0.1 accession 数：461
- 选择标准：`genotype + population + 任一 phenotype/metabolome`
- 带任一 DNA methylation 的 v0.1 accession 数：236

## phenotype/population

- population rows：461
- phenotype rows：461
- metabolite trait columns：247
- agri/AA/Oil trait columns：71
- total phenotype trait columns：318

## genotype

- VCF filter：biallelic SNP, `MAF >= 0.05`, `NS >= 450`
- filtered variants before thinning：799423
- thinning stride：4
- kept variants：199856
- genotype samples：461
- dosage matrix shape：[199856, 461]
- missing genotype entries encoded as `-1`：0
- dosage encoding：`0`, `1`, `2` ALT allele dosage; `-1` missing

## files

- `accessions.tsv`
- `modality_mask.tsv`
- `population.tsv`
- `population.parquet`
- `phenotype.tsv`
- `phenotype.parquet`
- `phenotype_trait_descriptors.tsv`
- `genotype_samples.tsv`
- `genotype_variants.tsv`
- `genotype_dosage_int8.npz`
- `manifest.tsv`

## validation

- `accessions.tsv` rows：461
- `modality_mask.tsv` rows：461
- `population.tsv` rows：461
- `phenotype.tsv` rows：461
- `genotype_samples.tsv` rows：461
- `genotype_variants.tsv` rows：199856
- `genotype_dosage_int8.npz` shape：`[199856, 461]`
- sample set matches accessions：true
- npz sample order matches `genotype_samples.tsv`：true
- variant count matches matrix rows：true
- sample count matches matrix columns：true
- dosage min/max：0/2

## Notes

- `data/processed/` is ignored by git because it contains local training matrices.
- Expression files from the first batch remain reference/tissue expression priors, not accession-level paired expression.
- Chromatin accessibility and interaction are not included as paired accession-level v0.1 modalities.
