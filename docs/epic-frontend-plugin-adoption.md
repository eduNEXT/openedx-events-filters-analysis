# Epic: Track Frontend Plugin Framework Adoption

## Problem

This repository measures adoption of the Open edX backend plugin APIs (`openedx-events`, `openedx-filters`) but has no equivalent coverage for the **frontend plugin framework** (`@openedx/frontend-plugin-framework`). Frontend plugin slots are a major extension archetype — operators and developers use them to inject custom UI into MFEs without forking — and their adoption is currently invisible to this analysis.

## Goal

Add adoption tracking for the Open edX frontend plugin framework so the repository provides a complete picture of plugin API success across backend and frontend layers.

## Adoption Signals to Search

Search GitHub for these terms in JavaScript/TypeScript files:

- `@openedx/frontend-plugin-framework` — package dependency (strongest signal)
- `PluginSlot` — JSX component used to define or consume a slot
- `Plugin` — base component for custom plugin implementations
- `PLUGIN_OPERATIONS` — configuration key used to register plugins

Scope: JS/TS files (`.js`, `.jsx`, `.ts`, `.tsx`, `package.json`) outside the `openedx/frontend-plugin-framework` source repo itself.

## Deliverables

1. `adoption_search_fe_plugins_code.py` — GitHub code search for frontend plugin signals, following the same pattern as `adoption_search_code.py` (deduplicate by commit SHA, exclude source repo).
2. `adoption_search_fe_plugins_prs.py` — GitHub PR search for frontend plugin signals, following `adoption_search_prs.py`.
3. `adoption_search_fe_plugins_per_org_prs.py` — org-level aggregation, following `adoption_search_per_org_prs.py`.
4. Update `Makefile` to include the new scripts in the `reports` target.
5. Update the GitHub Actions workflow to capture frontend plugin results.

## Reference

- Source repo: [openedx/frontend-plugin-framework](https://github.com/openedx/frontend-plugin-framework)
- Slot inventory (supply side): [openedx-plugin-slots-browser](https://arunmozhi.in/openedx-plugin-slots-browser/) — useful for cross-referencing which slots have the most consumer adoption
