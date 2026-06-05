# ZEAMAP v0.1 Single Human-Input Form Guide

日期：2026-06-06

## 为什么新增这个文件

投稿最后卡住的不是计算结果，而是人工确认信息：作者顺序、单位、ORCID、基金、利益冲突、审稿人、最终图件人工检查和 release 确认。之前这些信息分散在多个模板里，容易漏填或互相不一致。

现在只需要优先填写：

- `docs/2026-06-06-zeamap-v0-1-single-human-input-form.tsv`

## 怎么填

每一行是一个需要确认的字段：

- `section`：信息类型，例如 `author`、`affiliation`、`reviewer`、`figure_check`。
- `record_id`：同一类信息中的记录编号或名称。
- `field`：具体字段名。
- `value`：真正要填写的值。
- `required`：是否投稿前必填。
- `guidance`：填写提示。

把 `value` 里的 `TO_COMPLETE`、`yes/no`、`pass/revise` 和方括号示例全部替换为真实值。不能确认的信息不要猜，留给通讯作者确认。

## 填完后做什么

运行：

```bash
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_17_single_human_input_pack.py --apply
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_15_preflight_validator.py
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_16_metadata_ingestion_dryrun.py
```

只有 Stage 5.15 显示 `READY_FOR_RELEASE_EXECUTION`，Stage 5.16 显示 `READY_TO_INSERT_METADATA`，才进入真实 tag/release/DOI 步骤。
