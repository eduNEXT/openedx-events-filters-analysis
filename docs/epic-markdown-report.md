# Epic: Markdown Summary Report

## Problem

Results are stored in a SQLite database and raw text files, but there is no human-readable summary suitable for sharing with stakeholders or including in a presentation. Interpreting trends requires writing ad-hoc SQL queries.

## Goal

Generate a single Markdown file after each run that summarizes adoption across all plugin archetypes, highlights changes since the previous run, and is ready to commit to the `reports` branch alongside the database.

## Report Structure

### Header
- Report generation timestamp (UTC)
- Run IDs included in this report
- Notes label if provided

### 1. Adoption Snapshot (current run, non-fork repos only)

| Archetype | Repos | vs. Previous Run |
|---|---|---|
| Backend (events & filters) | N | +X / -Y |
| Frontend (plugin framework) | N | +X / -Y |
| **Total** | N | +X / -Y |

### 2. New Repos Since Last Run

Two subsections — Backend and Frontend — each listing repos that appear in the current run but not the previous run for that script. Forks excluded.

### 3. Adoption by Organization (PR signal)

Top organizations by PR count from the most recent `per_org_prs` run, backend and frontend side by side. Forks excluded.

### 4. Signal Breakdown (current run)

Which specific signals are driving hits, ranked by unique repo count. Helps identify which API primitives are most widely adopted.

| Signal | Repos | Phase |
|---|---|---|
| openedx-events | N | package |
| OpenEdxPublicSignal | N | source |
| ... | | |

### 5. Trend Chart (text-based)

ASCII bar chart of total adopting repos (non-fork) per run, per archetype, over all recorded runs. Example:

```
Backend adoption over time
2026-01  ████████████████  32
2026-02  ██████████████████  36
2026-03  ████████████████████  41

Frontend adoption over time
2026-01  ████████  16
2026-02  ██████████  20
```

## CLI Interface

```bash
python generate_report.py --db results/adoption.db
python generate_report.py --db results/adoption.db --out results/report.md
```

- `--db` path to the SQLite database (required)
- `--out` output path (default: stdout)

The script reads exclusively from the DB — it does not re-query GitHub.

## Deliverables

1. `generate_report.py` — standalone script that reads from the DB and writes Markdown.
2. Update `Makefile` with a `report` target that runs after `reports`:
   ```makefile
   report:
       @cd scripts && python generate_report.py --db $(DB) --out results/report.md
   ```
3. Update the GitHub Actions workflow to run `make report` after `make reports` and include `results/report.md` in the `reports` branch commit.

## Constraints

- No new dependencies — use only Python stdlib (`sqlite3`, `argparse`, `datetime`).
- The report must be readable as raw Markdown in a GitHub file view (no HTML, no embedded images).
- Sections that have no data (e.g. no previous run to compare against) should say so explicitly rather than error or be omitted.
