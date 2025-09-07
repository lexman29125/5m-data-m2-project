import streamlit as st
import pandas as pd
import plotly.express as px
from olist_report import run_query, TABLE_FACT, TABLE_SELLERS

# -------------------------
# Page Content
# -------------------------
st.title("Seller Performance & Reviews")

# Use tabs to organize content
tab1, tab2 = st.tabs(["Top Sellers", "Review Analysis"])

with tab1:
    st.header("Top Performing Sellers")

    sql_seller_kpis = f"""
    SELECT
        f.seller_id,
        s.seller_city,
        s.seller_state,
        COUNT(DISTINCT f.order_id) AS total_orders,
        SUM(SAFE_CAST(f.price AS FLOAT64)) AS total_revenue,
        AVG(SAFE_CAST(f.review_score AS FLOAT64)) AS avg_review_score
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_SELLERS}` s
        ON f.seller_id = s.seller_id
    GROUP BY 1, 2, 3
    ORDER BY total_revenue DESC
    LIMIT 100
    """
    df_seller_kpis = run_query(sql_seller_kpis)

    if not df_seller_kpis.empty:
        st.subheader("By Revenue")
        fig_revenue = px.bar(df_seller_kpis.head(10), x="total_revenue", y="seller_id", orientation="h",
                             labels={"total_revenue": "Total Revenue", "seller_id": "Seller ID"})
        st.plotly_chart(fig_revenue, use_container_width=True)

        st.subheader("By Number of Orders")
        fig_orders = px.bar(df_seller_kpis.sort_values("total_orders", ascending=False).head(10),
                            x="total_orders", y="seller_id", orientation="h",
                            labels={"total_orders": "Total Orders", "seller_id": "Seller ID"})
        st.plotly_chart(fig_orders, use_container_width=True)
        
        st.subheader("By Average Review Score")
        fig_reviews = px.bar(df_seller_kpis.sort_values("avg_review_score", ascending=False).head(10),
                            x="avg_review_score", y="seller_id", orientation="h",
                            labels={"avg_review_score": "Avg. Review Score", "seller_id": "Seller ID"})
        st.plotly_chart(fig_reviews, use_container_width=True)
    else:
        st.warning("No data found for seller KPIs.")

with tab2:
    st.header("Customer Review Analysis")

    # Query for review score distribution
    sql_review_dist = f"""
    SELECT
        SAFE_CAST(f.review_score AS INT64) AS review_score,
        COUNT(f.review_score) AS num_reviews
    FROM `{TABLE_FACT}` f
    WHERE f.review_score IS NOT NULL
    GROUP BY 1
    ORDER BY 1
    """
    df_review_dist = run_query(sql_review_dist)

    if not df_review_dist.empty:
        st.subheader("Review Score Distribution")
        fig_dist = px.bar(df_review_dist, x="review_score", y="num_reviews",
                          labels={"review_score": "Review Score", "num_reviews": "Number of Reviews"})
        st.plotly_chart(fig_dist, use_container_width=True)
    else:
        st.warning("No data found for review distribution.")

    # Query for average review score by seller state
    sql_review_by_state = f"""
    SELECT
        s.seller_state,
        AVG(SAFE_CAST(f.review_score AS FLOAT64)) AS avg_review_score
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_SELLERS}` s
        ON f.seller_id = s.seller_id
    WHERE f.review_score IS NOT NULL
    GROUP BY 1
    ORDER BY 2 DESC
    """
    df_review_by_state = run_query(sql_review_by_state)
    
    if not df_review_by_state.empty:
        st.subheader("Average Review Score by Seller State")
        fig_state_rev = px.bar(df_review_by_state, x="avg_review_score", y="seller_state", orientation="h",
                               labels={"avg_review_score": "Avg. Review Score", "seller_state": "Seller State"})
        st.plotly_chart(fig_state_rev, use_container_width=True)
    else:
        st.warning("No data found for review scores by state.")