# AI Infrastructure Dashboard MVP Spec

## Goal

Build a local Streamlit dashboard for tracking AI infrastructure companies, financial metrics, valuation, market expectations, industry events, and a personal watchlist.

The dashboard is for personal research and investment tracking. It should help answer:

* Which AI infrastructure themes are improving?
* Which companies have improving fundamentals?
* Which companies are expensive or cheap relative to expectations?
* What recent events may affect the investment thesis?

## Stack

* Python 3.11+
* Streamlit
* Pandas
* Plotly
* CSV files as the data source

## Scope

This is an MVP.

Do not implement:

* External APIs
* Web crawlers
* Databases
* Login system
* Automated data updates

## Data Files

Create a `data/` folder with the following CSV files.

### 1. companies.csv

Static company information only.

Columns:

* company_id
* ticker
* company_name
* exchange
* country
* sector
* ai_infra_category
* website
* description

### 2. financial_metrics.csv

Quarterly financial data.

Columns:

* company_id
* period
* revenue_usd_m
* revenue_yoy_pct
* gross_margin_pct
* operating_margin_pct
* net_income_usd_m
* eps
* eps_yoy_pct
* capex_usd_m
* free_cash_flow_usd_m
* inventory_usd_m

### 3. valuation_metrics.csv

Valuation data by date.

Columns:

* company_id
* date
* price
* market_cap_usd_m
* trailing_pe
* forward_pe
* price_to_sales
* ev_to_ebitda

### 4. estimates.csv

Market consensus estimates.

Columns:

* company_id
* period
* estimated_revenue_usd_m
* estimated_eps
* estimated_revenue_yoy_pct
* estimated_eps_yoy_pct
* analyst_count
* revision_direction

### 5. ai_infra_events.csv

News, earnings call notes, pricing updates, supply chain events, and thesis-related events.

Columns:

* event_id
* date
* company_id
* category
* event_title
* summary
* source_url
* importance
* thesis_impact

### 6. theme_exposure.csv

Company exposure to AI infrastructure themes.

Columns:

* company_id
* theme
* exposure_level
* notes

Valid themes include:

* CSP CapEx
* AI Accelerator
* ASIC
* HBM
* DRAM
* NAND
* Foundry
* Advanced Packaging
* Power
* Cooling
* PCB/CCL
* BBU/UPS
* Networking
* Industrial PC

### 7. watchlist.csv

Personal tracking notes for companies under active review.

Columns:

* company_id
* priority
* current_position
* thesis
* risk
* next_check

## Pages

### 1. Overview

Show:

* Total number of tracked companies
* Number of tracked themes
* Recent high-importance events
* Companies grouped by AI infrastructure category
* Simple summary of latest financial metrics

### 2. Companies

Show a table of companies.

Requirements:

* Filter by country
* Filter by sector
* Filter by AI infrastructure category

### 3. Financial Metrics

Show quarterly financial metrics.

Requirements:

* Filter by company
* Filter by period
* Show revenue, revenue YoY, EPS, EPS YoY, gross margin, operating margin, capex, free cash flow, and inventory
* Include at least one Plotly line chart for revenue over time

### 4. Valuation

Show valuation metrics.

Requirements:

* Filter by company
* Show price, market cap, trailing PE, forward PE, price-to-sales, EV/EBITDA
* Include a table sorted by forward PE

### 5. Estimates

Show analyst estimates.

Requirements:

* Filter by company
* Filter by period
* Show estimated revenue, estimated EPS, estimated YoY growth, analyst count, and revision direction

### 6. Events

Show AI infrastructure events.

Requirements:

* Filter by company
* Filter by category
* Filter by importance
* Filter by thesis impact
* Show source URL as a clickable link if possible

### 7. Theme Exposure

Show company exposure by AI infrastructure theme.

Requirements:

* Filter by theme
* Filter by exposure level
* Show which companies are exposed to each theme

### 8. Watchlist

Show personal watchlist notes.

Requirements:

* Join company_id with company_name for display
* Filter by priority
* Filter by current_position
* Show thesis, risk, and next check date

### 9. Company Detail

Show single-company research details.

Requirements:

* Select one company by company_name
* Show company profile from companies.csv
* Show watchlist notes from watchlist.csv if available
* Show latest financial metrics from financial_metrics.csv
* Show latest valuation metrics from valuation_metrics.csv
* Show estimates from estimates.csv
* Show theme exposure from theme_exposure.csv
* Show recent events from ai_infra_events.csv
* Do not replace the Financial Metrics, Valuation, Estimates, or Events pages
* Keep Companies as a browse/filter page without clickable company navigation for now

### 10. Better Charts and Company Comparison

Improve the dashboard from static tables into a comparison and trend analysis tool.

Requirements:

* Add multi-company selection where appropriate
* Use Plotly line charts
* Reuse financial_metrics.csv and valuation_metrics.csv
* Keep existing tables
* Do not remove existing pages
* Show revenue trend by default
* Show revenue YoY trend by default
* Show EPS trend by default
* Show gross margin trend by default
* Show free cash flow trend by default
* Show forward PE trend by default
* Offer operating margin, CapEx, inventory, and price-to-sales as optional charts
* On Financial Metrics, compare multiple companies over time
* On Valuation, compare forward PE by default and price-to-sales optionally when multiple dates exist
* On Company Detail, show simple trend charts for the selected company
* Sort period-based charts chronologically, not alphabetically

Chart intent:

* Revenue trend: demand and business scale
* Revenue YoY: growth acceleration or deceleration
* EPS trend: profitability to shareholders
* Gross margin trend: pricing power and product mix
* Free cash flow trend: ability to fund growth
* Forward PE trend: valuation relative to future earnings

Chart design:

* Show a short caption above each chart explaining what question it helps answer
* Move CapEx, operating margin, inventory, and price-to-sales into optional chart selectors
* Keep the implementation simple

## Code Requirements

* Keep code simple and beginner-friendly
* Avoid unnecessary classes
* Use functions where possible
* Create reusable data loading functions
* Validate that required CSV columns exist
* Display a clear Streamlit error message if a CSV file is missing or columns are missing
* App should run with:

```bash
streamlit run app.py
```

## Project Structure

```text
ai-infra-dashboard/
├── app.py
├── README.md
├── SPEC.md
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

## Design Decisions

### Decision 1

`companies.csv` should only store static company information.

Reason:

Financial data such as EPS, revenue, PE, and forward PE changes over time, so it belongs in separate time-based metric tables.

### Decision 2

Use CSV files for the MVP.

Reason:

The first version should focus on data model, dashboard structure, and usability. APIs, crawlers, and databases can be added later.

### Decision 3

Do not include GPU utilization, GPU capacity, or estimated power usage in the MVP.

Reason:

These data points are difficult to obtain consistently across companies and may reduce data quality.
