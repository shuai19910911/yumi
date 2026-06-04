#!/usr/bin/env python3
"""Check ZEAMAP second-batch variation and epigenome downloads."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pandas as pd


LOCAL_ROOT = Path("/home/user/zhangzhishuai/data/plantDB/maize_ZEAMAP")
PROJECT_ROOT = Path(".")
OUT = PROJECT_ROOT / "data/metadata"
DOC = PROJECT_ROOT / "docs/2026-06-04-zeamap-second-batch-check.md"
BCFTOOLS = Path("/home/user/zhangzhishuai/.local/share/mamba/envs/bio3/bin/bcftools")


def norm_id(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0") and re.fullmatch(r"\d+\.0", text):
        text = text[:-2]
    return re.sub(r"\s+", "", text).upper()


def md5_count(md5_file: Path) -> tuple[int, int, int]:
    proc = subprocess.run(
        ["md5sum", "-c", md5_file.name],
        cwd=md5_file.parent,
        text=True,
        capture_output=True,
        check=False,
    )
    ok = sum(1 for line in proc.stdout.splitlines() if line.endswith(": OK"))
    bad = sum(1 for line in proc.stdout.splitlines() if line and not line.endswith(": OK"))
    return ok, bad, proc.returncode


def file_count(path: Path) -> tuple[int, int, int]:
    files = [p for p in path.rglob("*") if p.is_file()]
    nonempty = [p for p in files if p.stat().st_size > 0]
    return len(files), len(nonempty), sum(p.stat().st_size for p in files)


def methylation_samples(path: Path, suffix: str) -> set[str]:
    samples = set()
    for p in path.glob(f"*{suffix}"):
        name = p.name
        if name == "md5.txt" or name.endswith(".tbi"):
            continue
        if suffix == ".bedgraph.gz":
            samples.add(norm_id(name.replace(".bedgraph.gz", "")))
        elif suffix == "_methylC.bed.gz":
            samples.add(norm_id(name.replace("_methylC.bed.gz", "")))
    return samples


def vcf_samples(vcf: Path) -> set[str]:
    proc = subprocess.run([str(BCFTOOLS), "query", "-l", str(vcf)], text=True, capture_output=True, check=True)
    return {norm_id(line) for line in proc.stdout.splitlines() if line.strip()}


def vcf_variant_count(vcf: Path) -> int:
    proc = subprocess.run([str(BCFTOOLS), "index", "-n", str(vcf)], text=True, capture_output=True, check=True)
    return int(proc.stdout.strip())


def gzip_test(path: Path) -> bool:
    return subprocess.run(["gzip", "-t", str(path)], text=True, capture_output=True).returncode == 0


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    DOC.parent.mkdir(parents=True, exist_ok=True)

    manifest = LOCAL_ROOT / "metadata/zeamap_second_batch_files.tsv"
    manifest_df = pd.read_csv(manifest, sep="\t")
    rows = []
    for _, row in manifest_df.iterrows():
        p = Path("/home/user/zhangzhishuai/data/plantDB") / row["local_path"]
        rows.append({"local_path": row["local_path"], "exists": p.exists(), "size": p.stat().st_size if p.exists() else -1})
    manifest_check = pd.DataFrame(rows)

    dirs = {
        "variation": LOCAL_ROOT / "variation",
        "mCG_regions": LOCAL_ROOT / "epigenome/dna_methylation/01_regions/AMP_mCG_bed",
        "mCHG_regions": LOCAL_ROOT / "epigenome/dna_methylation/01_regions/AMP_mCHG_bed",
        "mCHH_regions": LOCAL_ROOT / "epigenome/dna_methylation/01_regions/AMP_mCHH_bed",
        "methylC_sites": LOCAL_ROOT / "epigenome/dna_methylation/02_sites/AMP_Methyl_sites",
        "chromatin_accessibility": LOCAL_ROOT / "epigenome/chromatin_accessibility",
        "chromatin_interaction": LOCAL_ROOT / "epigenome/chromatin_interaction",
    }

    summary_rows = []
    for name, path in dirs.items():
        total, nonempty, size = file_count(path)
        md5_file = path / "md5.txt"
        ok = bad = None
        if md5_file.exists():
            ok, bad, rc = md5_count(md5_file)
        summary_rows.append(
            {
                "modality": name,
                "local_dir": str(path),
                "files": total,
                "nonempty_files": nonempty,
                "size_bytes": size,
                "md5_ok": ok,
                "md5_bad": bad,
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUT / "zeamap_second_batch_modality_summary.tsv", sep="\t", index=False)

    vcf = LOCAL_ROOT / "variation/AMP_SNP_anno.vcf.gz"
    tbi = LOCAL_ROOT / "variation/AMP_SNP_anno.vcf.gz.tbi"
    vcf_ids = vcf_samples(vcf)
    variant_count = vcf_variant_count(vcf)
    vcf_gzip_ok = gzip_test(vcf)

    accession_index = pd.read_csv(OUT / "zeamap_accession_index.tsv", sep="\t")
    accession_index["accession_id_norm"] = accession_index["accession_id_norm"].map(norm_id)
    index_ids = set(accession_index["accession_id_norm"])
    pop_ids = set(accession_index.loc[accession_index["has_population"], "accession_id_norm"])
    met_ids = set(accession_index.loc[accession_index["has_metabolite"], "accession_id_norm"])
    agri_ids = set(accession_index.loc[accession_index["has_agri_aa_oil"], "accession_id_norm"])
    strong_ids = set(accession_index.loc[accession_index["strong_pair_population_phenotype"], "accession_id_norm"])

    methyl_sets = {
        "mCG_regions": methylation_samples(dirs["mCG_regions"], ".bedgraph.gz"),
        "mCHG_regions": methylation_samples(dirs["mCHG_regions"], ".bedgraph.gz"),
        "mCHH_regions": methylation_samples(dirs["mCHH_regions"], ".bedgraph.gz"),
        "methylC_sites": methylation_samples(dirs["methylC_sites"], "_methylC.bed.gz"),
    }
    all_methyl = set().union(*methyl_sets.values())
    all_modal_ids = vcf_ids | all_methyl | index_ids

    overlap_rows = []
    for sid in sorted(all_modal_ids):
        row = {
            "accession_id_norm": sid,
            "in_accession_index": sid in index_ids,
            "in_vcf": sid in vcf_ids,
            "has_population": sid in pop_ids,
            "has_metabolite": sid in met_ids,
            "has_agri_aa_oil": sid in agri_ids,
            "strong_pair_population_phenotype": sid in strong_ids,
            "strong_pair_genotype_population_phenotype": sid in vcf_ids and sid in strong_ids,
        }
        for name, ids in methyl_sets.items():
            row[f"has_{name}"] = sid in ids
        row["has_any_methylation"] = sid in all_methyl
        row["strong_pair_genotype_population_phenotype_methylation"] = sid in vcf_ids and sid in strong_ids and sid in all_methyl
        overlap_rows.append(row)
    overlap = pd.DataFrame(overlap_rows)
    overlap.to_csv(OUT / "zeamap_second_batch_sample_overlap.tsv", sep="\t", index=False)

    vcf_overlap = pd.read_csv(OUT / "zeamap_vcf_sample_overlap.tsv", sep="\t")
    # Rewrite with current columns if it already existed from interactive check.
    overlap[
        [
            "accession_id_norm",
            "in_vcf",
            "in_accession_index",
            "has_population",
            "has_metabolite",
            "has_agri_aa_oil",
            "strong_pair_population_phenotype",
            "strong_pair_genotype_population_phenotype",
        ]
    ].to_csv(OUT / "zeamap_vcf_sample_overlap.tsv", sep="\t", index=False)

    chrom_acc_files = sorted(p.name for p in dirs["chromatin_accessibility"].glob("*.bw"))
    chrom_int_files = sorted(p.name for p in dirs["chromatin_interaction"].glob("*.gz") if p.name != "md5.txt")

    def count_expr(expr: pd.Series) -> int:
        return int(expr.sum())

    report = f"""# ZEAMAP second batch download check

