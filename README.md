# Open edX Events and Filters Data Analysis

This repository contains scripts for generating data on the usage of Open edX events and filters by leveraging the GitHub API. The data and results obtained from these scripts are intended for use in a presentation at the Open edX Conference 2024.

## Table of Contents
- [Introduction](#introduction)
- [Requirements](#requirements)
- [Installation](#installation)
- [Scripts](#scripts)
  - [fetch_events_data.py](#fetch_events_datapy)
  - [analyze_filters_usage.py](#analyze_filters_usagepy)
- [Results](#results)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction
This project aims to provide insights into the usage of Open edX events and filters by querying data from the GitHub API. The scripts in this repository fetch and analyze this data, generating results that can be used to understand trends, usage patterns, and more.

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

### fetch_events_data.py
This script fetches data on the usage of Open edX events from GitHub repositories.

#### Usage
```bash
python fetch_events_data.py --token YOUR_GITHUB_API_TOKEN --output events_data.json
