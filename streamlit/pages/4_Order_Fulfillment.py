# streamlit/pages/4_Order_Fulfillment.py

import streamlit as st
import pandas as pd
import plotly.express as px
from olist_report import (
    run_query,
    TABLE_FACT,
    TABLE_CUSTOMERS,
    TABLE_STG_ORDERS,
    TABLE_STG_CUSTOMERS,
    TABLE_DATES,
    create_state_filter,
    get_state_filter_sql_clause,
    create_year_filter,
    get_year_filter_sql_clause,
)

# -------------------------
# Page Content
# -------------------------
st.title("Order Fulfillment & Delivery")

# Create the customer state and year filter UI
selected_states = create_state_filter(TABLE_CUSTOMERS)
selected_years = create_year_filter(TABLE_DATES)
st.session_state.selected_states = selected_states
st.session_state.selected_years = selected_years

# Use tabs to organize content
tab1, tab2, tab3 = st.tabs(["Delivery Times", "Performance by Location", "Delivery Rates"])

with tab1:
    st.header("Overall Delivery Time Trend")

    # This query uses the customer state and year filter.
    state_filter = get_state_filter_sql_clause("c", selected_states)
    year_filter = get_year_filter_sql_clause("d", st.session_state.selected_years)
    sql_delivery_trend = f"""
    SELECT
        FORMAT_DATE('%Y-%m', d.full_date) AS month,
        AVG(f.delivery_time_days) AS avg_delivery_days
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_DATES}` d
        ON f.order_date_key = d.date_key
    JOIN `{TABLE_CUSTOMERS}` c
        ON f.customer_id = c.customer_id
    WHERE TRUE {state_filter} {year_filter}
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

    # This query uses the customer state and year filter.
    state_filter = get_state_filter_sql_clause("c", selected_states)
    year_filter = get_year_filter_sql_clause("d", st.session_state.selected_years)
    sql_delivery_by_state = f"""
    SELECT
        c.customer_state,
        AVG(f.delivery_time_days) AS avg_delivery_days
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_DATES}` d
        ON f.order_date_key = d.date_key
    JOIN `{TABLE_CUSTOMERS}` c
        ON f.customer_id = c.customer_id
    WHERE TRUE {state_filter} {year_filter}
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
    state_filter = get_state_filter_sql_clause("c", selected_states)
    year_filter = get_year_filter_sql_clause("d", st.session_state.selected_years)
    sql_late_delivery = f"""
    SELECT
        CAST(SUM(CASE WHEN DATE(o.order_delivered_customer_date) > DATE(o.order_estimated_delivery_date) THEN 1 ELSE 0 END) AS FLOAT64) / COUNT(o.order_id) AS late_rate
    FROM `{TABLE_STG_ORDERS}` o
    JOIN `{TABLE_STG_CUSTOMERS}` c
        ON o.customer_id = c.customer_id
    JOIN `{TABLE_DATES}` d
        ON DATE(o.order_purchase_timestamp) = d.full_date
    WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL
    AND TRIM(o.order_delivered_customer_date) != ''
    AND o.order_estimated_delivery_date IS NOT NULL
    AND TRIM(o.order_estimated_delivery_date) != ''
    {state_filter} {year_filter}
    """
    df_late_delivery = run_query(sql_late_delivery)

    if not df_late_delivery.empty and 'late_rate' in df_late_delivery.columns:
        late_rate = df_late_delivery.iloc[0]['late_rate']
        st.metric("Late Delivery Rate", f"{late_rate:.2%}")
    else:
        st.warning("No data available to calculate the late delivery rate.")

    # New section for late orders breakdown
    st.subheader("Late Orders Breakdown")
    
    sql_late_breakdown = f"""
    SELECT
        FORMAT_DATE('%Y-%m', DATE(o.order_delivered_customer_date)) AS month,
        CASE
            WHEN DATE_DIFF(DATE(o.order_delivered_customer_date), DATE(o.order_estimated_delivery_date), DAY) <= 5 THEN '1-5 days late'
            WHEN DATE_DIFF(DATE(o.order_delivered_customer_date), DATE(o.order_estimated_delivery_date), DAY) <= 10 THEN '6-10 days late'
            WHEN DATE_DIFF(DATE(o.order_delivered_customer_date), DATE(o.order_estimated_delivery_date), DAY) <= 15 THEN '11-15 days late'
            WHEN DATE_DIFF(DATE(o.order_delivered_customer_date), DATE(o.order_estimated_delivery_date), DAY) <= 20 THEN '16-20 days late'
            ELSE '>20 days late'
        END AS days_late_category,
        COUNT(o.order_id) AS num_late_orders
    FROM `{TABLE_STG_ORDERS}` o
    JOIN `{TABLE_STG_CUSTOMERS}` c
        ON o.customer_id = c.customer_id
    JOIN `{TABLE_DATES}` d
        ON DATE(o.order_purchase_timestamp) = d.full_date
    WHERE
        o.order_status = 'delivered'
        AND o.order_delivered_customer_date IS NOT NULL
        AND TRIM(o.order_delivered_customer_date) != ''
        AND o.order_estimated_delivery_date IS NOT NULL
        AND TRIM(o.order_estimated_delivery_date) != ''
        AND DATE(o.order_delivered_customer_date) > DATE(o.order_estimated_delivery_date)
        {state_filter} {year_filter}
    GROUP BY 1, 2
    ORDER BY 1, 2
    """
    df_late_breakdown = run_query(sql_late_breakdown)

    if not df_late_breakdown.empty:
        category_order = ['1-5 days late', '6-10 days late', '11-15 days late', '16-20 days late', '>20 days late']
        color_map = {
            '1-5 days late': 'rgb(0, 0, 255)',      # Deep Blue
            '6-10 days late': 'rgb(173, 216, 230)', # Light Blue
            '11-15 days late': 'rgb(255, 215, 0)',  # Gold (Yellow)
            '16-20 days late': 'rgb(255, 69, 0)',   # Orange-Red
            '>20 days late': 'rgb(178, 34, 34)'     # Firebrick (Dark Red)
        }

        fig_breakdown = px.bar(
            df_late_breakdown,
            x="month",
            y="num_late_orders",
            color="days_late_category",
            category_orders={"days_late_category": category_order},
            color_discrete_map=color_map,
            title="Late Orders by Month and Days Late",
            labels={"month": "Month", "num_late_orders": "Number of Late Orders", "days_late_category": "Days Late"},
        )
        fig_breakdown.update_layout(barmode='stack')
        st.plotly_chart(fig_breakdown, use_container_width=True)
    else:
        st.warning("No data found for late order breakdown.")