# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This project uses the GitHub REST and GraphQL APIs to analyze adoption of [openedx-events](https://github.com/openedx/openedx-events) and [openedx-filters](https://github.com/openedx/openedx-filters) across the Open edX ecosystem. Results are used for conference presentations and community research.

## Setup

```bash
pip install -r requirements.txt
```

All scripts require a GitHub personal access token (fine-grained PAT). The CI workflow reads it from the `GH_FINE_GRAINED_PAT` GitHub Actions secret.

## Running Scripts

All scripts live in `scripts/` and write to stdout. Run from the `scripts/` directory:

```bash
# Code adoption search (searches GitHub code index)
python adoption_search_code.py YOUR_TOKEN > results/adoption_search_code.txt

# PR adoption search (searches PRs mentioning adoption signals)
python adoption_search_prs.py YOUR_TOKEN > results/adoption_search_prs.txt

# PR search grouped by contributor organization
python adoption_search_per_org_prs.py YOUR_TOKEN > results/adoption_search_per_org_prs.txt

# All PRs to a specific repo (REST)
python contributions.py YOUR_TOKEN ORG_NAME REPO_NAME > results/<repo>/contributions.txt

# PRs grouped by contributor organization
python contributions_per_org.py YOUR_TOKEN ORG_NAME REPO_NAME
python contributions_per_org_agg.py YOUR_TOKEN ORG_NAME REPO_NAME  # aggregated across orgs

# Unique contributors for a repo
python unique_contributors.py YOUR_TOKEN ORG_NAME REPO_NAME
```

Via Makefile (runs `adoption_search_code.py` only):

```bash
make reports TOKEN=YOUR_TOKEN
```

## Automated Reports

`.github/workflows/reports.yml` runs `make reports` on the 1st of each month (UTC midnight) and on manual dispatch. Results are force-pushed to the `reports` branch.

## Architecture

**Data flow:**

1. Scripts query the GitHub API (REST search for code/PRs, GraphQL for contributions).
2. Results are deduplicated — by commit SHA for code results, by PR URL for PR results.
3. Source repos (`openedx-events`, `openedx-filters`) are excluded from adoption counts.
4. For org-level scripts, each contributor's GitHub profile is fetched to extract their listed organization.
5. Output is plain text to stdout.

**The 7 adoption signals** searched across all scripts:
- `openedx_events`, `openedx-events`, `OpenEdxPublicSignal`
- `openedx_filters`, `openedx-filters`, `OpenEdxPublicFilter`
- `PipelineStep`

**Results directory:** `scripts/results/` (committed snapshots) and a top-level `results/` directory (local working output).
