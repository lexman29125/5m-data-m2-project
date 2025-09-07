# streamlit/pages/8_Customer_Analytics.py

import streamlit as st
import pandas as pd
import plotly.express as px
from olist_report import (
    run_query,
    TABLE_CUSTOMERS,
    TABLE_FACT,
    create_state_filter,
    get_state_filter_sql_clause,
    create_year_filter,
    get_year_filter_sql_clause,
    TABLE_DATES,
)

# -------------------------
# Page Content
# -------------------------
st.title("Customer Analytics")

# Create the customer state and year filters UI
selected_states = create_state_filter(TABLE_CUSTOMERS)
selected_years = create_year_filter(TABLE_DATES)
st.session_state.selected_states = selected_states
st.session_state.selected_years = selected_years

# Use tabs to organize content
tab1, tab2 = st.tabs(["Customer Demographics", "Order Behavior"])

with tab1:
    st.header("Customer Demographics")

    # Query for unique customers by state (with year filter)
    state_filter = get_state_filter_sql_clause("c", selected_states)
    year_filter = get_year_filter_sql_clause("d", st.session_state.selected_years)
    sql_customers_by_state = f"""
    SELECT
        c.customer_state,
        COUNT(DISTINCT c.customer_unique_id) AS total_customers
    FROM `{TABLE_CUSTOMERS}` c
    JOIN `{TABLE_FACT}` f ON c.customer_id = f.customer_id
    JOIN `{TABLE_DATES}` d ON f.order_date_key = d.date_key
    WHERE TRUE {state_filter} {year_filter}
    GROUP BY 1
    ORDER BY total_customers DESC
    """
    df_customers_by_state = run_query(sql_customers_by_state)

    if not df_customers_by_state.empty:
        st.subheader("Total Unique Customers by State")
        fig_customers = px.bar(df_customers_by_state, x="total_customers", y="customer_state", orientation="h",
                               labels={"total_customers": "Total Unique Customers", "customer_state": "Customer State"})
        st.plotly_chart(fig_customers, use_container_width=True)
    else:
        st.warning("No data found for customer demographics with the current filter selection.")

with tab2:
    st.header("Customer Order Behavior")
    
    # Query for orders per customer (with year filter)
    state_filter = get_state_filter_sql_clause("c", selected_states)
    year_filter = get_year_filter_sql_clause("d", st.session_state.selected_years)
    sql_orders_per_customer = f"""
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT f.order_id) AS total_orders
    FROM `{TABLE_CUSTOMERS}` c
    JOIN `{TABLE_FACT}` f ON c.customer_id = f.customer_id
    JOIN `{TABLE_DATES}` d ON f.order_date_key = d.date_key
    WHERE TRUE {state_filter} {year_filter}
    GROUP BY 1
    """
    df_orders_per_customer = run_query(sql_orders_per_customer)
    
    if not df_orders_per_customer.empty:
        st.subheader("Orders Per Customer")
        fig_orders_dist = px.histogram(df_orders_per_customer, x="total_orders", nbins=20,
                                       labels={"total_orders": "Number of Orders"})
        st.plotly_chart(fig_orders_dist, use_container_width=True)
    else:
        st.warning("No data found for orders per customer with the current filter selection.")

    # Query for average spending per customer (with year filter)
    state_filter = get_state_filter_sql_clause("c", selected_states)
    year_filter = get_year_filter_sql_clause("d", st.session_state.selected_years)
    sql_avg_spending = f"""
    SELECT
        c.customer_unique_id,
        SUM(SAFE_CAST(f.price AS FLOAT64)) AS total_spent
    FROM `{TABLE_CUSTOMERS}` c
    JOIN `{TABLE_FACT}` f ON c.customer_id = f.customer_id
    JOIN `{TABLE_DATES}` d ON f.order_date_key = d.date_key
    WHERE TRUE {state_filter} {year_filter}
    GROUP BY 1
    """
    df_avg_spending = run_query(sql_avg_spending)

    if not df_avg_spending.empty:
        st.subheader("Total Spending Per Customer")
        fig_spending_dist = px.histogram(df_avg_spending, x="total_spent", nbins=50,
                                         labels={"total_spent": "Total Spending"})
        st.plotly_chart(fig_spending_dist, use_container_width=True)
    else:
        st.warning("No data found for customer spending with the current filter selection.")