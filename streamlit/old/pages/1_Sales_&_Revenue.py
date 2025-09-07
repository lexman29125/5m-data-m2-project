import streamlit as st
import pandas as pd
import plotly.express as px
from olist_report import run_query, TABLE_FACT, TABLE_PAYMENTS, TABLE_DATES

# -------------------------
# Page Content
# -------------------------
st.title("Sales & Revenue Insights")

# Use tabs to organize content within this page
tab1, tab2 = st.tabs(["Trends & KPIs", "Analysis by Channel"])

with tab1:
    st.header("Overall Sales Performance")

    sql_trends = f"""
    SELECT
        FORMAT_DATE('%Y-%m', d.full_date) AS month,
        SUM(SAFE_CAST(f.price AS FLOAT64)) AS total_revenue,
        COUNT(DISTINCT f.order_id) AS total_orders
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_DATES}` d ON f.order_date_key = d.date_key
    GROUP BY 1
    ORDER BY 1
    """
    df_trends = run_query(sql_trends)
    
    col1, col2 = st.columns(2)
    with col1:
        total_revenue = df_trends['total_revenue'].sum() if not df_trends.empty else 0
        st.metric("Total Revenue", f"${total_revenue:,.2f}")
    with col2:
        total_orders = df_trends['total_orders'].sum() if not df_trends.empty else 0
        st.metric("Total Orders", f"{total_orders:,}")

    st.subheader("Monthly Revenue Trend")
    fig = px.line(df_trends, x="month", y="total_revenue", markers=True,
                  labels={"month": "Month", "total_revenue": "Total Revenue"})
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Revenue by Payment Type")
    
    sql_payments = f"""
    SELECT
        p.payment_type,
        SUM(SAFE_CAST(f.price AS FLOAT64)) AS total_revenue
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_PAYMENTS}` p
    ON f.payment_type_key = p.payment_type_key
    GROUP BY 1
    ORDER BY 2 DESC
    """
    df_payments = run_query(sql_payments)
    
    fig = px.bar(df_payments, x="payment_type", y="total_revenue",
                 labels={"payment_type": "Payment Type", "total_revenue": "Total Revenue"})
    st.plotly_chart(fig, use_container_width=True)