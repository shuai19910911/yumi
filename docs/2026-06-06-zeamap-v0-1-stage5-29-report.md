# ZEAMAP v0.1 Stage 5.29 Format Compliance And Export Report

日期：2026-06-06

## Verdict

`DOCX_HTML_EXPORT_READY_AUTHOR_FIELDS_REMAIN`

## What changed

- Created a clean submission manuscript Markdown file with internal stage notes removed.
- Exported DOCX and standalone HTML preview through pandoc in the `yumi` environment.
- Checked The Plant Genome route formatting elements: Core Ideas, abstract, author-year references, data/code statements, figure/table legends and claim boundaries.
- Updated final gate with export and format-compliance rows.

## Gate summary

- pass/human_required/fail: 6/4/0
- Remaining human-only blockers are unchanged: author metadata, funding/COI/acknowledgements, final figure approval and repository release PID.

## Export artifacts

| artifact | format | status | size_bytes |
| --- | --- | --- | --- |
| docs/2026-06-06-zeamap-v0-1-stage5-29-submission-clean-manuscript.docx | docx | pass | 21591 |
| docs/2026-06-06-zeamap-v0-1-stage5-29-submission-clean-manuscript.html | html | pass | 33268 |
| PDF | pdf | not_required_for_current_gate | NA |

## Format checks

| check | status | evidence |
| --- | --- | --- |
| title_present | pass | Clean manuscript begins with the manuscript title. |
| core_ideas_present | pass | Core Ideas section retained for The Plant Genome route. |
| abstract_present | pass | Abstract and Keywords sections present. |
| main_text_word_count | pass | Main text word count estimate: 1643. |
| references_author_year_style | pass | Reference entries detected: 18; no numbered entries expected. |
| required_statements_present | pass | Data, code, competing-interest and ethics statements checked. |
| figure_legends_present | pass | Figure 1-3 legends present. |
| table_legends_present | pass | Main and supplementary table legends present. |
| author_metadata_placeholders | human_required | Author, funding and acknowledgement placeholders intentionally retained for author completion. |
| claim_boundary | pass | Candidate-interval and no-causal-claim boundaries checked. |
