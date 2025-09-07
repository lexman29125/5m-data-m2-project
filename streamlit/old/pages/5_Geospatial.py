# streamlit/pages/5_Geospatial.py

import streamlit as st
import pandas as pd
import plotly.express as px
import os
from olist_report import run_query, TABLE_FACT, TABLE_CUSTOMERS, TABLE_SELLERS, TABLE_GEOLOCATION, TABLE_STG_CUSTOMERS, TABLE_STG_SELLERS

# -------------------------
# Page Content
# -------------------------
st.title("Geospatial Analytics")

# Use tabs to organize content
tab1, tab2 = st.tabs(["Sales Heatmap", "Seller vs. Customer Locations"])

with tab1:
    st.header("Revenue by State")

    sql_sales_by_state = f"""
    SELECT
        c.customer_state,
        SUM(SAFE_CAST(f.price AS FLOAT64)) AS total_revenue
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_CUSTOMERS}` c
        ON f.customer_id = c.customer_id
    GROUP BY 1
    ORDER BY 2 DESC
    """
    df_sales_by_state = run_query(sql_sales_by_state)

    if not df_sales_by_state.empty:
        st.subheader("Total Revenue by State")
        fig_state = px.bar(df_sales_by_state, x="total_revenue", y="customer_state", orientation="h",
                           labels={"total_revenue": "Total Revenue", "customer_state": "Customer State"})
        st.plotly_chart(fig_state, use_container_width=True)
    else:
        st.warning("No data found for sales by state.")

with tab2:
    st.header("Geographic Distribution")

    # Corrected query for customer locations
    sql_customer_locations = f"""
    SELECT
        c.customer_unique_id,
        AVG(g.latitude) as lat,
        AVG(g.longitude) as lon
    FROM `{TABLE_CUSTOMERS}` c
    JOIN `{TABLE_STG_CUSTOMERS}` sc
        ON c.customer_id = sc.customer_id
    JOIN `{TABLE_GEOLOCATION}` g
        ON sc.customer_zip_code_prefix = g.geolocation_zip_code_prefix
    GROUP BY 1
    """
    df_customers = run_query(sql_customer_locations)
    
    # Corrected query for seller locations
    sql_seller_locations = f"""
    SELECT
        s.seller_id,
        AVG(g.latitude) as lat,
        AVG(g.longitude) as lon
    FROM `{TABLE_SELLERS}` s
    JOIN `{TABLE_STG_SELLERS}` ss
        ON s.seller_id = ss.seller_id
    JOIN `{TABLE_GEOLOCATION}` g
        ON ss.seller_zip_code_prefix = g.geolocation_zip_code_prefix
    GROUP BY 1
    """
    df_sellers = run_query(sql_seller_locations)

    if not df_customers.empty and not df_sellers.empty:
        df_customers['type'] = 'Customer'
        df_sellers['type'] = 'Seller'
        df_map_data = pd.concat([df_customers, df_sellers], ignore_index=True)

        # Removed the 'size' parameter to fix the TypeError
        fig_map = px.scatter_mapbox(df_map_data, lat="lat", lon="lon",
                                    color="type",
                                    zoom=3, height=500,
                                    labels={"type": "Location Type"},
                                    category_orders={"type": ["Customer", "Seller"]})
        
        fig_map.update_layout(mapbox_style="open-street-map")
        
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("No geospatial data found for plotting.")