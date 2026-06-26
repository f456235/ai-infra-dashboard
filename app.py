import pandas as pd
import streamlit as st

from src.charts import revenue_line_chart, valuation_scatter_chart
from src.data_loader import (
    load_ai_infra_events,
    load_companies,
    load_estimates,
    load_financial_metrics,
    load_theme_exposure,
    load_valuation_metrics,
)


st.set_page_config(
    page_title="AI Infrastructure Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
)


def company_name_map(companies: pd.DataFrame) -> dict[str, str]:
    return dict(zip(companies["company_id"], companies["company_name"]))


def add_company_names(data: pd.DataFrame, companies: pd.DataFrame) -> pd.DataFrame:
    names = company_name_map(companies)
    data = data.copy()
    data["company_name"] = data["company_id"].map(names)
    return data


def company_filter(label: str, companies: pd.DataFrame) -> list[str]:
    names = ["All"] + companies["company_name"].sort_values().tolist()
    selected = st.selectbox(label, names)
    if selected == "All":
        return companies["company_id"].tolist()
    return companies.loc[companies["company_name"] == selected, "company_id"].tolist()


def period_filter(data: pd.DataFrame, column: str = "period") -> list[str]:
    periods = sorted(data[column].dropna().unique(), reverse=True)
    selected = st.multiselect("Period", periods, default=periods)
    return selected


