# AI Infrastructure Dashboard

A local Streamlit MVP for tracking AI infrastructure companies, financial
metrics, valuation, market expectations, industry events, and theme exposure.

This app uses CSV files only. It does not include APIs, crawlers, databases, or
automated updates.

## Features

- Overview with company count, theme count, recent high-importance events,
  category grouping, and latest financial metrics.
- Companies page with country, sector, and AI infrastructure category filters.
- Financial Metrics page with company and period filters plus a revenue chart.
- Valuation page with company filter, valuation chart, and table sorted by
  forward PE.
- Estimates page with company and period filters.
- Events page with company, category, importance, and thesis impact filters.
- Theme Exposure page with theme and exposure-level filters.
- Watchlist page with priority and current-position filters.

## Project Structure

```text
ai-infra-dashboard/
├── app.py
├── README.md
├── spec.md
├── requirements.txt
├── data/
│   ├── companies.csv
│   ├── financial_metrics.csv
│   ├── valuation_metrics.csv
│   ├── estimates.csv
│   ├── ai_infra_events.csv
│   ├── theme_exposure.csv
│   └── watchlist.csv
└── src/
    ├── data_loader.py
    └── charts.py
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## Data Files

The app reads these files from `data/`:

- `companies.csv`
- `financial_metrics.csv`
- `valuation_metrics.csv`
- `estimates.csv`
- `ai_infra_events.csv`
- `theme_exposure.csv`
- `watchlist.csv`

Required columns are validated in `src/data_loader.py`. If a required file or
column is missing, the app displays a clear Streamlit error message.

## Extending

- Add companies to `data/companies.csv`.
- Add new quarterly financial rows to `data/financial_metrics.csv`.
- Add valuation snapshots to `data/valuation_metrics.csv`.
- Add estimate periods to `data/estimates.csv`.
- Add thesis events to `data/ai_infra_events.csv`.
- Add or adjust theme mappings in `data/theme_exposure.csv`.
- Add watchlist notes to `data/watchlist.csv`.
- Add reusable charts in `src/charts.py`.
