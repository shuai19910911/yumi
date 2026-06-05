# ZEAMAP v0.1 Stage 5.31 Figure Approval And Release Readiness Report

日期：2026-06-06

## Verdict

`FIGURE_RELEASE_PIPELINE_READY_AUTHOR_APPROVAL_REQUIRED`

## What changed

- Created a structured Figure 1-3 final visual approval template.
- Added a release notes draft for the GitHub submission release.
- Added Zenodo metadata draft with creator fields left as `TO_COMPLETE`.
- Updated final gate without creating a tag, GitHub release or archive DOI.

## Gate summary

- pass/human_required/fail: 8/4/0

## Figure approval audit

| figure | status | evidence |
| --- | --- | --- |
| Figure 1 | human_required | Missing: pdf_opened; svg_opened; png_opened; panel_labels_correct; text_readable_at_journal_size; no_label_overlap; legend_matches_figure; color_accessibility_checked; approver; approval_date; final_status=pass |
| Figure 2 | human_required | Missing: pdf_opened; svg_opened; png_opened; panel_labels_correct; text_readable_at_journal_size; no_label_overlap; legend_matches_figure; color_accessibility_checked; approver; approval_date; final_status=pass |
| Figure 3 | human_required | Missing: pdf_opened; svg_opened; png_opened; panel_labels_correct; text_readable_at_journal_size; no_label_overlap; legend_matches_figure; color_accessibility_checked; approver; approval_date; final_status=pass |

## Release readiness audit

| check | status | evidence | git_head_at_audit |
| --- | --- | --- | --- |
| release_notes_draft | pass | Release notes draft exists for tag zeamap-oil-v0.1-submission. | c08e90f |
| zenodo_metadata_draft | human_required | Zenodo metadata draft exists but creator fields require real author metadata. | c08e90f |
| clean_git_status_before_release | human_required | Working tree currently has uncommitted changes for Stage 5.31. | c08e90f |
| tag_not_created_by_agent | human_required | Do not create tag zeamap-oil-v0.1-submission until final author-approved manuscript is committed. | c08e90f |
| archive_pid_not_available | human_required | A DOI/PID can only be created after an author-approved release/archive step. | c08e90f |