def render_overview(
    companies: pd.DataFrame,
    financials: pd.DataFrame,
    events: pd.DataFrame,
    theme_exposure: pd.DataFrame,
) -> None:
    st.title("AI Infrastructure Dashboard")
    st.caption("Local research dashboard for AI infrastructure investment tracking.")

    latest_period = financials["period"].max()
    latest_financials = financials[financials["period"] == latest_period]
    high_importance_events = events[events["importance"].str.lower() == "high"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tracked companies", f"{len(companies):,}")
    col2.metric("Tracked themes", f"{theme_exposure['theme'].nunique():,}")
    col3.metric("Latest revenue", f"${latest_financials['revenue_usd_m'].sum():,.0f}M")
    col4.metric("High-importance events", f"{len(high_importance_events):,}")

    left, right = st.columns([2, 1])
    with left:
        st.subheader("Companies by AI infrastructure category")
        grouped = (
            companies.groupby("ai_infra_category")["company_id"]
            .count()
            .reset_index(name="company_count")
            .sort_values("company_count", ascending=False)
        )
        st.dataframe(grouped, use_container_width=True, hide_index=True)

        st.subheader(f"Latest financial metrics ({latest_period})")
        summary = add_company_names(latest_financials, companies)
        st.dataframe(
            summary[
                [
                    "company_name",
                    "revenue_usd_m",
                    "revenue_yoy_pct",
                    "gross_margin_pct",
                    "operating_margin_pct",
                    "eps",
                    "eps_yoy_pct",
                    "free_cash_flow_usd_m",
                ]
            ].sort_values("revenue_usd_m", ascending=False),
            use_container_width=True,
            hide_index=True,
        )

    with right:
        st.subheader("Recent high-importance events")
        recent_events = add_company_names(high_importance_events, companies).head(6)
        for _, event in recent_events.iterrows():
            st.write(f"**{event['date'].date()} | {event['company_name']}**")
            st.write(event["event_title"])
            st.caption(f"Impact: {event['thesis_impact']}")


def render_companies(companies: pd.DataFrame) -> None:
    st.title("Companies")

    country = st.multiselect(
        "Country",
        sorted(companies["country"].unique()),
        default=sorted(companies["country"].unique()),
    )
    sector = st.multiselect(
        "Sector",
        sorted(companies["sector"].unique()),
        default=sorted(companies["sector"].unique()),
    )
    category = st.multiselect(
        "AI infrastructure category",
        sorted(companies["ai_infra_category"].unique()),
        default=sorted(companies["ai_infra_category"].unique()),
    )

    filtered = companies[
        companies["country"].isin(country)
        & companies["sector"].isin(sector)
        & companies["ai_infra_category"].isin(category)
    ]
    st.dataframe(filtered, use_container_width=True, hide_index=True)


def render_financial_metrics(companies: pd.DataFrame, financials: pd.DataFrame) -> None:
    st.title("Financial Metrics")

    selected_company_ids = company_filter("Company", companies)
    selected_periods = period_filter(financials)
    filtered = financials[
        financials["company_id"].isin(selected_company_ids)
        & financials["period"].isin(selected_periods)
    ]
    filtered = add_company_names(filtered, companies)

    st.plotly_chart(revenue_line_chart(filtered), use_container_width=True)
    st.dataframe(
        filtered[
            [
                "period",
                "company_name",
                "revenue_usd_m",
                "revenue_yoy_pct",
                "eps",
                "eps_yoy_pct",
                "gross_margin_pct",
                "operating_margin_pct",
                "capex_usd_m",
                "free_cash_flow_usd_m",
                "inventory_usd_m",
            ]
        ].sort_values(["period", "company_name"], ascending=[False, True]),
        use_container_width=True,
        hide_index=True,
    )


def render_valuation(companies: pd.DataFrame, valuations: pd.DataFrame) -> None:
    st.title("Valuation")

    selected_company_ids = company_filter("Company", companies)
    filtered = valuations[valuations["company_id"].isin(selected_company_ids)]
    filtered = add_company_names(filtered, companies)

    st.plotly_chart(valuation_scatter_chart(filtered), use_container_width=True)
    st.subheader("Valuation table sorted by forward PE")
    st.dataframe(
        filtered[
            [
                "date",
                "company_name",
                "price",
                "market_cap_usd_m",
                "trailing_pe",
                "forward_pe",
                "price_to_sales",
                "ev_to_ebitda",
            ]
        ].sort_values("forward_pe"),
        use_container_width=True,
        hide_index=True,
    )


def render_estimates(companies: pd.DataFrame, estimates: pd.DataFrame) -> None:
    st.title("Estimates")

    selected_company_ids = company_filter("Company", companies)
    selected_periods = period_filter(estimates)
    filtered = estimates[
        estimates["company_id"].isin(selected_company_ids)
        & estimates["period"].isin(selected_periods)
    ]
    filtered = add_company_names(filtered, companies)

    st.dataframe(
        filtered[
            [
                "period",
                "company_name",
                "estimated_revenue_usd_m",
                "estimated_eps",
                "estimated_revenue_yoy_pct",
                "estimated_eps_yoy_pct",
                "analyst_count",
                "revision_direction",
            ]
        ].sort_values(["period", "company_name"], ascending=[False, True]),
        use_container_width=True,
        hide_index=True,
    )


def render_events(companies: pd.DataFrame, events: pd.DataFrame) -> None:
    st.title("Events")

    selected_company_ids = company_filter("Company", companies)
    category = st.multiselect(
        "Category",
        sorted(events["category"].unique()),
        default=sorted(events["category"].unique()),
    )
    importance = st.multiselect(
        "Importance",
        sorted(events["importance"].unique()),
        default=sorted(events["importance"].unique()),
    )
    thesis_impact = st.multiselect(
        "Thesis impact",
        sorted(events["thesis_impact"].unique()),
        default=sorted(events["thesis_impact"].unique()),
    )

    filtered = events[
        events["company_id"].isin(selected_company_ids)
        & events["category"].isin(category)
        & events["importance"].isin(importance)
        & events["thesis_impact"].isin(thesis_impact)
    ]
    filtered = add_company_names(filtered, companies)

    for _, event in filtered.sort_values("date", ascending=False).iterrows():
        st.subheader(event["event_title"])
        st.caption(
            f"{event['date'].date()} | {event['company_name']} | "
            f"{event['category']} | {event['importance']} | {event['thesis_impact']}"
        )
        st.write(event["summary"])
        if pd.notna(event["source_url"]) and event["source_url"]:
            st.markdown(f"[Source]({event['source_url']})")


def render_theme_exposure(
    companies: pd.DataFrame, theme_exposure: pd.DataFrame
) -> None:
    st.title("Theme Exposure")

    theme = st.multiselect(
        "Theme",
        sorted(theme_exposure["theme"].unique()),
        default=sorted(theme_exposure["theme"].unique()),
    )
    exposure_level = st.multiselect(
        "Exposure level",
        sorted(theme_exposure["exposure_level"].unique()),
        default=sorted(theme_exposure["exposure_level"].unique()),
    )

    filtered = theme_exposure[
        theme_exposure["theme"].isin(theme)
        & theme_exposure["exposure_level"].isin(exposure_level)
    ]
    filtered = add_company_names(filtered, companies)
    st.dataframe(
        filtered[
            ["theme", "company_name", "exposure_level", "notes"]
        ].sort_values(["theme", "company_name"]),
        use_container_width=True,
        hide_index=True,
    )


def main() -> None:
    companies = load_companies()
    financials = load_financial_metrics()
    valuations = load_valuation_metrics()
    estimates = load_estimates()
    events = load_ai_infra_events()
    theme_exposure = load_theme_exposure()

    st.sidebar.title("AI Infrastructure")
    page = st.sidebar.radio(
        "Navigate",
        [
            "Overview",
            "Companies",
            "Financial Metrics",
            "Valuation",
            "Estimates",
            "Events",
            "Theme Exposure",
        ],
        label_visibility="collapsed",
    )

    if page == "Overview":
        render_overview(companies, financials, events, theme_exposure)
    elif page == "Companies":
        render_companies(companies)
    elif page == "Financial Metrics":
        render_financial_metrics(companies, financials)
    elif page == "Valuation":
        render_valuation(companies, valuations)
    elif page == "Estimates":
        render_estimates(companies, estimates)
    elif page == "Events":
        render_events(companies, events)
    else:
        render_theme_exposure(companies, theme_exposure)


if __name__ == "__main__":
    main()
