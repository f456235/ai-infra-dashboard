import pandas as pd
import plotly.express as px


def revenue_line_chart(financials: pd.DataFrame):
    return px.line(
        financials,
        x="period",
        y="revenue_usd_m",
        color="company_name",
        markers=True,
        title="Revenue Over Time",
        labels={
            "period": "Period",
            "revenue_usd_m": "Revenue, USD millions",
            "company_name": "Company",
        },
    )


def valuation_scatter_chart(valuations: pd.DataFrame):
    return px.scatter(
        valuations,
        x="forward_pe",
        y="price_to_sales",
        size="market_cap_usd_m",
        color="company_name",
        hover_data=["date", "trailing_pe", "ev_to_ebitda"],
        title="Valuation Snapshot",
        labels={
            "forward_pe": "Forward PE",
            "price_to_sales": "Price to Sales",
            "market_cap_usd_m": "Market cap, USD millions",
            "company_name": "Company",
        },
    )
