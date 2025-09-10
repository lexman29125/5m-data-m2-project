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

# Query for RFM, which is used in both tabs
state_filter = get_state_filter_sql_clause("c", selected_states)
year_filter = get_year_filter_sql_clause("d", st.session_state.selected_years)
sql_rfm = f"""
SELECT
    c.customer_unique_id,
    DATE_DIFF(CURRENT_DATE(), MAX(d.full_date), DAY) AS Recency,
    COUNT(DISTINCT f.order_id) AS Frequency,
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

with tab1:
    st.header("Overall Customer Metrics")
    
    # Calculate and display metrics
    total_customers = df_rfm.shape[0] if not df_rfm.empty else 0
    total_orders = df_rfm['Frequency'].sum() if not df_rfm.empty else 0
    avg_orders_per_customer = df_rfm['Frequency'].mean() if not df_rfm.empty else 0
    
    # Use st.columns to display metrics in a row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Unique Customers", f"{total_customers:,}")
    
    with col2:
        st.metric("Total Unique Orders", f"{total_orders:,}")
    
    with col3:
        st.metric("Average Orders per Customer", f"{avg_orders_per_customer:.2f}")

    # Add the bar chart for order frequency
    if not df_rfm.empty:
        st.subheader("Frequency of Unique Orders Per Customer")
        fig_frequency = px.histogram(df_rfm, x="Frequency",
                                     title="Distribution of Order Frequency",
                                     labels={"Frequency": "Number of Unique Orders"})
        st.plotly_chart(fig_frequency, use_container_width=True)
    else:
        st.warning("No data found for the customer overview.")

with tab2:
    st.header("Customer Segmentation (RFM)")
    
    if not df_rfm.empty:
        # Create RFM segments (simplified for this example)
        # Using .rank(method='first', pct=True) to avoid issues with duplicates
        df_rfm['R_Score'] = df_rfm['Recency'].rank(method='first', pct=True, ascending=False)
        df_rfm['F_Score'] = df_rfm['Frequency'].rank(method='first', pct=True)
        df_rfm['M_Score'] = df_rfm['Monetary'].rank(method='first', pct=True)

        # Plot the distribution of RFM scores
        st.subheader("RFM Score Distribution")
        fig_rfm = px.scatter(df_rfm, x='Frequency', y='Monetary', color='R_Score',
                             labels={'Frequency': 'Frequency (Orders)', 'Monetary': 'Monetary (Revenue)', 'R_Score': 'Recency Score'},
                             hover_name='customer_unique_id',
                             title="RFM Analysis Scatter Plot")
        st.plotly_chart(fig_rfm, use_container_width=True)
    else:
        st.warning("No data found for RFM analysis with the current filter selection.")