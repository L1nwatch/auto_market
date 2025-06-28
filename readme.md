[En](./readme.md) | [中](./readme_zh.md)

# Auto Market

[![Run auto_lotto_main.py Daily](https://github.com/L1nwatch/auto_market/actions/workflows/daily-run-main.yml/badge.svg)](https://github.com/L1nwatch/auto_market/actions/workflows/daily-run-main.yml)
[![pages-build-deployment](https://github.com/L1nwatch/auto_market/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/L1nwatch/auto_market/actions/workflows/pages/pages-build-deployment)
[![Run Tests](https://github.com/L1nwatch/auto_market/actions/workflows/run-tests.yml/badge.svg)](https://github.com/L1nwatch/auto_market/actions/workflows/run-tests.yml)


## Repository Overview

This repository hosts two automation projects:

1. **Auto Lotto** - predicts numbers for the Lotto 6/49 game using language models, buys tickets, and checks results.
2. **Auto Stock Trading** - demonstrates a simple stock trading strategy and logging (currently paused).

Key directories and files:
- `auto_lotto_main.py` orchestrates the lotto workflow.
- `utils/` contains helpers for predictions, scraping results, purchasing tickets, and database access.
- `auto_stock/` holds the trading scripts and its README.
- `docs/` publishes lotto outcomes via GitHub Pages.
- `github-runner.Dockerfile` builds the self-hosted runner used by GitHub Actions.

## Project1: Auto Lotto

This project predicts numbers for the Lotto 6/49 lottery, automatically purchases tickets, and verifies winning statuses.
It is specifically built around Loto-Québec's version of Lotto 6/49: the historical draws are scraped from the Loto‑Québec
website and tickets are bought through Loto‑Québec's online platform. Other Canadian lottery systems are not supported.
The available predictors include:
1. **LLM** - a language model suggests numbers based on recent draws.
2. **Random** - generates purely random combinations.
3. **Frequency-weighted** - analyzes historical draws to select the most common numbers. Simulations are available for 1–5 years of history.
4. **Least frequency-weighted** - selects numbers that appear the least often in historical draws.

The purchased tickets and their results are displayed on GitHub Pages.
[https://l1nwatch.github.io/auto_market/](https://l1nwatch.github.io/auto_market/)

You can also view the frequency-weighted simulation results here:
[1 Year](https://l1nwatch.github.io/auto_market/freq_simulation_1_year.html) |
[2 Years](https://l1nwatch.github.io/auto_market/freq_simulation_2_year.html) |
[3 Years](https://l1nwatch.github.io/auto_market/freq_simulation_3_year.html) |
[4 Years](https://l1nwatch.github.io/auto_market/freq_simulation_4_year.html) |
[5 Years](https://l1nwatch.github.io/auto_market/freq_simulation_5_year.html) |
[All Years](https://l1nwatch.github.io/auto_market/freq_simulation_all_years.html)

You can view the least frequency-weighted simulation results here:
[1 Year](https://l1nwatch.github.io/auto_market/least_freq_simulation_1_year.html) |
[2 Years](https://l1nwatch.github.io/auto_market/least_freq_simulation_2_year.html) |
[3 Years](https://l1nwatch.github.io/auto_market/least_freq_simulation_3_year.html) |
[4 Years](https://l1nwatch.github.io/auto_market/least_freq_simulation_4_year.html) |
[5 Years](https://l1nwatch.github.io/auto_market/least_freq_simulation_5_year.html) |
[All Years](https://l1nwatch.github.io/auto_market/least_freq_simulation_all_years.html)


### Design Overview

```mermaid
flowchart TD
    %% Root 1: Daily Run
    A[Daily Run - GitHub Actions] --> B[Self-Hosted Runner]
    B --> C[Setup Environment and Execute main.py Script]
    C --> F[Fetch Historical Data]
    F --> G[Predict Next Lotto Numbers]
    G --> D[Auto Purchase Tickets]
    I --> H[Update SQLite Database]
    F --> I[Check Win Status]
    D --> H
    H --> J[Generate Results HTML]
    J --> Q[Push and Publish on GitHub Pages]


    %% Additional Connections
    %% H --> K  
    %% Database shared between Daily Run and Web Display
    %% Failure Handling
    C --> R[Retry on Failure]   
    
    %% Root 2: Web Displaying
    Z[Web Displaying]
    Z --> M[View Results on GitHub Pages]

    %% Styling
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style Z fill:#f9f,stroke:#333,stroke-width:2px
    style H fill:#faa,stroke:#333,stroke-width:2px
    style J fill:#bfb,stroke:#333,stroke-width:2px
    style Q fill:#bfb,stroke:#333,stroke-width:2px
    style M fill:#bfb,stroke:#333,stroke-width:2px
```

### How to run daily

The execution schedule is defined in
[`.github/workflows/daily-run-main.yml`](.github/workflows/daily-run-main.yml).
This GitHub Actions workflow runs `auto_lotto_main.py` every day at **14:00 UTC**
(9:00 AM Montreal time).

1. **Create a self-hosted runner**

   Build and start the runner container with your credentials:

```shell
docker build -f github-runner.Dockerfile \
  --build-arg OPENAI_API_KEY="$OPENAI_API_KEY" \
  --build-arg RUNNER_TOKEN="$RUNNER_TOKEN" \
  --build-arg LOTTO_USER="$LOTTO_USER" \
  --build-arg LOTTO_PASSWORD="$LOTTO_PASSWORD" \
  -t auto-lotto-github-runner .

docker run -d auto-lotto-github-runner
```

2. **Workflow execution**

   Once the runner is online, GitHub automatically triggers the workflow daily.
   You can also manually start it from the Actions tab using the
   `workflow_dispatch` option.

## Project2: Auto Stock Trading

An experimental bot that interacts with the Tonghuashun trading system to buy
recently dipped stocks and automatically place sell orders for profit or loss.
The scripts are paused but remain available for reference.

- [Chinese documentation](./auto_stock/README.md)
- [English documentation](./auto_stock/README_en.md)
