import streamlit as st
import pandas as pd
import plotly.express as px
from olist_report import run_query, TABLE_FACT, TABLE_CUSTOMERS, TABLE_STG_ORDERS, TABLE_DATES

# -------------------------
# Page Content
# -------------------------
st.title("Order Fulfillment & Delivery")

# Use tabs to organize content
tab1, tab2, tab3 = st.tabs(["Delivery Times", "Performance by Location", "Delivery Rates"])

with tab1:
    st.header("Overall Delivery Time Trend")

    sql_delivery_trend = f"""
    SELECT
        FORMAT_DATE('%Y-%m', d.full_date) AS month,
        AVG(f.delivery_time_days) AS avg_delivery_days
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_DATES}` d
        ON f.order_date_key = d.date_key
    GROUP BY 1
    ORDER BY 1
    """
    df_delivery_trend = run_query(sql_delivery_trend)
    
    if not df_delivery_trend.empty:
        fig_trend = px.line(df_delivery_trend, x="month", y="avg_delivery_days",
                            title="Average Delivery Time (Days) by Month",
                            labels={"month": "Month", "avg_delivery_days": "Avg. Delivery Days"})
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.warning("No data found for delivery time trends.")

with tab2:
    st.header("Average Delivery Time by Customer State")

    sql_delivery_by_state = f"""
    SELECT
        c.customer_state,
        AVG(f.delivery_time_days) AS avg_delivery_days
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_CUSTOMERS}` c
        ON f.customer_id = c.customer_id
    GROUP BY 1
    ORDER BY 2 DESC
    """
    df_delivery_by_state = run_query(sql_delivery_by_state)
    
    if not df_delivery_by_state.empty:
        fig_state = px.bar(df_delivery_by_state, x="avg_delivery_days", y="customer_state", orientation="h",
                           title="Average Delivery Time by State",
                           labels={"avg_delivery_days": "Avg. Delivery Days", "customer_state": "Customer State"})
        st.plotly_chart(fig_state, use_container_width=True)
    else:
        st.warning("No data found for delivery times by state.")

with tab3:
    st.header("Late Delivery Rate")
    
    # We must query the raw staging table for this, as the `order_estimated_delivery_date`
    # is not available in the fact table.
    sql_late_delivery = f"""
    SELECT
        CAST(SUM(CASE WHEN SAFE_CAST(order_delivered_customer_date AS DATE) > SAFE_CAST(order_estimated_delivery_date AS DATE) THEN 1 ELSE 0 END) AS FLOAT64) / COUNT(order_id) AS late_rate
    FROM `{TABLE_STG_ORDERS}`
    WHERE order_status = 'delivered'
    """
    df_late_delivery = run_query(sql_late_delivery)

    if not df_late_delivery.empty and 'late_rate' in df_late_delivery.columns:
        late_rate = df_late_delivery.iloc[0]['late_rate']
        st.metric("Late Delivery Rate", f"{late_rate:.2%}")
        st.info("This metric is calculated from the raw staging data because the final fact table does not contain the required date fields.")
    else:
        st.warning("No data available to calculate the late delivery rate.")