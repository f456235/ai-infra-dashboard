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

COMPANY_EXPOSURE_COLUMNS = [
    "exposure_id",
    "company_id",
    "thesis_id",
    "exposure_level",
    "exposure_reason",
    "evidence_id",
    "last_reviewed",
]

WATCHLIST_COLUMNS = [
    "company_id",
    "priority",
    "current_position",
    "thesis",
    "risk",
    "next_check",
]

INDUSTRY_THESIS_COLUMNS = [
    "thesis_id",
    "industry_layer",
    "thesis_category",
    "thesis_title",
    "thesis_summary",
    "key_drivers",
    "risks",
    "status",
    "conviction",
    "last_reviewed",
]

TECHNOLOGY_COLUMNS = [
    "technology_id",
    "technology_name",
    "technology_category",
    "description",
    "related_thesis_ids",
    "maturity_stage",
    "key_companies",
    "last_reviewed",
]

PRODUCT_COLUMNS = [
    "product_id",
    "product_name",
    "primary_company_id",
    "product_category",
    "description",
    "launch_status",
    "related_technology_ids",
    "related_thesis_ids",
    "last_reviewed",
]

RELATIONSHIP_COLUMNS = [
    "relationship_id",
    "source_id",
    "source_type",
    "relationship_type",
    "target_id",
    "target_type",
    "reason",
    "confidence",
    "evidence_id",
    "last_updated",
]

EVIDENCE_COLUMNS = [
    "evidence_id",
    "date",
    "fact_text",
    "evidence_title",
    "evidence_summary",
    "source_type",
    "source_url",
    "related_event_id",
    "related_company_id",
    "related_thesis_id",
    "evidence_direction",
    "confidence",
    "notes",
]

ENTITY_RELATIONSHIP_COLUMNS = [
    "relationship_id",
    "source_entity",
    "source_type",
    "relationship_type",
    "target_entity",
    "target_type",
    "notes",
    "importance",
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

    try:
        data = pd.read_csv(path)
    except Exception as error:
        st.error(f"Could not read `data/{filename}`: {error}")
        st.stop()

    validate_columns(data, required_columns, filename)

    for column in date_columns or []:
        parsed_dates = pd.to_datetime(data[column], errors="coerce")
        invalid_dates = (
            parsed_dates.isna()
            & data[column].notna()
            & (data[column].astype(str).str.strip() != "")
        )
        if invalid_dates.any():
            st.error(f"`data/{filename}` has invalid dates in `{column}`.")
            st.stop()
        data[column] = parsed_dates

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


def load_company_exposure() -> pd.DataFrame:
    data = load_csv("company_exposure.csv", COMPANY_EXPOSURE_COLUMNS, ["last_reviewed"])
    return data.sort_values(["company_id", "thesis_id"])


def load_watchlist() -> pd.DataFrame:
    data = load_csv("watchlist.csv", WATCHLIST_COLUMNS, ["next_check"])
    return data.sort_values(["priority", "next_check"])


def load_industry_theses() -> pd.DataFrame:
    data = load_csv("industry_theses.csv", INDUSTRY_THESIS_COLUMNS, ["last_reviewed"])
    return data.sort_values(["industry_layer", "thesis_category", "thesis_id"])


def load_entity_relationships() -> pd.DataFrame:
    data = load_csv("entity_relationships.csv", ENTITY_RELATIONSHIP_COLUMNS)
    return data.sort_values(["source_entity", "relationship_type", "target_entity"])


def load_technologies() -> pd.DataFrame:
    data = load_csv("technologies.csv", TECHNOLOGY_COLUMNS, ["last_reviewed"])
    return data.sort_values(["technology_category", "technology_name"])


def load_products() -> pd.DataFrame:
    data = load_csv("products.csv", PRODUCT_COLUMNS, ["last_reviewed"])
    return data.sort_values(["product_category", "product_name"])


def load_relationships() -> pd.DataFrame:
    data = load_csv("relationships.csv", RELATIONSHIP_COLUMNS, ["last_updated"])
    return data.sort_values(["source_type", "source_id", "relationship_type"])


def load_evidence() -> pd.DataFrame:
    data = load_csv("evidence.csv", EVIDENCE_COLUMNS, ["date"])
    return data.sort_values("date", ascending=False)
