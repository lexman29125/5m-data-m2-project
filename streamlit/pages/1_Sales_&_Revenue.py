# streamlit/pages/1_Sales_&_Revenue.py

import streamlit as st
import pandas as pd
import plotly.express as px
from olist_report import run_query, TABLE_FACT, TABLE_PAYMENTS, TABLE_DATES, TABLE_CUSTOMERS, create_state_filter, get_state_filter_sql_clause, create_year_filter, get_year_filter_sql_clause

# -------------------------
# Page Content
# -------------------------
st.title("Sales & Revenue Insights")

# Create the customer state filter UI
selected_states = create_state_filter(TABLE_CUSTOMERS)
selected_years = create_year_filter(TABLE_DATES)
st.session_state.selected_states = selected_states
st.session_state.selected_years = selected_years

# Use tabs to organize content within this page
tab1, tab2 = st.tabs(["Trends & KPIs", "Analysis by Channel"])

with tab1:
    st.header("Overall Sales Performance")

    state_filter = get_state_filter_sql_clause("c", selected_states)
    year_filter = get_year_filter_sql_clause("d", st.session_state.selected_years)
    sql_trends = f"""
    SELECT
        FORMAT_DATE('%Y-%m', d.full_date) AS month,
        SUM(SAFE_CAST(f.price AS FLOAT64)) AS total_revenue,
        COUNT(DISTINCT f.order_id) AS total_orders
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_DATES}` d ON f.order_date_key = d.date_key
    JOIN `{TABLE_CUSTOMERS}` c ON f.customer_id = c.customer_id
    WHERE TRUE {state_filter} {year_filter}
    GROUP BY month
    ORDER BY month
    """
    df_trends = run_query(sql_trends)

    if not df_trends.empty:
        # Filter out the incomplete latest month for trend analysis
        df_trends['month_dt'] = pd.to_datetime(df_trends['month'])
        df_trends = df_trends[df_trends['month_dt'] < pd.to_datetime('today').to_period('M').to_timestamp()]

    # Calculate and display metrics using st.columns
    col1, col2, col3 = st.columns(3)
    with col1:
        total_revenue = df_trends['total_revenue'].sum() if not df_trends.empty else 0
        st.metric("Total Revenue", f"${total_revenue:,.2f}")
    with col2:
        total_orders = df_trends['total_orders'].sum() if not df_trends.empty else 0
        st.metric("Total Orders", f"{total_orders:,}")
    with col3:
        avg_revenue_per_order = total_revenue / total_orders if total_orders > 0 else 0
        st.metric("Average Revenue per Order", f"${avg_revenue_per_order:,.2f}")

    if not df_trends.empty:
        st.subheader("Monthly Revenue Trend")
        fig_revenue_trend = px.bar(df_trends, x="month_dt", y="total_revenue",
                            labels={"month_dt": "Month", "total_revenue": "Total Revenue"},
                            title="Monthly Revenue Trend")
        fig_revenue_trend.update_xaxes(dtick="M1", tickformat="%b\n%Y")
        st.plotly_chart(fig_revenue_trend, use_container_width=True)

        st.subheader("Monthly Orders Trend")
        fig_orders_trend = px.bar(df_trends, x="month_dt", y="total_orders",
                            labels={"month_dt": "Month", "total_orders": "Total Orders"},
                            title="Monthly Orders Trend")
        fig_orders_trend.update_xaxes(dtick="M1", tickformat="%b\n%Y")
        st.plotly_chart(fig_orders_trend, use_container_width=True)
        
        st.subheader("Cumulative Revenue Over Time")
        df_trends['cumulative_revenue'] = df_trends['total_revenue'].cumsum()
        fig_cumulative = px.line(df_trends, x="month_dt", y="cumulative_revenue", markers=True,
                                labels={"month_dt": "Month", "cumulative_revenue": "Cumulative Revenue"},
                                title="Cumulative Revenue Over Time")
        fig_cumulative.update_xaxes(dtick="M1", tickformat="%b\n%Y")
        st.plotly_chart(fig_cumulative, use_container_width=True)
    else:
        st.warning("No data found for sales trends with the current filter selection.")

with tab2:
    st.header("Revenue by Payment Type")
    
    state_filter = get_state_filter_sql_clause("c", selected_states)
    year_filter = get_year_filter_sql_clause("d", st.session_state.selected_years)
    sql_payments = f"""
    SELECT
        p.payment_type,
        SUM(SAFE_CAST(f.price AS FLOAT64)) AS total_revenue
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_PAYMENTS}` p
        ON f.payment_type_key = p.payment_type_key
    JOIN `{TABLE_CUSTOMERS}` c
        ON f.customer_id = c.customer_id
    JOIN `{TABLE_DATES}` d
        ON f.order_date_key = d.date_key
    WHERE TRUE {state_filter} {year_filter}
    GROUP BY p.payment_type
    ORDER BY total_revenue DESC
    """
    df_payments = run_query(sql_payments)
    
    if not df_payments.empty:
        fig_payments = px.pie(df_payments, values='total_revenue', names='payment_type',
                              title='Revenue Distribution by Payment Type')
        st.plotly_chart(fig_payments, use_container_width=True)
    else:
        st.warning("No data found for revenue by payment type.")