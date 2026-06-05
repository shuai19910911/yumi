# Stage 5.32 Post-Human-Input Command Checklist

日期：2026-06-06

Run this only after filling the Stage 5.30 and Stage 5.31 templates.

```bash
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_30_author_metadata_ingestion.py
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_31_figure_release_readiness.py
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_29_format_export_package.py
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_32_human_action_packet.py
git diff --check
git status --short
```

Expected before release:

- Stage 5.30 author/funding audit rows all `pass`.
- Stage 5.31 figure approval rows all `pass`.
- Final gate has no `fail` and no `human_required` except release PID if the archive DOI is intentionally created after journal upload.
- DOCX/HTML export is regenerated from the filled manuscript.
