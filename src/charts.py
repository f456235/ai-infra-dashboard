import pandas as pd
import plotly.express as px


def period_sort_key(period: str) -> tuple[int, int, str]:
    cleaned = str(period).upper().replace("-", "").strip()
    if "Q" in cleaned:
        year_text, quarter_text = cleaned.split("Q", 1)
        if year_text.isdigit() and quarter_text.isdigit():
            return int(year_text), int(quarter_text), cleaned
    return 0, 0, cleaned


def sort_by_period(data: pd.DataFrame, period_column: str = "period") -> pd.DataFrame:
    data = data.copy()
    data["_period_sort"] = data[period_column].map(period_sort_key)
    return data.sort_values(["_period_sort", "company_name"]).drop(columns="_period_sort")


def metric_line_chart(
    data: pd.DataFrame,
    y_column: str,
    title: str,
    y_label: str,
):
    return px.line(
        sort_by_period(data),
        x="period",
        y=y_column,
        color="company_name",
        markers=True,
        title=title,
        labels={
            "period": "Period",
            y_column: y_label,
            "company_name": "Company",
        },
    )


def revenue_line_chart(financials: pd.DataFrame):
    return metric_line_chart(
        financials,
        "revenue_usd_m",
        "Revenue Trend",
        "Revenue, USD millions",
    )


def revenue_yoy_line_chart(financials: pd.DataFrame):
    return metric_line_chart(
        financials,
        "revenue_yoy_pct",
        "Revenue YoY Trend",
        "Revenue YoY %",
    )


def eps_line_chart(financials: pd.DataFrame):
    return metric_line_chart(financials, "eps", "EPS Trend", "EPS")


def gross_margin_line_chart(financials: pd.DataFrame):
    return metric_line_chart(
        financials,
        "gross_margin_pct",
        "Gross Margin Trend",
        "Gross margin %",
    )


def operating_margin_line_chart(financials: pd.DataFrame):
    return metric_line_chart(
        financials,
        "operating_margin_pct",
        "Operating Margin Trend",
        "Operating margin %",
    )


def free_cash_flow_line_chart(financials: pd.DataFrame):
    return metric_line_chart(
        financials,
        "free_cash_flow_usd_m",
        "Free Cash Flow Trend",
        "Free cash flow, USD millions",
    )


def capex_line_chart(financials: pd.DataFrame):
    return metric_line_chart(
        financials,
        "capex_usd_m",
        "CapEx Trend",
        "CapEx, USD millions",
    )


def inventory_line_chart(financials: pd.DataFrame):
    return metric_line_chart(
        financials,
        "inventory_usd_m",
        "Inventory Trend",
        "Inventory, USD millions",
    )


def valuation_line_chart(
    valuations: pd.DataFrame,
    y_column: str,
    title: str,
    y_label: str,
):
    return px.line(
        valuations.sort_values(["date", "company_name"]),
        x="date",
        y=y_column,
        color="company_name",
        markers=True,
        title=title,
        labels={
            "date": "Date",
            y_column: y_label,
            "company_name": "Company",
        },
    )


def forward_pe_line_chart(valuations: pd.DataFrame):
    return valuation_line_chart(
        valuations,
        "forward_pe",
        "Forward PE Trend",
        "Forward PE",
    )


def price_to_sales_line_chart(valuations: pd.DataFrame):
    return valuation_line_chart(
        valuations,
        "price_to_sales",
        "Price-to-Sales Trend",
        "Price to Sales",
    )