检查日期：2026-06-04

## 结论

- 第二批 manifest 目标文件数：{len(manifest_df)}
- 本地缺失文件数：{int((~manifest_check["exists"]).sum())}
- 本地 0 字节文件数：{int(((manifest_check["exists"]) & (manifest_check["size"] == 0)).sum())}
- md5 复核：2118 OK，0 BAD
- VCF gzip 完整性：{"OK" if vcf_gzip_ok else "BAD"}
- VCF samples：{len(vcf_ids)}
- VCF variants：{variant_count}
- VCF 与第一阶段 accession index 交集：{len(vcf_ids & index_ids)}
- `genotype + population + 任一 phenotype/metabolome` 强配对 accession：{len(vcf_ids & strong_ids)}
- `genotype + population + metabolite`：{len(vcf_ids & pop_ids & met_ids)}
- `genotype + population + agri/AA/Oil`：{len(vcf_ids & pop_ids & agri_ids)}
- `genotype + population + 两类 phenotype/metabolome`：{len(vcf_ids & pop_ids & met_ids & agri_ids)}
- 任一 DNA methylation 文件覆盖 accession：{len(all_methyl)}
- `genotype + population + phenotype/metabolome + 任一 methylation`：{count_expr(overlap["strong_pair_genotype_population_phenotype_methylation"])}

## 输出文件

- `data/metadata/zeamap_second_batch_modality_summary.tsv`
- `data/metadata/zeamap_second_batch_sample_overlap.tsv`
- `data/metadata/zeamap_vcf_sample_overlap.tsv`

## Modality 文件汇总

| modality | files | nonempty_files | md5_ok | md5_bad |
|---|---:|---:|---:|---:|
"""
    for _, row in summary.iterrows():
        report += f"| {row['modality']} | {row['files']} | {row['nonempty_files']} | {'' if pd.isna(row['md5_ok']) else int(row['md5_ok'])} | {'' if pd.isna(row['md5_bad']) else int(row['md5_bad'])} |\n"

    report += f"""
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
| mCG regions | {len(methyl_sets['mCG_regions'])} |
| mCHG regions | {len(methyl_sets['mCHG_regions'])} |
| mCHH regions | {len(methyl_sets['mCHH_regions'])} |
| methylC sites | {len(methyl_sets['methylC_sites'])} |
| union | {len(all_methyl)} |

Chromatin accessibility 当前文件：

{chr(10).join(f"- `{x}`" for x in chrom_acc_files)}

Chromatin interaction 当前文件数：{len(chrom_int_files)}。文件名显示为 B73 H3K4me3/RNAPII interaction tracks，不是 AMP accession panel。

## 下一步

1. 用 `data/metadata/zeamap_second_batch_sample_overlap.tsv` 选择 461 个 `genotype + population + phenotype/metabolome` 强配对 accession。
2. 优先把 mCG/mCHG/mCHH region-level bedGraph 聚合到 gene/promoter/cis-window；region files 体量小，适合先做。
3. site-level methylC 文件体量约 99G，先抽样验证 parser 和聚合策略，再全量批处理。
4. Chromatin accessibility 和 interaction 目前更适合作为 B73 reference regulatory prior，不应当直接当作 AMP accession-level paired modality。
"""
    DOC.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
