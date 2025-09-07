import streamlit as st
import pandas as pd
import plotly.express as px
from olist_report import run_query, TABLE_FACT, TABLE_PRODUCTS, TABLE_DATES

# -------------------------
# Page Content
# -------------------------
st.title("Product Performance")

# Use tabs to organize content
tab1, tab2 = st.tabs(["Sales Trends", "Top Products"])

with tab1:
    st.header("Monthly Sales Trends by Product Category")

    sql_trends = f"""
    SELECT
        FORMAT_DATE('%Y-%m', d.full_date) AS month,
        COALESCE(p.product_category_name_english, 'untranslated') AS product_category,
        SUM(SAFE_CAST(f.price AS FLOAT64)) AS total_revenue
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_PRODUCTS}` p
        ON f.product_id = p.product_id
    JOIN `{TABLE_DATES}` d
        ON f.order_date_key = d.date_key
    GROUP BY 1, 2
    ORDER BY 1, 3 DESC
    """
    df_trends = run_query(sql_trends)

    if not df_trends.empty:
        fig_trends = px.line(df_trends, x="month", y="total_revenue", color="product_category",
                             title="Revenue Trend by Category",
                             labels={"month": "Month", "total_revenue": "Total Revenue", "product_category": "Product Category"})
        st.plotly_chart(fig_trends, use_container_width=True)
    else:
        st.warning("No data found for product sales trends.")

with tab2:
    st.header("Top 10 Product Categories")
    
    # Query for top products by revenue
    sql_top_revenue = f"""
    SELECT
        COALESCE(p.product_category_name_english, 'untranslated') AS product_category,
        SUM(SAFE_CAST(f.price AS FLOAT64)) AS total_revenue
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_PRODUCTS}` p
        ON f.product_id = p.product_id
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT 10
    """
    df_top_revenue = run_query(sql_top_revenue)

    # Query for top products by units sold
    sql_top_units = f"""
    SELECT
        COALESCE(p.product_category_name_english, 'untranslated') AS product_category,
        COUNT(f.order_id) AS total_units_sold
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_PRODUCTS}` p
        ON f.product_id = p.product_id
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT 10
    """
    df_top_units = run_query(sql_top_units)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("By Revenue")
        fig_revenue = px.bar(df_top_revenue, x="total_revenue", y="product_category", orientation="h",
                             labels={"total_revenue": "Total Revenue", "product_category": "Product Category"})
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col2:
        st.subheader("By Units Sold")
        fig_units = px.bar(df_top_units, x="total_units_sold", y="product_category", orientation="h",
                           labels={"total_units_sold": "Total Units Sold", "product_category": "Product Category"})
        st.plotly_chart(fig_units, use_container_width=True)