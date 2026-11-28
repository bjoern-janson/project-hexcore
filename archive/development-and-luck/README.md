# Development, law discovery and cumulative luck

Four exploratory experimental batches from 2026-11-28. The code and protocols retain their historical local identifiers; numbering in the conversation and original file headings need not match. Read the original documentation rather than inferring missing results from the labels.

| Batch | Entry point | Original protocol and outcome |
|---|---|---|
| Chemistry | [chemistry.py](hexcore_chemistry/chemistry.py), [followup.py](hexcore_chemistry/followup.py) | [README](hexcore_chemistry/README.md) |
| Development | [development.py](hexcore_development/development.py), [followup.py](hexcore_development/followup.py) | [README](hexcore_development/README.md), [main log](hexcore_development/run.log) |
| Law discovery | [law_discovery.py](hexcore_law_discovery/law_discovery.py), [ambiguity.py](hexcore_law_discovery/ambiguity.py) | [README](hexcore_law_discovery/README.md), [run log](hexcore_law_discovery/run.log), [audit log](hexcore_law_discovery/ambiguity.log) |
| Luck | [experiment.py](hexcore_luck/experiment.py), [followup.py](hexcore_luck/followup.py) | [README](hexcore_luck/README.md), [audit](hexcore_luck/audit.json) |

See [DEVELOPMENT_AND_LUCK.md](../../docs/DEVELOPMENT_AND_LUCK.md) for the cross-lineage interpretation and a proposed lifetime ecological experiment.

## Custody status

The four original ZIP files were available locally and passed ZIP integrity checks. They contain 34 non-directory members. 24 original members are committed byte-identically: 12 Markdown files, eight Python scripts, three execution logs, and one audit JSON. Nine other JSON result files, one further execution log and the four original ZIPs are preserved in the separately delivered completion bundle, but are **not in GitHub at this checkpoint**. The connector could read text attachments and write UTF-8 Git objects, but did not expose a direct local-archive transfer path. One attempted log transcription did not match its expected hash and was excluded rather than silently substituted.

[ORIGINALS-CUSTODY.txt](ORIGINALS-CUSTODY.txt) lists the exact Git blob SHA-1 for all 34 extracted members and four original ZIP files, indicating their import status. Hashes were computed from the original local bytes. The 24 committed files were checked against the repository's Git tree. The completion bundle contains all 38 originals, a SHA-256 and Git blob manifest, and a verification script for importing the remaining files into a local checkout. Status in this ledger is historical; verify the current tree after any later import.

The historical scripts were not rerun during this import. Reproduction may regenerate results; those new outputs should be kept apart from originals. Some follow-up scripts require preceding result files, so import the complete bundle or reproduce the preceding experiment in a separate working directory before running. No new license, independent scientific validation or new experimental claim is implied.
