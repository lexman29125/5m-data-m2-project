import streamlit as st
import pandas as pd
import plotly.express as px
from olist_report import run_query, TABLE_FACT, TABLE_PRODUCTS

# -------------------------
# Page Content
# -------------------------
st.title("Product Analytics")

# Use tabs to organize content
tab1, tab2 = st.tabs(["Category Performance", "Reviews & Dimensions"])

with tab1:
    st.header("Top Performing Product Categories")
    
    # Query for product category performance
    sql_category_performance = f"""
    SELECT
        pr.product_category_name_english AS category,
        SUM(SAFE_CAST(f.price AS FLOAT64)) AS total_revenue,
        COUNT(DISTINCT f.order_id) AS total_orders
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_PRODUCTS}` pr
        ON f.product_id = pr.product_id
    GROUP BY 1
    ORDER BY total_revenue DESC
    LIMIT 20
    """
    df_category_performance = run_query(sql_category_performance)
    
    if not df_category_performance.empty:
        st.subheader("Top Categories by Revenue")
        fig_revenue = px.bar(df_category_performance.sort_values("total_revenue", ascending=False),
                             x="total_revenue", y="category", orientation="h",
                             labels={"total_revenue": "Total Revenue", "category": "Category"})
        st.plotly_chart(fig_revenue, use_container_width=True)

        st.subheader("Top Categories by Orders")
        fig_orders = px.bar(df_category_performance.sort_values("total_orders", ascending=False),
                            x="total_orders", y="category", orientation="h",
                            labels={"total_orders": "Total Orders", "category": "Category"})
        st.plotly_chart(fig_orders, use_container_width=True)
    else:
        st.warning("No data found for product category performance.")

with tab2:
    st.header("Product Insights")
    
    # Query for review score by product category
    sql_reviews_by_category = f"""
    SELECT
        pr.product_category_name_english AS category,
        AVG(SAFE_CAST(f.review_score AS FLOAT64)) AS avg_review_score
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_PRODUCTS}` pr
        ON f.product_id = pr.product_id
    WHERE f.review_score IS NOT NULL
    GROUP BY 1
    ORDER BY avg_review_score DESC
    LIMIT 20
    """
    df_reviews_by_category = run_query(sql_reviews_by_category)
    
    if not df_reviews_by_category.empty:
        st.subheader("Average Review Score by Category")
        fig_reviews = px.bar(df_reviews_by_category, x="avg_review_score", y="category", orientation="h",
                              labels={"avg_review_score": "Avg. Review Score", "category": "Category"})
        st.plotly_chart(fig_reviews, use_container_width=True)
    else:
        st.warning("No data found for reviews by category.")
        
    # Query for product weight vs. review score
    sql_weight_vs_review = f"""
    SELECT
        SAFE_CAST(pr.product_weight_g AS FLOAT64) AS weight_g,
        AVG(SAFE_CAST(f.review_score AS FLOAT64)) AS avg_review_score
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_PRODUCTS}` pr
        ON f.product_id = pr.product_id
    WHERE
        pr.product_weight_g IS NOT NULL
        AND f.review_score IS NOT NULL
    GROUP BY 1
    """
    df_weight_vs_review = run_query(sql_weight_vs_review)

    if not df_weight_vs_review.empty:
        st.subheader("Product Weight vs. Review Score")
        fig_weight_review = px.scatter(df_weight_vs_review, x="weight_g", y="avg_review_score",
                                        labels={"weight_g": "Product Weight (g)", "avg_review_score": "Avg. Review Score"})
        st.plotly_chart(fig_weight_review, use_container_width=True)
    else:
        st.warning("No data found for product weight vs. review score.")