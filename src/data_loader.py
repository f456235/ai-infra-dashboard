from pathlib import Path

import pandas as pd
import streamlit as st


DATA_DIR = Path(__file__).resolve().parent.parent / "data"

COMPANY_COLUMNS = [
    "company_id",
    "ticker",
    "company_name",
    "exchange",
    "country",
    "sector",
    "ai_infra_category",
    "website",
    "description",
]

FINANCIAL_COLUMNS = [
    "company_id",
    "period",
    "revenue_usd_m",
    "revenue_yoy_pct",
    "gross_margin_pct",
    "operating_margin_pct",
    "net_income_usd_m",
    "eps",
    "eps_yoy_pct",
    "capex_usd_m",
    "free_cash_flow_usd_m",
    "inventory_usd_m",
]

VALUATION_COLUMNS = [
    "company_id",
    "date",
    "price",
    "market_cap_usd_m",
    "trailing_pe",
    "forward_pe",
    "price_to_sales",
    "ev_to_ebitda",
]

ESTIMATE_COLUMNS = [
    "company_id",
    "period",
    "estimated_revenue_usd_m",
    "estimated_eps",
    "estimated_revenue_yoy_pct",
    "estimated_eps_yoy_pct",
    "analyst_count",
    "revision_direction",
]

EVENT_COLUMNS = [
    "event_id",
    "date",
    "company_id",
    "category",
    "event_title",
    "summary",
    "source_url",
    "importance",
    "thesis_impact",
]

THEME_EXPOSURE_COLUMNS = [
    "company_id",
    "theme",
    "exposure_level",
    "notes",
]


def validate_columns(data: pd.DataFrame, required_columns: list[str], filename: str) -> None:
    missing_columns = [column for column in required_columns if column not in data.columns]
    if missing_columns:
        st.error(
            f"`data/{filename}` is missing required columns: "
            f"{', '.join(missing_columns)}"
        )
        st.stop()


@st.cache_data
def load_csv(
    filename: str,
    required_columns: list[str],
    date_columns: list[str] | None = None,
) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.exists():
        st.error(f"Missing required data file: `data/{filename}`")
        st.stop()

    data = pd.read_csv(path, parse_dates=date_columns or [])
    validate_columns(data, required_columns, filename)
    return data


def load_companies() -> pd.DataFrame:
    return load_csv("companies.csv", COMPANY_COLUMNS).sort_values("company_name")


def load_financial_metrics() -> pd.DataFrame:
    data = load_csv("financial_metrics.csv", FINANCIAL_COLUMNS)
    return data.sort_values(["company_id", "period"])


def load_valuation_metrics() -> pd.DataFrame:
    data = load_csv("valuation_metrics.csv", VALUATION_COLUMNS, ["date"])
    return data.sort_values(["company_id", "date"])


def load_estimates() -> pd.DataFrame:
    data = load_csv("estimates.csv", ESTIMATE_COLUMNS)
    return data.sort_values(["company_id", "period"])


def load_ai_infra_events() -> pd.DataFrame:
    data = load_csv("ai_infra_events.csv", EVENT_COLUMNS, ["date"])
    return data.sort_values("date", ascending=False)


def load_theme_exposure() -> pd.DataFrame:
    data = load_csv("theme_exposure.csv", THEME_EXPOSURE_COLUMNS)
    return data.sort_values(["theme", "company_id"])
