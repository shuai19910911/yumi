# ZEAMAP v0.1 Stage 5.17 Single Human-Input Sync Report

日期：2026-06-06

## Verdict

`NOT_READY_HUMAN_FIELDS_REMAIN`

Mode: dry-run only; Stage 5.14 templates were not overwritten

## What This Adds

Stage 5.17 makes the submission-blocking human fields easier to handle. Instead of editing several files independently, the corresponding author can fill one table:

- `docs/2026-06-06-zeamap-v0-1-single-human-input-form.tsv`

After the table has no placeholders, rerun this script with `--apply` to synchronize the author, affiliation, reviewer, funding/COI and figure-check templates. Then rerun Stage 5.15 and Stage 5.16.

## Audit Summary

- Sections checked: 5
- Ready sections: 0
- Placeholder/bracket rows remaining: 62
- Blank required rows remaining: 0

## Next Command After Filling The Form

```bash
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_17_single_human_input_pack.py --apply
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_15_preflight_validator.py
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_16_metadata_ingestion_dryrun.py
```
