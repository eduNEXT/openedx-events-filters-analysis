# Epic: Add GitLab Repository Coverage

## Problem

All current adoption searches target GitHub exclusively. A meaningful portion of the Open edX operator and integrator community hosts their extensions on GitLab (both gitlab.com and self-hosted instances). Excluding these repos understates true adoption and biases results toward GitHub-native organizations.

## Goal

Extend the adoption analysis to cover GitLab repositories, producing comparable adoption counts that can be combined with or reported alongside the existing GitHub results.

## Scope

- **gitlab.com** — public repositories searchable via the GitLab REST API.
- Self-hosted GitLab instances are out of scope for a first pass (require per-instance credentials and discovery).

## Signals to Search

Same set as GitHub:

**Backend:** `openedx_events`, `openedx-events`, `OpenEdxPublicSignal`, `openedx_filters`, `openedx-filters`, `OpenEdxPublicFilter`, `PipelineStep`

**Frontend (if the FE epic is completed first):** `@openedx/frontend-plugin-framework`, `PluginSlot`, `PLUGIN_OPERATIONS`

## GitLab API Notes

- Code search endpoint: `GET /search?scope=blobs&search=<term>` (requires authentication for rate limits)
- Auth: personal access token with `read_api` scope, passed as `PRIVATE-TOKEN` header
- Rate limit: 10 requests/second for authenticated users; include backoff
- Results include `project_id`, `path`, `ref` — use `project_id + path + ref` as deduplication key (analogous to commit SHA on GitHub)
- Exclude results from the source repos (`openedx-events`, `openedx-filters`) by project name

## Deliverables

1. `gitlab_adoption_search_code.py` — GitLab code search for all backend (and optionally frontend) signals, deduplicating by project+path+ref, excluding source repos.
2. `gitlab_adoption_search_prs.py` — GitLab merge request search for adoption signals (MR description/title search via `/search?scope=merge_requests`).
3. Update `Makefile` with a `gitlab-reports` target (separate token variable, e.g. `GITLAB_TOKEN`).
4. Update GitHub Actions workflow to accept a `GITLAB_PAT` secret and run GitLab scripts alongside the existing GitHub ones.

## Open Questions

- Should GitLab and GitHub counts be merged into unified totals, or reported separately?
- Are there known key organizations on GitLab (e.g. specific university or government deployments) that should be explicitly included?
