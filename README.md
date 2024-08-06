# Open edX Events and Filters data

This repository contains scripts for generating data on the usage of Open edX events and filters by leveraging the GitHub API. The data and results obtained from these scripts are intended for use in a presentation at the Open edX Conference 2024 and for future analysis.

These scripts were initially generated using ChatGPT 4.0 and were subsequently modified to meet specific project requirements.

## Table of Contents
- [Introduction](#introduction)
- [Requirements](#requirements)
- [Installation](#installation)
- [Scripts](#scripts)
  - [Adoption search by code](#adoption-search-by-code)
  - [Adoption search by pull requests](#adoption-search-by-pull-requests)
  - [Adoption search by pull requests per organization](#adoption-search-by-pull-requests-per-organization)
  - [All contributions](#all-contributions)
  - [All contributions per organization](#all-contributions-per-organization)
  - [All contributions per organization aggregated](#all-contributions-per-organization-aggregated)
  - [Unique contributors](#unique-contributors)
- [Results](#results)
- [Usage](#usage)

## Introduction
This project aims to provide insights into the usage of Open edX events and filters by querying data from the GitHub API. The scripts in this repository fetch github data, generating results that can be used to understand usage patterns and more.

## Requirements
- Python 3.8 or higher
- GitHub API token (for accessing the GitHub API)

## Installation
1. Clone this repository:
    ```bash
    git clone https://github.com/mariajgrimaldi/openedx-events-filters-analysis.git
    cd openedx-events-filters-analysis
    ```
2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

## Scripts

### Adoption search by code
This script fetches data on the adoption of Open edX events and filters from GitHub code ``search/code?q={query}+extension:py&page={page}``, by using these search terms:

| Search String | Significance |
| --- | --- |
| openedx_events | Indicates the use of event-driven architecture, allowing custom behaviors and integrations without modifying core code. |
| openedx_filters | Shows utilization of filter mechanisms, highlighting the platform's extensibility and customization capabilities. |
| openedx-events | Reflects the adoption of event-driven architecture similar to openedx_events. |
| openedx-filters | Similar to openedx_filters, indicating use of filter mechanisms for extending the platform. |
| OpenEdxPublicSignal | Suggests widespread use of signaling mechanisms for decoupling components and enhancing modularity. |
| PipelineStep | Indicates creation and integration of custom processing steps into workflows, enhancing flexibility and customization. |
| OpenEdxPublicFilter | Shows adoption of filters for modifying data flow, providing high levels of customization and control over data processing within the platform. |

#### Usage
```bash
python adoption_search_code.py YOUR_GITHUB_API_TOKEN > scripts/results/adoption_search_code.txt
```
### Adoption search by pull requests
This script fetches data on the adoption of Open edX events and filters from Github pull requests ``search/issues?q={query}&type=pr&page={page}``, by using the same search terms as in the previous script.

#### Usage
```bash
python adoption_search_prs.py YOUR_GITHUB_API_TOKEN > scripts/results/adoption_search_prs.txt
```

### Adoption search by pull requests per organization
This script fetches data on the adoption of Open edX events and filters from Github pull requests ``search/issues?q={query}&type=pr&page={page}``, by using the same search terms as in the previous script
and organizes them per the author's organization.

#### Usage
```bash
python adoption_search_per_org_prs.py YOUR_GITHUB_API_TOKEN > scripts/results/adoption_search_per_org_prs.txt
```

### All contributions 
This script fetches all pull requests made to a library by using Github's graphQL API, and returns a list of PRs URLs, descriptions and authors.

#### Usage
```bash
python contributions.py YOUR_GITHUB_API_TOKEN ORG_NAME REPO_NAME > scripts/results/<openex-events|openedx-filters>/contributions.txt
```

### All contributions per organization
This script fetches all pull requests made to a library by using Github's graphQL API, and returns a list of pull request URLs, descriptions and authors organized by the author's organization.

#### Usage
```bash
python contributions_per_org.py YOUR_GITHUB_API_TOKEN ORG_NAME REPO_NAME > scripts/results/<openex-events|openedx-filters>/contributions_per_org.txt
```

### All contributions per organization aggregated
This script fetches all pull requests made to a library by using Github's graphQL API. It returns a list of pull requests URLs, descriptions, and authors organized by the author's organization but aggregating them if the author belongs to more than one.

#### Usage
```bash
python contributions_per_org.py YOUR_GITHUB_API_TOKEN ORG_NAME REPO_NAME > scripts/results/<openex-events|openedx-filters>/contributions_per_org_agg.txt
```

### Unique contributors
This script generates a list of unique contributors for a library.

#### Usage
```bash
python unique_contributors.py YOUR_GITHUB_API_TOKEN ORG_NAME REPO_NAME > scripts/results/<openex-events|openedx-filters>/unique_contributors.txt
```

## Results

The results for each script, dating back to June 24, are in the ``script/results`` folder.
