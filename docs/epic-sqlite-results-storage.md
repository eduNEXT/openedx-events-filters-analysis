# Epic: Store Results in SQLite for Historical Tracking

## Problem

Results are currently written to flat text files and overwritten on each run. There is no way to track adoption trends over time, compare runs, or answer questions like "how many new repos adopted openedx-events since last month?"

## Goal

Persist every run's results to a SQLite database so that adoption counts can be trended over time and individual runs can be compared.

## Schema

### `runs` table
Each execution of any script is a single run.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `run_at` | TIMESTAMP | UTC timestamp of execution |
| `script` | TEXT | e.g. `adoption_search_code`, `adoption_search_fe_plugins_code` |
| `signal_type` | TEXT | `backend` or `frontend` |
| `notes` | TEXT | Optional free-text label (e.g. "pre-conference run", "May 2026 monthly") |

### `results` table
One row per unique repository hit per run (code search scripts).

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `run_id` | INTEGER FK | References `runs.id` |
| `repository` | TEXT | Repo name (e.g. `openedx-webhooks`) |
| `repository_url` | TEXT | Full GitHub URL |
| `is_fork` | BOOLEAN | Whether the repository is a fork — allows filtering fork inflation from counts |
| `file_path` | TEXT | Path of the matching file within the repo |
| `file_url` | TEXT | Full GitHub blob URL |
| `signal` | TEXT | The search string that produced this hit |
| `phase` | TEXT | `package` or `source` — which search phase found it |

### `pr_results` table
One row per unique PR hit per run (PR search scripts).

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `run_id` | INTEGER FK | References `runs.id` |
| `pr_url` | TEXT | Full GitHub PR URL |
| `title` | TEXT | PR title |
| `repository` | TEXT | Repo name extracted from PR URL |
| `repository_url` | TEXT | Full GitHub repo URL |
| `is_fork` | BOOLEAN | Whether the repository is a fork |
| `author` | TEXT | GitHub username of the PR author |
| `organization` | TEXT | Organization of the PR author (NULL for non-org scripts) |

## CLI Interface

Scripts should gain a `--db` flag that writes results to the database in addition to (not instead of) stdout, so existing usage and CI pipelines are unaffected.

```bash
python adoption_search_code.py $TOKEN --db results/adoption.db
python adoption_search_fe_plugins_code.py $TOKEN --db results/adoption.db
python adoption_search_prs.py $TOKEN --db results/adoption.db
python adoption_search_fe_plugins_prs.py $TOKEN --db results/adoption.db
python adoption_search_per_org_prs.py $TOKEN --db results/adoption.db
python adoption_search_fe_plugins_per_org_prs.py $TOKEN --db results/adoption.db
```

An optional `--notes` flag labels the run:
```bash
python adoption_search_code.py $TOKEN --db results/adoption.db --notes "May 2026 monthly"
```

## Querying

No dedicated query tool is required for the first version — direct SQLite queries are sufficient:

```sql
-- Adoption count per script over time, excluding forks
SELECT r.run_at, r.script, COUNT(DISTINCT res.repository) AS repos
FROM runs r JOIN results res ON res.run_id = r.id
WHERE res.is_fork = 0
GROUP BY r.id ORDER BY r.run_at;

-- Repos that are new since the previous run (excluding forks)
SELECT res.repository
FROM results res
JOIN runs r ON res.run_id = r.id
WHERE r.script = 'adoption_search_code'
  AND r.id = (SELECT MAX(id) FROM runs WHERE script = 'adoption_search_code')
  AND res.is_fork = 0
  AND res.repository NOT IN (
    SELECT repository FROM results res2
    JOIN runs r2 ON res2.run_id = r2.id
    WHERE r2.script = 'adoption_search_code'
      AND res2.is_fork = 0
      AND r2.id = (SELECT MAX(id) FROM runs WHERE script = 'adoption_search_code'
                   AND id < (SELECT MAX(id) FROM runs WHERE script = 'adoption_search_code'))
  );

-- PR count by organization over time
SELECT r.run_at, pr.organization, COUNT(*) AS prs
FROM runs r JOIN pr_results pr ON pr.run_id = r.id
WHERE pr.is_fork = 0
GROUP BY r.id, pr.organization ORDER BY r.run_at, prs DESC;
```

## Deliverables

1. `db.py` — shared module with `init_db(path)`, `record_run(...)`, `record_results(...)`, and `record_pr_results(...)` functions using Python's built-in `sqlite3`.
2. Update all six scripts (`adoption_search_code.py`, `adoption_search_fe_plugins_code.py`, `adoption_search_prs.py`, `adoption_search_fe_plugins_prs.py`, `adoption_search_per_org_prs.py`, `adoption_search_fe_plugins_per_org_prs.py`) with `--db` and `--notes` flags.
3. Fetch the `fork` field from the GitHub API for each repository and populate `is_fork` — the repository search response already includes this field, so no extra API calls are needed.
4. Update `Makefile` to pass a `DB` variable through to scripts: `make reports TOKEN=... DB=results/adoption.db`.
5. Commit `results/adoption.db` to the `reports` branch alongside the text files so the historical record travels with the repo.
