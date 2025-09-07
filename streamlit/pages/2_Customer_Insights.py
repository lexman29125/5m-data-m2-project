# streamlit/pages/2_Customer_Insights.py

import streamlit as st
import pandas as pd
import plotly.express as px
from olist_report import run_query, TABLE_FACT, TABLE_CUSTOMERS, TABLE_DATES, create_state_filter, get_state_filter_sql_clause, create_year_filter, get_year_filter_sql_clause

# -------------------------
# Page Content
# -------------------------
st.title("Customer Insights")

# Create the customer state filter UI
selected_states = create_state_filter(TABLE_CUSTOMERS)
selected_years = create_year_filter(TABLE_DATES)
st.session_state.selected_states = selected_states
st.session_state.selected_years = selected_years

# Use tabs for different sections of analysis
tab1, tab2 = st.tabs(["Customer Overview", "Customer Segmentation"])

with tab1:
    st.header("Overall Customer Metrics")
    
    # Apply the state filter and year filter to this query.
    state_filter = get_state_filter_sql_clause("c", selected_states)
    year_filter = get_year_filter_sql_clause("d", st.session_state.selected_years)
    sql_total_customers = f"""
    SELECT COUNT(DISTINCT c.customer_unique_id) AS total_customers
    FROM `{TABLE_CUSTOMERS}` c
    JOIN `{TABLE_FACT}` f ON f.customer_id = c.customer_id
    JOIN `{TABLE_DATES}` d ON f.order_date_key = d.date_key
    WHERE TRUE {state_filter} {year_filter}
    """
    df_total_customers = run_query(sql_total_customers)
    
    total_customers = df_total_customers.iloc[0]['total_customers'] if not df_total_customers.empty else 0
    st.metric("Total Unique Customers", f"{total_customers:,}")

with tab2:
    st.header("Customer Segmentation (RFM Analysis)")

    # SQL query to get RFM data
    state_filter = get_state_filter_sql_clause("c", selected_states)
    year_filter = get_year_filter_sql_clause("d", st.session_state.selected_years)
    sql_rfm = f"""
    SELECT
        c.customer_unique_id,
        DATE_DIFF(CURRENT_DATE(), MAX(d.full_date), DAY) AS Recency,
        COUNT(f.order_id) AS Frequency,
        SUM(SAFE_CAST(f.price AS FLOAT64)) AS Monetary
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_CUSTOMERS}` c
        ON f.customer_id = c.customer_id
    JOIN `{TABLE_DATES}` d
        ON f.order_date_key = d.date_key
    WHERE TRUE {state_filter} {year_filter}
    GROUP BY c.customer_unique_id
    """

    df_rfm = run_query(sql_rfm)

    if not df_rfm.empty:
        # Create RFM segments (simplified for this example)
        # Using .rank(method='first', pct=True) to avoid issues with duplicates
        df_rfm['R_Score'] = df_rfm['Recency'].rank(method='first', pct=True)
        df_rfm['F_Score'] = df_rfm['Frequency'].rank(method='first', pct=True)
        df_rfm['M_Score'] = df_rfm['Monetary'].rank(method='first', pct=True)

        # Plot the distribution of RFM scores
        st.subheader("RFM Score Distribution")
        fig_rfm = px.scatter(df_rfm, x='Frequency', y='Monetary', color='R_Score', 
                             hover_name='customer_unique_id',
                             labels={'R_Score': 'Recency (Days Since Last Order)', 'Frequency': 'Number of Orders', 'Monetary': 'Total Spend'})
        st.plotly_chart(fig_rfm, use_container_width=True)
    else:
        st.warning("No data available for RFM analysis.")