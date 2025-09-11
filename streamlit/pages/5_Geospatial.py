# streamlit/pages/5_Geospatial.py

import streamlit as st
import pandas as pd
import plotly.express as px
import os
import plotly.graph_objects as go
import requests

from olist_report import (
    run_query, TABLE_FACT, TABLE_CUSTOMERS, TABLE_SELLERS, TABLE_GEOLOCATION,
    TABLE_STG_CUSTOMERS, TABLE_STG_SELLERS, haversine,
    create_state_filter, get_state_filter_sql_clause,
    create_year_filter, get_year_filter_sql_clause,
    TABLE_DATES, TABLE_STG_ORDERS
)

# -------------------------
# Page Content
# -------------------------
st.title("Geospatial Analytics")

# Create filters
selected_states = create_state_filter(TABLE_CUSTOMERS)
selected_years = create_year_filter(TABLE_DATES)
st.session_state.selected_states = selected_states
st.session_state.selected_years = selected_years

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "State Spending Heatmap",
    "Customer Spending Locations",
    "Seller vs. Customer Locations",
    "Delivery Routes"
])

# -------------------------
# TAB 1 - State Spending Heatmap
# -------------------------
with tab1:
    st.header("State Spending Distribution")
    
    state_filter = get_state_filter_sql_clause("c", st.session_state.selected_states)
    year_filter = get_year_filter_sql_clause("d", st.session_state.selected_years)
    sql_state_spending = f"""
    SELECT
        c.customer_state,
        SUM(SAFE_CAST(f.price AS FLOAT64)) AS total_spent
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_CUSTOMERS}` c
        ON f.customer_id = c.customer_id
    JOIN `{TABLE_DATES}` d
        ON f.order_date_key = d.date_key
    WHERE TRUE {state_filter} {year_filter}
    GROUP BY 1
    """
    df_state_spending = run_query(sql_state_spending)

    if not df_state_spending.empty:
        df_state_spending['customer_state'] = df_state_spending['customer_state'].str.upper()

        # Load Brazil states geojson
        geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
        response = requests.get(geojson_url)
        geojson = response.json() if response.status_code == 200 else None

        if geojson:
            # Custom color scale: transparent for 0, then a darker red for low values
            # and smoothly transitioning to a darker red for high values.
            custom_colorscale = [
                [0.0, "rgba(0,0,0,0)"], # transparent
                [0.001, "rgb(252,146,114)"], # A distinct red for the lowest non-zero values
                [0.2, "rgb(251,106,74)"],
                [0.4, "rgb(239,59,44)"],
                [0.6, "rgb(203,24,29)"],
                [1.0, "rgb(165,15,21)"]   # Darkest red
            ]

            # Format the total_spent column with commas and a dollar sign for the hover text
            df_state_spending['total_spent_formatted'] = df_state_spending['total_spent'].apply(lambda x: f"${x:,.2f}")
            
            fig_map = go.Figure(go.Choroplethmapbox(
                geojson=geojson,
                locations=df_state_spending['customer_state'],
                z=df_state_spending['total_spent'],
                colorscale=custom_colorscale,
                zmin=0,
                zmax=df_state_spending['total_spent'].max(),
                marker_opacity=0.6,
                marker_line_width=0.5,
                featureidkey="properties.sigla",
                # Use the new formatted column for the hover text
                hovertext=df_state_spending['customer_state'] + ': ' + df_state_spending['total_spent_formatted'],
                hoverinfo='text',
                colorbar=dict(title="Total Spending")
            ))
            fig_map.update_layout(
                mapbox_style="open-street-map",
                mapbox_zoom=3,
                mapbox_center = {"lat": -14.2350, "lon": -51.9253},
                margin={"r":0,"t":0,"l":0,"b":0},
                title="Total Spending by State (Transparent Overlay)"
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.error("Failed to load Brazil states geojson file.")
    else:
        st.warning("No data found for state spending with the current filter selection.")


# -------------------------
# TAB 2 - Customer Spending Locations
# -------------------------
with tab2:
    st.header("Customer Spending Distribution")

    state_filter = get_state_filter_sql_clause("c", st.session_state.selected_states)
    year_filter = get_year_filter_sql_clause("d", st.session_state.selected_years)
    sql_customer_locations = f"""
    SELECT
        c.customer_unique_id,
        AVG(g.latitude) as lat,
        AVG(g.longitude) as lon,
        SUM(SAFE_CAST(f.price AS FLOAT64)) AS total_spent
    FROM `{TABLE_CUSTOMERS}` c
    JOIN `{TABLE_STG_CUSTOMERS}` sc
        ON c.customer_id = sc.customer_id
    JOIN `{TABLE_GEOLOCATION}` g
        ON sc.customer_zip_code_prefix = g.geolocation_zip_code_prefix
    JOIN `{TABLE_FACT}` f
        ON c.customer_id = f.customer_id
    JOIN `{TABLE_DATES}` d
        ON f.order_date_key = d.date_key
    WHERE TRUE {state_filter} {year_filter}
    GROUP BY 1
    """
    df_customers = run_query(sql_customer_locations)
    
    if not df_customers.empty:
        st.subheader("Customer Locations by Total Spending")
        fig_cust_loc = px.scatter_mapbox(
            df_customers,
            lat="lat",
            lon="lon",
            size="total_spent",
            size_max=15,
            hover_name="customer_unique_id",
            hover_data={"total_spent": ':.2f'},
            color_continuous_scale=px.colors.sequential.Viridis,
            zoom=3,
            height=500
        )
        fig_cust_loc.update_layout(mapbox_style="carto-positron")
        st.plotly_chart(fig_cust_loc, use_container_width=True)
    else:
        st.warning("No data found for customer locations with the current filter selection.")


# -------------------------
# TAB 3 - Seller vs Customer Locations
# -------------------------
with tab3:
    st.header("Geographic Distribution")

    state_filter = get_state_filter_sql_clause("c", st.session_state.selected_states)
    year_filter = get_year_filter_sql_clause("d", st.session_state.selected_years)
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
    JOIN `{TABLE_FACT}` f
        ON c.customer_id = f.customer_id
    JOIN `{TABLE_DATES}` d
        ON f.order_date_key = d.date_key
    WHERE TRUE {state_filter} {year_filter}
    GROUP BY 1
    """
    df_customers = run_query(sql_customer_locations)

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
    JOIN `{TABLE_FACT}` f
        ON s.seller_id = f.seller_id
    JOIN `{TABLE_DATES}` d
        ON f.order_date_key = d.date_key
    WHERE TRUE {year_filter}
    GROUP BY 1
    """
    df_sellers = run_query(sql_seller_locations)

    if not df_customers.empty and not df_sellers.empty:
        df_customers['type'] = 'Customer'
        df_sellers['type'] = 'Seller'
        df_map_data = pd.concat([df_customers, df_sellers], ignore_index=True)

        fig_map = px.scatter_mapbox(
            df_map_data,
            lat="lat",
            lon="lon",
            color="type",
            zoom=3,
            height=500,
            labels={"type": "Location Type"},
            category_orders={"type": ["Customer", "Seller"]}
        )
        fig_map.update_layout(mapbox_style="open-street-map")
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("No geospatial data found for plotting with the current filter selection.")


# -------------------------
# TAB 4 - Delivery Routes
# -------------------------
with tab4:
    st.header("Delivery Routes")

    state_filter = get_state_filter_sql_clause("t6", st.session_state.selected_states)
    year_filter = get_year_filter_sql_clause("d", st.session_state.selected_years)
    sql_delivery_routes = f"""
    SELECT
        t1.order_id,
        t1.seller_id,
        t1.customer_id,
        t2.latitude AS seller_lat,
        t2.longitude AS seller_lon,
        t3.latitude AS cust_lat,
        t3.longitude AS cust_lon
    FROM `{TABLE_FACT}` AS t1
    JOIN `{TABLE_SELLERS}` AS t4 ON t1.seller_id = t4.seller_id
    JOIN `{TABLE_STG_SELLERS}` AS t5 ON t4.seller_id = t5.seller_id
    JOIN `{TABLE_GEOLOCATION}` AS t2 ON t5.seller_zip_code_prefix = t2.geolocation_zip_code_prefix
    JOIN `{TABLE_CUSTOMERS}` AS t6 ON t1.customer_id = t6.customer_id
    JOIN `{TABLE_STG_CUSTOMERS}` AS t7 ON t6.customer_id = t7.customer_id
    JOIN `{TABLE_GEOLOCATION}` AS t3 ON t7.customer_zip_code_prefix = t3.geolocation_zip_code_prefix
    JOIN `{TABLE_DATES}` AS d ON t1.order_date_key = d.date_key
    WHERE t1.order_id IS NOT NULL AND t1.price > 0 {state_filter} {year_filter}
    LIMIT 1000
    """
    df_routes = run_query(sql_delivery_routes)
    
    if not df_routes.empty:
        df_routes['distance_km'] = df_routes.apply(
            lambda x: haversine(x.seller_lat, x.seller_lon, x.cust_lat, x.cust_lon), axis=1
        )

        # Get nearest and furthest routes
        min_distance = df_routes['distance_km'].min()
        max_distance = df_routes['distance_km'].max()
        
        # Display the distances
        st.info(f"The nearest delivery route is **{min_distance:.1f} km**.")
        st.info(f"The furthest delivery route is **{max_distance:.1f} km**.")

        st.subheader("Interactive Map of Delivery Routes")
        sample_size = st.slider("Max Routes to Display", min_value=50, max_value=len(df_routes), value=200, step=50)
        df_sample = df_routes.head(sample_size).copy()

        fig_routes = go.Figure()
        for _, row in df_sample.iterrows():
            fig_routes.add_trace(go.Scattermapbox(
                mode="lines",
                lon=[row.seller_lon, row.cust_lon],
                lat=[row.seller_lat, row.cust_lat],
                line=dict(width=2, color="orange"),
                hoverinfo="text",
                text=f"Order ID: {row.order_id}<br>Distance: {row.distance_km:.1f} km"
            ))
        fig_routes.update_layout(
            mapbox=dict(
                style="open-street-map",
                zoom=3,
                center={"lat": df_routes.cust_lat.mean(), "lon": df_routes.cust_lon.mean()}
            ),
            margin={"r":0,"t":0,"l":0,"b":0}
        )
        st.plotly_chart(fig_routes, use_container_width=True)
    else:
        st.warning("No data found for delivery routes with the current filter selection.")