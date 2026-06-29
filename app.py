import pandas as pd
import streamlit as st

from src.charts import (
    capex_line_chart,
    eps_line_chart,
    forward_pe_line_chart,
    free_cash_flow_line_chart,
    gross_margin_line_chart,
    inventory_line_chart,
    operating_margin_line_chart,
    price_to_sales_line_chart,
    revenue_line_chart,
    revenue_yoy_line_chart,
    sort_by_period,
)
from src.data_loader import (
    load_ai_infra_events,
    load_company_exposure,
    load_companies,
    load_estimates,
    load_evidence,
    load_financial_metrics,
    load_industry_theses,
    load_products,
    load_relationships,
    load_research_actions,
    load_technologies,
    load_theme_exposure,
    load_valuation_metrics,
    load_watchlist,
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


def multi_company_filter(label: str, companies: pd.DataFrame) -> list[str]:
    company_names = companies["company_name"].sort_values().tolist()
    selected_names = st.multiselect(label, company_names, default=company_names)
    return companies[
        companies["company_name"].isin(selected_names)
    ]["company_id"].tolist()


def select_company(companies: pd.DataFrame) -> tuple[str, str]:
    company_names = companies["company_name"].sort_values().tolist()
    selected_name = st.selectbox("Company", company_names)
    selected_id = companies.loc[
        companies["company_name"] == selected_name, "company_id"
    ].iloc[0]
    return selected_id, selected_name


def period_filter(data: pd.DataFrame, column: str = "period") -> list[str]:
    periods = sort_by_period(
        data[[column]].drop_duplicates().assign(company_name=""),
        column,
    )[column].tolist()
    selected = st.multiselect("Period", periods, default=periods)
    return selected


def show_table_or_message(data: pd.DataFrame, message: str) -> None:
    if data.empty:
        st.info(message)
        return
    st.dataframe(data, use_container_width=True, hide_index=True)


def filter_values(data: pd.DataFrame, column: str) -> list[str]:
    return sorted(data[column].fillna("").astype(str).unique())


def sort_research_actions(actions: pd.DataFrame) -> pd.DataFrame:
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    status_order = {"Open": 0, "In Progress": 1, "Waiting": 2, "Done": 3, "Archived": 4}
    sorted_actions = actions.copy()
    sorted_actions["_priority_order"] = (
        sorted_actions["priority"].map(priority_order).fillna(99)
    )
    sorted_actions["_status_order"] = sorted_actions["status"].map(status_order).fillna(99)
    return sorted_actions.sort_values(
        ["_status_order", "_priority_order", "due_date"]
    ).drop(columns=["_priority_order", "_status_order"])


def split_ids(value) -> list[str]:
    if pd.isna(value) or value == "":
        return []
    return [item.strip() for item in str(value).split(";") if item.strip()]


def contains_id(value, target_id: str) -> bool:
    return target_id in split_ids(value)


def related_ids(
    relationships: pd.DataFrame,
    source_id: str,
    target_type: str,
) -> list[str]:
    matches = relationships[
        (relationships["source_id"] == source_id)
        & (relationships["target_type"] == target_type)
    ]
    return matches["target_id"].dropna().astype(str).unique().tolist()


def source_ids_for_target(
    relationships: pd.DataFrame,
    target_id: str,
    source_type: str,
) -> list[str]:
    matches = relationships[
        (relationships["target_id"] == target_id)
        & (relationships["source_type"] == source_type)
    ]
    return matches["source_id"].dropna().astype(str).unique().tolist()


def show_chart(caption: str, chart) -> None:
    st.caption(caption)
    st.plotly_chart(chart, use_container_width=True)


def show_evidence_cards(evidence_items: pd.DataFrame, empty_message: str) -> None:
    if evidence_items.empty:
        st.info(empty_message)
        return

    for _, item in evidence_items.sort_values("date", ascending=False).iterrows():
        direction = str(item["evidence_direction"])
        confidence = str(item["confidence"])
        title = f"{item['evidence_title']} - {direction} / {confidence}"
        expanded = direction in ["needs_review", "challenges"]

        with st.expander(title, expanded=expanded):
            if expanded:
                st.warning(f"{direction} evidence needs attention.")
            else:
                st.markdown(f"**Direction:** `{direction}`  **Confidence:** `{confidence}`")

            st.markdown(f"**Date:** {item['date']}")
            st.markdown("**Observed fact**")
            st.write(item["fact_text"])
            st.markdown("**Evidence interpretation**")
            st.write(item["evidence_summary"])
            st.markdown(
                f"**Company:** `{item['related_company_id']}`  "
                f"**Thesis:** `{item['related_thesis_id']}`"
            )
            if pd.notna(item["source_url"]) and str(item["source_url"]).strip():
                st.markdown(f"[Source]({item['source_url']})")
            if pd.notna(item["notes"]) and str(item["notes"]).strip():
                st.markdown("**Notes**")
                st.write(item["notes"])


OPTIONAL_FINANCIAL_CHARTS = {
    "CapEx": (
        "How much is the company investing to support growth?",
        capex_line_chart,
    ),
    "Operating margin": (
        "Is operating leverage improving as the business scales?",
        operating_margin_line_chart,
    ),
    "Inventory": (
        "Is inventory building faster than demand?",
        inventory_line_chart,
    ),
}


OPTIONAL_VALUATION_CHARTS = {
    "Price-to-sales": (
        "How is valuation moving relative to revenue?",
        price_to_sales_line_chart,
    ),
}


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

    selected_company_ids = multi_company_filter("Companies", companies)
    selected_periods = period_filter(financials)
    filtered = financials[
        financials["company_id"].isin(selected_company_ids)
        & financials["period"].isin(selected_periods)
    ]
    filtered = add_company_names(filtered, companies)

    first_row, second_row = st.columns(2)
    with first_row:
        show_chart(
            "What does revenue say about demand and business scale?",
            revenue_line_chart(filtered),
        )
        show_chart(
            "Is growth accelerating or decelerating?",
            revenue_yoy_line_chart(filtered),
        )
        show_chart(
            "Can the company fund growth from its own cash generation?",
            free_cash_flow_line_chart(filtered),
        )
    with second_row:
        show_chart(
            "How much profitability is reaching shareholders?",
            eps_line_chart(filtered),
        )
        show_chart(
            "What do margins say about pricing power and product mix?",
            gross_margin_line_chart(filtered),
        )

    optional_charts = st.multiselect(
        "Optional financial charts",
        list(OPTIONAL_FINANCIAL_CHARTS.keys()),
    )
    for chart_name in optional_charts:
        caption, chart_function = OPTIONAL_FINANCIAL_CHARTS[chart_name]
        show_chart(caption, chart_function(filtered))

    st.dataframe(
        sort_by_period(filtered)[
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
        ],
        use_container_width=True,
        hide_index=True,
    )


def render_valuation(companies: pd.DataFrame, valuations: pd.DataFrame) -> None:
    st.title("Valuation")

    selected_company_ids = multi_company_filter("Companies", companies)
    filtered = valuations[valuations["company_id"].isin(selected_company_ids)]
    filtered = add_company_names(filtered, companies)

    show_chart(
        "How is valuation changing relative to future earnings expectations?",
        forward_pe_line_chart(filtered),
    )

    optional_charts = st.multiselect(
        "Optional valuation charts",
        list(OPTIONAL_VALUATION_CHARTS.keys()),
    )
    for chart_name in optional_charts:
        caption, chart_function = OPTIONAL_VALUATION_CHARTS[chart_name]
        show_chart(caption, chart_function(filtered))

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


def render_watchlist(companies: pd.DataFrame, watchlist: pd.DataFrame) -> None:
    st.title("Watchlist")

    priority = st.multiselect(
        "Priority",
        sorted(watchlist["priority"].unique()),
        default=sorted(watchlist["priority"].unique()),
    )
    current_position = st.multiselect(
        "Current position",
        sorted(watchlist["current_position"].unique()),
        default=sorted(watchlist["current_position"].unique()),
    )

    filtered = watchlist[
        watchlist["priority"].isin(priority)
        & watchlist["current_position"].isin(current_position)
    ]
    filtered = add_company_names(filtered, companies)

    st.dataframe(
        filtered[
            [
                "company_name",
                "priority",
                "current_position",
                "thesis",
                "risk",
                "next_check",
            ]
        ].sort_values(["priority", "next_check", "company_name"]),
        use_container_width=True,
        hide_index=True,
    )


def render_industry_thesis(
    industry_theses: pd.DataFrame,
    evidence: pd.DataFrame,
    technologies: pd.DataFrame,
    products: pd.DataFrame,
    company_exposure: pd.DataFrame,
) -> None:
    st.title("Industry Thesis")

    st.subheader("Industry Theses")
    industry_layer = st.multiselect(
        "Industry layer",
        filter_values(industry_theses, "industry_layer"),
        default=filter_values(industry_theses, "industry_layer"),
    )
    thesis_category = st.multiselect(
        "Thesis category",
        filter_values(industry_theses, "thesis_category"),
        default=filter_values(industry_theses, "thesis_category"),
    )
    status = st.multiselect(
        "Status",
        filter_values(industry_theses, "status"),
        default=filter_values(industry_theses, "status"),
    )
    conviction = st.multiselect(
        "Conviction",
        filter_values(industry_theses, "conviction"),
        default=filter_values(industry_theses, "conviction"),
    )

    filtered_theses = industry_theses[
        industry_theses["industry_layer"].astype(str).isin(industry_layer)
        & industry_theses["thesis_category"].astype(str).isin(thesis_category)
        & industry_theses["status"].isin(status)
        & industry_theses["conviction"].isin(conviction)
    ]
    show_table_or_message(
        filtered_theses[
            [
                "thesis_id",
                "industry_layer",
                "thesis_category",
                "thesis_title",
                "thesis_summary",
                "status",
                "conviction",
                "key_drivers",
                "risks",
                "last_reviewed",
            ]
        ].sort_values(["industry_layer", "thesis_category", "last_reviewed"]),
        "No theses match the selected filters.",
    )

    selected_thesis_ids = filtered_theses["thesis_id"].tolist()

    st.subheader("Related Evidence")
    related_evidence = evidence[evidence["related_thesis_id"].isin(selected_thesis_ids)]
    show_table_or_message(
        related_evidence[
            [
                "date",
                "related_thesis_id",
                "fact_text",
                "evidence_summary",
                "evidence_direction",
                "confidence",
                "related_company_id",
                "source_url",
            ]
        ],
        "No evidence is linked to the selected theses.",
    )

    st.subheader("Related Technologies")
    related_technologies = technologies[
        technologies["related_thesis_ids"].apply(
            lambda value: any(thesis_id in split_ids(value) for thesis_id in selected_thesis_ids)
        )
    ]
    show_table_or_message(
        related_technologies[
            [
                "technology_name",
                "technology_category",
                "description",
                "related_thesis_ids",
                "maturity_stage",
                "key_companies",
            ]
        ],
        "No technologies are linked to the selected theses.",
    )

    st.subheader("Related Products")
    related_products = products[
        products["related_thesis_ids"].apply(
            lambda value: any(thesis_id in split_ids(value) for thesis_id in selected_thesis_ids)
        )
    ]
    show_table_or_message(
        related_products[
            [
                "product_name",
                "primary_company_id",
                "product_category",
                "description",
                "launch_status",
                "related_technology_ids",
                "related_thesis_ids",
            ]
        ],
        "No products are linked to the selected theses.",
    )

    st.subheader("Related Company Exposures")
    related_exposure = company_exposure[
        company_exposure["thesis_id"].isin(selected_thesis_ids)
    ]
    show_table_or_message(
        related_exposure[
            [
                "company_id",
                "thesis_id",
                "exposure_level",
                "exposure_reason",
                "evidence_id",
                "last_reviewed",
            ]
        ],
        "No company exposure is linked to the selected theses.",
    )


def render_technology_page(technologies: pd.DataFrame) -> None:
    st.title("Technology")

    technology_category = st.multiselect(
        "Technology category",
        filter_values(technologies, "technology_category"),
        default=filter_values(technologies, "technology_category"),
    )
    maturity_stage = st.multiselect(
        "Maturity stage",
        filter_values(technologies, "maturity_stage"),
        default=filter_values(technologies, "maturity_stage"),
    )

    filtered = technologies[
        technologies["technology_category"].astype(str).isin(technology_category)
        & technologies["maturity_stage"].astype(str).isin(maturity_stage)
    ]
    show_table_or_message(
        filtered[
            [
                "technology_id",
                "technology_name",
                "technology_category",
                "description",
                "related_thesis_ids",
                "maturity_stage",
                "key_companies",
                "last_reviewed",
            ]
        ],
        "No technologies match the selected filters.",
    )


def render_product_page(products: pd.DataFrame) -> None:
    st.title("Product")

    product_data = products.copy()
    product_data["primary_company_id"] = product_data["primary_company_id"].fillna("")

    primary_company_id = st.multiselect(
        "Primary company ID",
        filter_values(product_data, "primary_company_id"),
        default=filter_values(product_data, "primary_company_id"),
    )
    product_category = st.multiselect(
        "Product category",
        filter_values(product_data, "product_category"),
        default=filter_values(product_data, "product_category"),
    )
    launch_status = st.multiselect(
        "Launch status",
        filter_values(product_data, "launch_status"),
        default=filter_values(product_data, "launch_status"),
    )

    filtered = product_data[
        product_data["primary_company_id"].astype(str).isin(primary_company_id)
        & product_data["product_category"].astype(str).isin(product_category)
        & product_data["launch_status"].astype(str).isin(launch_status)
    ]
    show_table_or_message(
        filtered[
            [
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
        ],
        "No products match the selected filters.",
    )


def render_evidence_page(evidence: pd.DataFrame) -> None:
    st.title("Evidence Inbox")

    evidence_direction = st.multiselect(
        "Evidence direction",
        filter_values(evidence, "evidence_direction"),
        default=filter_values(evidence, "evidence_direction"),
    )
    related_company_id = st.multiselect(
        "Related company ID",
        filter_values(evidence, "related_company_id"),
        default=filter_values(evidence, "related_company_id"),
    )
    related_thesis_id = st.multiselect(
        "Related thesis ID",
        filter_values(evidence, "related_thesis_id"),
        default=filter_values(evidence, "related_thesis_id"),
    )
    confidence = st.multiselect(
        "Confidence",
        filter_values(evidence, "confidence"),
        default=filter_values(evidence, "confidence"),
    )

    filtered = evidence[
        evidence["evidence_direction"].astype(str).isin(evidence_direction)
        & evidence["related_company_id"].astype(str).isin(related_company_id)
        & evidence["related_thesis_id"].astype(str).isin(related_thesis_id)
        & evidence["confidence"].astype(str).isin(confidence)
    ]
    attention_evidence = filtered[
        filtered["evidence_direction"].isin(["needs_review", "challenges"])
    ]

    st.subheader("Needs Review / Challenges")
    show_evidence_cards(
        attention_evidence,
        "No needs_review or challenges evidence matches the selected filters.",
    )

    st.subheader("Evidence Inbox")
    remaining_evidence = filtered.drop(attention_evidence.index)
    show_evidence_cards(
        remaining_evidence,
        "No other evidence records match the selected filters.",
    )

    st.subheader("Table View")
    evidence_view = filtered[
        [
            "date",
            "fact_text",
            "evidence_title",
            "evidence_summary",
            "evidence_direction",
            "confidence",
            "related_company_id",
            "related_thesis_id",
            "source_type",
            "source_url",
            "notes",
        ]
    ]
    if evidence_view.empty:
        st.info("No evidence records match the selected filters.")
        return
    st.dataframe(
        evidence_view,
        use_container_width=True,
        hide_index=True,
        column_config={"source_url": st.column_config.LinkColumn("source_url")},
    )


def render_relationships_page(relationships: pd.DataFrame) -> None:
    st.title("Relationships")

    source_type = st.multiselect(
        "Source type",
        filter_values(relationships, "source_type"),
        default=filter_values(relationships, "source_type"),
    )
    relationship_type = st.multiselect(
        "Relationship type",
        filter_values(relationships, "relationship_type"),
        default=filter_values(relationships, "relationship_type"),
    )
    target_type = st.multiselect(
        "Target type",
        filter_values(relationships, "target_type"),
        default=filter_values(relationships, "target_type"),
    )
    confidence = st.multiselect(
        "Confidence",
        filter_values(relationships, "confidence"),
        default=filter_values(relationships, "confidence"),
    )

    filtered = relationships[
        relationships["source_type"].astype(str).isin(source_type)
        & relationships["relationship_type"].astype(str).isin(relationship_type)
        & relationships["target_type"].astype(str).isin(target_type)
        & relationships["confidence"].astype(str).isin(confidence)
    ]
    show_table_or_message(
        filtered[
            [
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
        ],
        "No relationships match the selected filters.",
    )


def render_research_actions(research_actions: pd.DataFrame) -> None:
    st.title("Research Actions")

    priority = st.multiselect(
        "Priority",
        filter_values(research_actions, "priority"),
        default=filter_values(research_actions, "priority"),
    )
    status = st.multiselect(
        "Status",
        filter_values(research_actions, "status"),
        default=filter_values(research_actions, "status"),
    )
    related_company_id = st.multiselect(
        "Related company ID",
        filter_values(research_actions, "related_company_id"),
        default=filter_values(research_actions, "related_company_id"),
    )
    related_thesis_id = st.multiselect(
        "Related thesis ID",
        filter_values(research_actions, "related_thesis_id"),
        default=filter_values(research_actions, "related_thesis_id"),
    )

    filtered = research_actions[
        research_actions["priority"].astype(str).isin(priority)
        & research_actions["status"].astype(str).isin(status)
        & research_actions["related_company_id"].astype(str).isin(related_company_id)
        & research_actions["related_thesis_id"].astype(str).isin(related_thesis_id)
    ]
    filtered = sort_research_actions(filtered)
    active_actions = filtered[
        filtered["status"].isin(["Open", "In Progress", "Waiting"])
    ]
    action_columns = [
        "priority",
        "status",
        "due_date",
        "action_title",
        "reason",
        "next_step",
        "related_company_id",
        "related_thesis_id",
        "related_evidence_id",
        "last_updated",
    ]

    st.subheader("Open / Active Actions")
    show_table_or_message(
        active_actions[action_columns],
        "No open or active research actions match the selected filters.",
    )

    st.subheader("All Matching Actions")
    show_table_or_message(
        filtered[action_columns],
        "No research actions match the selected filters.",
    )


def render_research_home(
    research_actions: pd.DataFrame,
    evidence: pd.DataFrame,
    industry_theses: pd.DataFrame,
    watchlist: pd.DataFrame,
) -> None:
    st.title("Research Home")
    st.caption("What should I pay attention to next?")

    active_statuses = ["Open", "In Progress", "Waiting"]
    high_priority_actions = research_actions[
        (research_actions["priority"] == "High")
        & research_actions["status"].isin(active_statuses)
    ]
    high_priority_actions = sort_research_actions(high_priority_actions)

    st.subheader("Open High Priority Research Actions")
    show_table_or_message(
        high_priority_actions[
            [
                "status",
                "due_date",
                "action_title",
                "reason",
                "next_step",
                "related_company_id",
                "related_thesis_id",
            ]
        ],
        "No open high priority research actions.",
    )

    st.subheader("Recent Evidence")
    recent_evidence = evidence.sort_values("date", ascending=False).head(8)
    show_table_or_message(
        recent_evidence[
            [
                "date",
                "fact_text",
                "evidence_title",
                "evidence_direction",
                "confidence",
                "related_company_id",
                "related_thesis_id",
            ]
        ],
        "No evidence records yet.",
    )

    st.subheader("Evidence Marked Needs Review Or Challenges")
    review_evidence = evidence[
        evidence["evidence_direction"].isin(["needs_review", "challenges"])
    ].sort_values("date", ascending=False)
    show_table_or_message(
        review_evidence[
            [
                "date",
                "fact_text",
                "evidence_title",
                "evidence_direction",
                "confidence",
                "related_company_id",
                "related_thesis_id",
                "notes",
            ]
        ],
        "No evidence is currently marked needs_review or challenges.",
    )

    st.subheader("Industry Theses That May Need Review")
    review_thesis_ids = review_evidence["related_thesis_id"].dropna().astype(str).unique()
    theses_to_review = industry_theses[
        industry_theses["thesis_id"].isin(review_thesis_ids)
        | industry_theses["status"].isin(["Watching", "Needs Review"])
    ]
    thesis_columns = [
        "thesis_id",
        "industry_layer",
        "thesis_category",
        "thesis_title",
        "status",
        "conviction",
        "last_reviewed",
        "key_questions",
    ]
    thesis_columns = [
        column for column in thesis_columns if column in theses_to_review.columns
    ]
    show_table_or_message(
        theses_to_review[thesis_columns].sort_values(["status", "last_reviewed"]),
        "No industry theses are flagged for review by current evidence or status.",
    )

    st.subheader("High Priority Watchlist Items")
    high_priority_watchlist = watchlist[watchlist["priority"] == "High"]
    show_table_or_message(
        high_priority_watchlist[
            [
                "company_id",
                "current_position",
                "thesis",
                "risk",
                "next_check",
            ]
        ].sort_values("next_check"),
        "No high priority watchlist items.",
    )


def render_company_detail(
    companies: pd.DataFrame,
    financials: pd.DataFrame,
    valuations: pd.DataFrame,
    estimates: pd.DataFrame,
    events: pd.DataFrame,
    theme_exposure: pd.DataFrame,
    company_exposure: pd.DataFrame,
    industry_theses: pd.DataFrame,
    evidence: pd.DataFrame,
    technologies: pd.DataFrame,
    products: pd.DataFrame,
    relationships: pd.DataFrame,
    watchlist: pd.DataFrame,
    research_actions: pd.DataFrame,
) -> None:
    st.title("Company Research Brief")
    company_id, company_name = select_company(companies)

    company = companies[companies["company_id"] == company_id].iloc[0]
    company_financials = financials[financials["company_id"] == company_id]
    company_valuations = valuations[valuations["company_id"] == company_id]
    company_estimates = estimates[estimates["company_id"] == company_id]
    company_events = events[events["company_id"] == company_id]
    company_themes = theme_exposure[theme_exposure["company_id"] == company_id]
    company_watchlist = watchlist[watchlist["company_id"] == company_id]
    company_exposures = company_exposure[company_exposure["company_id"] == company_id]
    company_evidence = evidence[evidence["related_company_id"] == company_id]
    company_actions = research_actions[
        research_actions["related_company_id"] == company_id
    ]
    open_company_actions = sort_research_actions(
        company_actions[company_actions["status"].isin(["Open", "In Progress", "Waiting"])]
    )
    company_product_ids = source_ids_for_target(relationships, company_id, "Product")
    company_technology_ids = source_ids_for_target(relationships, company_id, "Technology")
    direct_product_ids = products[
        products["primary_company_id"].fillna("") == company_id
    ]["product_id"].tolist()
    product_ids = sorted(set(company_product_ids + direct_product_ids))
    technology_ids = set(company_technology_ids)
    for product_id in product_ids:
        product_row = products[products["product_id"] == product_id]
        if not product_row.empty:
            for value in product_row["related_technology_ids"]:
                technology_ids.update(split_ids(value))

    st.subheader("Why this company?")
    st.write(company["description"])

    profile_summary = pd.DataFrame(
        {
            "Field": [
                "Ticker",
                "Exchange",
                "Country",
                "Sector",
                "AI infrastructure category",
            ],
            "Value": [
                company["ticker"],
                company["exchange"],
                company["country"],
                company["sector"],
                company["ai_infra_category"],
            ],
        }
    )
    st.dataframe(profile_summary, use_container_width=True, hide_index=True)

    st.write("Watchlist priority and next check")
    show_table_or_message(
        company_watchlist[
            ["priority", "current_position", "thesis", "risk", "next_check"]
        ],
        "No watchlist context for this company.",
    )

    st.write("Industry thesis exposure")
    exposure_view = company_exposures.merge(
        industry_theses[
            [
                "thesis_id",
                "industry_layer",
                "thesis_category",
                "thesis_title",
                "status",
                "conviction",
            ]
        ],
        on="thesis_id",
        how="left",
    )
    show_table_or_message(
        exposure_view[
            [
                "industry_layer",
                "thesis_category",
                "thesis_title",
                "exposure_level",
                "exposure_reason",
                "evidence_id",
                "status",
                "conviction",
            ]
        ],
        "No industry thesis exposure for this company.",
    )

    st.subheader("Supporting Evidence")
    supporting_evidence = company_evidence[
        company_evidence["evidence_direction"] == "supports"
    ]
    show_evidence_cards(
        supporting_evidence,
        "No supporting evidence linked directly to this company.",
    )

    st.subheader("Challenging / Needs Review Evidence")
    challenging_evidence = company_evidence[
        company_evidence["evidence_direction"].isin(
            ["challenges", "weakens", "needs_review"]
        )
    ]
    show_evidence_cards(
        challenging_evidence,
        "No challenging, weakening, or needs_review evidence linked directly to this company.",
    )

    st.subheader("Recent Events")
    show_table_or_message(
        company_events[
            [
                "date",
                "category",
                "event_title",
                "summary",
                "importance",
                "thesis_impact",
                "source_url",
            ]
        ].sort_values("date", ascending=False),
        "No recent events for this company.",
    )

    st.subheader("Open Research Actions")
    show_table_or_message(
        open_company_actions[
            [
                "priority",
                "status",
                "due_date",
                "action_title",
                "reason",
                "next_step",
                "related_thesis_id",
                "related_evidence_id",
            ]
        ],
        "No open research actions for this company.",
    )

    st.subheader("Related Technologies")
    related_technologies = technologies[
        technologies["technology_id"].isin(sorted(technology_ids))
    ]
    show_table_or_message(
        related_technologies[
            [
                "technology_name",
                "technology_category",
                "description",
                "related_thesis_ids",
                "maturity_stage",
                "key_companies",
            ]
        ],
        "No related technologies found for this company.",
    )

    st.subheader("Related Products")
    related_products = products[products["product_id"].isin(product_ids)]
    show_table_or_message(
        related_products[
            [
                "product_name",
                "primary_company_id",
                "product_category",
                "description",
                "launch_status",
                "related_technology_ids",
                "related_thesis_ids",
            ]
        ],
        "No related products found for this company.",
    )

    st.subheader("Open Questions / Next Checks")
    next_checks = []
    for _, item in company_watchlist.iterrows():
        next_checks.append(
            {
                "source": "Watchlist",
                "question_or_check": item["risk"],
                "next_step": item["next_check"],
            }
        )
    for _, item in open_company_actions.iterrows():
        next_checks.append(
            {
                "source": "Research Action",
                "question_or_check": item["reason"],
                "next_step": item["next_step"],
            }
        )
    show_table_or_message(
        pd.DataFrame(next_checks),
        "No open questions or next checks for this company.",
    )

    st.subheader("Financial Snapshot")
    st.write(company_name)
    profile = pd.DataFrame(
        {
            "Field": [
                "Ticker",
                "Exchange",
                "Country",
                "Sector",
                "AI infrastructure category",
                "Website",
            ],
            "Value": [
                company["ticker"],
                company["exchange"],
                company["country"],
                company["sector"],
                company["ai_infra_category"],
                company["website"],
            ],
        }
    )
    st.dataframe(profile, use_container_width=True, hide_index=True)

    st.subheader("Watchlist Notes")
    watchlist_view = company_watchlist[
        ["priority", "current_position", "thesis", "risk", "next_check"]
    ]
    show_table_or_message(watchlist_view, "No watchlist notes for this company.")

    if not company_financials.empty:
        st.subheader("Financial Trends")
        trend_data = add_company_names(company_financials, companies)
        first_row, second_row = st.columns(2)
        with first_row:
            show_chart(
                "What does revenue say about demand and business scale?",
                revenue_line_chart(trend_data),
            )
            show_chart(
                "Is growth accelerating or decelerating?",
                revenue_yoy_line_chart(trend_data),
            )
            show_chart(
                "Can the company fund growth from its own cash generation?",
                free_cash_flow_line_chart(trend_data),
            )
        with second_row:
            show_chart(
                "How much profitability is reaching shareholders?",
                eps_line_chart(trend_data),
            )
            show_chart(
                "What do margins say about pricing power and product mix?",
                gross_margin_line_chart(trend_data),
            )

        optional_charts = st.multiselect(
            "Optional company financial charts",
            list(OPTIONAL_FINANCIAL_CHARTS.keys()),
        )
        for chart_name in optional_charts:
            caption, chart_function = OPTIONAL_FINANCIAL_CHARTS[chart_name]
            show_chart(caption, chart_function(trend_data))

    st.subheader("Latest Financial Metrics")
    if company_financials.empty:
        st.info("No financial metrics for this company.")
    else:
        latest_financial = company_financials.sort_values("period").tail(1)
        st.dataframe(
            latest_financial[
                [
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
            ],
            use_container_width=True,
            hide_index=True,
        )

    if not company_valuations.empty:
        st.subheader("Valuation Trends")
        valuation_trend_data = add_company_names(company_valuations, companies)
        show_chart(
            "How is valuation changing relative to future earnings expectations?",
            forward_pe_line_chart(valuation_trend_data),
        )
        optional_charts = st.multiselect(
            "Optional company valuation charts",
            list(OPTIONAL_VALUATION_CHARTS.keys()),
        )
        for chart_name in optional_charts:
            caption, chart_function = OPTIONAL_VALUATION_CHARTS[chart_name]
            show_chart(caption, chart_function(valuation_trend_data))

    st.subheader("Latest Valuation Metrics")
    if company_valuations.empty:
        st.info("No valuation metrics for this company.")
    else:
        latest_valuation = company_valuations.sort_values("date").tail(1)
        st.dataframe(
            latest_valuation[
                [
                    "date",
                    "price",
                    "market_cap_usd_m",
                    "trailing_pe",
                    "forward_pe",
                    "price_to_sales",
                    "ev_to_ebitda",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Estimates")
    estimates_view = company_estimates[
        [
            "period",
            "estimated_revenue_usd_m",
            "estimated_eps",
            "estimated_revenue_yoy_pct",
            "estimated_eps_yoy_pct",
            "analyst_count",
            "revision_direction",
        ]
    ].sort_values("period", ascending=False)
    show_table_or_message(estimates_view, "No estimates for this company.")

    st.subheader("Theme Exposure")
    themes_view = company_themes[
        ["theme", "exposure_level", "notes"]
    ].sort_values(["theme", "exposure_level"])
    show_table_or_message(themes_view, "No theme exposure for this company.")

    st.subheader("Recent Events")
    events_view = company_events[
        [
            "date",
            "category",
            "event_title",
            "summary",
            "importance",
            "thesis_impact",
            "source_url",
        ]
    ].sort_values("date", ascending=False)
    show_table_or_message(events_view, "No recent events for this company.")


def main() -> None:
    companies = load_companies()
    financials = load_financial_metrics()
    valuations = load_valuation_metrics()
    estimates = load_estimates()
    events = load_ai_infra_events()
    theme_exposure = load_theme_exposure()
    company_exposure = load_company_exposure()
    watchlist = load_watchlist()
    industry_theses = load_industry_theses()
    technologies = load_technologies()
    products = load_products()
    evidence = load_evidence()
    relationships = load_relationships()
    research_actions = load_research_actions()

    st.sidebar.title("AI Infrastructure")
    page = st.sidebar.radio(
        "Navigate",
        [
            "Research Home",
            "Research Actions",
            "Overview",
            "Companies",
            "Company Detail",
            "Financial Metrics",
            "Valuation",
            "Estimates",
            "Events",
            "Theme Exposure",
            "Watchlist",
            "Industry Thesis",
            "Technology",
            "Product",
            "Evidence",
            "Relationships",
        ],
        label_visibility="collapsed",
    )

    if page == "Research Home":
        render_research_home(
            research_actions,
            evidence,
            industry_theses,
            watchlist,
        )
    elif page == "Research Actions":
        render_research_actions(research_actions)
    elif page == "Overview":
        render_overview(companies, financials, events, theme_exposure)
    elif page == "Companies":
        render_companies(companies)
    elif page == "Company Detail":
        render_company_detail(
            companies,
            financials,
            valuations,
            estimates,
            events,
            theme_exposure,
            company_exposure,
            industry_theses,
            evidence,
            technologies,
            products,
            relationships,
            watchlist,
            research_actions,
        )
    elif page == "Financial Metrics":
        render_financial_metrics(companies, financials)
    elif page == "Valuation":
        render_valuation(companies, valuations)
    elif page == "Estimates":
        render_estimates(companies, estimates)
    elif page == "Events":
        render_events(companies, events)
    elif page == "Theme Exposure":
        render_theme_exposure(companies, theme_exposure)
    elif page == "Watchlist":
        render_watchlist(companies, watchlist)
    elif page == "Industry Thesis":
        render_industry_thesis(
            industry_theses,
            evidence,
            technologies,
            products,
            company_exposure,
        )
    elif page == "Technology":
        render_technology_page(technologies)
    elif page == "Product":
        render_product_page(products)
    elif page == "Evidence":
        render_evidence_page(evidence)
    else:
        render_relationships_page(relationships)


if __name__ == "__main__":
    main()
