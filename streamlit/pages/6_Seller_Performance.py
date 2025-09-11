import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from olist_report import (
    run_query, TABLE_FACT, TABLE_SELLERS, TABLE_DATES,
    create_year_filter, get_year_filter_sql_clause
)

# -------------------------
# Page Content
# -------------------------
st.title("Seller Performance & Reviews")

# Define state filter function within the app
def create_seller_state_filter():
    """Creates a multiselect filter for seller states."""
    sql_states = f"SELECT DISTINCT seller_state FROM `{TABLE_SELLERS}` ORDER BY seller_state"
    df_states = run_query(sql_states)
    all_states = df_states['seller_state'].tolist()
    return st.multiselect(
        "Filter by Seller State",
        all_states,
        default=all_states
    )

def get_seller_state_filter_sql_clause(alias, selected_states):
    """Generates the SQL WHERE clause for seller states."""
    if selected_states:
        states_tuple = tuple(selected_states)
        if len(states_tuple) == 1:
            return f"AND {alias}.seller_state = '{states_tuple[0]}'"
        else:
            return f"AND {alias}.seller_state IN {states_tuple}"
    return ""

# State and Year Filters (moved directly under the header)
selected_seller_states = create_seller_state_filter()
selected_years = create_year_filter(TABLE_DATES)
st.session_state.selected_seller_states = selected_seller_states
st.session_state.selected_years = selected_years

# Tabs
tab_insights, tab_top_sellers, tab_reviews = st.tabs(["Seller Insights", "Top Sellers", "Review Analysis"])

# --------------------------------
# Tab 1: Seller Insights
# --------------------------------
with tab_insights:
    st.header("Seller Insights")

    # Geospatial Heatmap for Total Revenue by Seller State
    st.subheader("Total Revenue by Seller State")

    state_filter = get_seller_state_filter_sql_clause("s", st.session_state.selected_seller_states)
    year_filter = get_year_filter_sql_clause("d", st.session_state.selected_years)
    sql_seller_revenue = f"""
    SELECT
        s.seller_state,
        SUM(SAFE_CAST(f.price AS FLOAT64)) AS total_revenue
    FROM `{TABLE_SELLERS}` s
    JOIN `{TABLE_FACT}` f
        ON s.seller_id = f.seller_id
    JOIN `{TABLE_DATES}` d
        ON f.order_date_key = d.date_key
    WHERE TRUE {state_filter} {year_filter}
    GROUP BY 1
    """
    df_seller_revenue = run_query(sql_seller_revenue)

    if not df_seller_revenue.empty:
        df_seller_revenue['seller_state'] = df_seller_revenue['seller_state'].str.upper()

        # Load Brazil states geojson
        geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
        response = requests.get(geojson_url)
        geojson = response.json() if response.status_code == 200 else None

        if geojson:
            custom_colorscale = [
                [0.0, "rgba(0,0,0,0)"], # transparent
                [0.001, "rgb(252,146,114)"], # A distinct red for the lowest non-zero values
                [0.2, "rgb(251,106,74)"],
                [0.4, "rgb(239,59,44)"],
                [0.6, "rgb(203,24,29)"],
                [1.0, "rgb(165,15,21)"]  # Darkest red
            ]

            df_seller_revenue['total_revenue_formatted'] = df_seller_revenue['total_revenue'].apply(lambda x: f"${x:,.2f}")

            fig_map = go.Figure(go.Choroplethmapbox(
                geojson=geojson,
                locations=df_seller_revenue['seller_state'],
                z=df_seller_revenue['total_revenue'],
                colorscale=custom_colorscale,
                zmin=0,
                zmax=df_seller_revenue['total_revenue'].max(),
                marker_opacity=0.6,
                marker_line_width=0.5,
                featureidkey="properties.sigla",
                hovertext=df_seller_revenue['seller_state'] + ': ' + df_seller_revenue['total_revenue_formatted'],
                hoverinfo='text',
                colorbar=dict(title="Total Revenue")
            ))
            fig_map.update_layout(
                mapbox_style="open-street-map",
                mapbox_zoom=3,
                mapbox_center = {"lat": -14.2350, "lon": -51.9253},
                margin={"r":0,"t":0,"l":0,"b":0},
                title="Total Revenue by Seller State"
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.error("Failed to load Brazil states geojson file.")
    else:
        st.warning("No data found for seller revenue with the current filter selection.")


    # Seller Distribution by State
    st.subheader("Seller Distribution & Performance by State")
    sql_seller_state_dist = f"""
    SELECT
        s.seller_state,
        COUNT(DISTINCT s.seller_id) AS num_sellers,
        AVG(SAFE_CAST(f.review_score AS FLOAT64)) AS avg_review_score,
        SUM(SAFE_CAST(f.price AS FLOAT64)) AS total_revenue
    FROM `{TABLE_SELLERS}` s
    LEFT JOIN `{TABLE_FACT}` f
        ON s.seller_id = f.seller_id
    LEFT JOIN `{TABLE_DATES}` d
        ON f.order_date_key = d.date_key
    WHERE 1=1
    {get_seller_state_filter_sql_clause("s", st.session_state.selected_seller_states)}
    {get_year_filter_sql_clause("d", st.session_state.selected_years)}
    GROUP BY 1
    ORDER BY num_sellers DESC
    """
    df_seller_state_dist = run_query(sql_seller_state_dist)

    if not df_seller_state_dist.empty:
        fig_state_dist = px.pie(
            df_seller_state_dist,
            names="seller_state",
            values="num_sellers",
            title="Sellers by State",
            hole=0.3
        )
        st.plotly_chart(fig_state_dist, use_container_width=True)

        fig_avg_revenue = px.bar(
            df_seller_state_dist.sort_values("total_revenue", ascending=False),
            x="total_revenue",
            y="seller_state",
            orientation="h",
            labels={"total_revenue": "Total Revenue", "seller_state": "Seller State"},
            title="Total Revenue by State"
        )
        st.plotly_chart(fig_avg_revenue, use_container_width=True)
    else:
        st.warning("No data found for seller state distribution.")


# --------------------------------
# Tab 2: Top Performing Sellers
# --------------------------------
with tab_top_sellers:
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
    JOIN `{TABLE_DATES}` d
        ON f.order_date_key = d.date_key
    WHERE 1=1
    {get_seller_state_filter_sql_clause("s", st.session_state.selected_seller_states)}
    {get_year_filter_sql_clause("d", st.session_state.selected_years)}
    GROUP BY 1, 2, 3
    ORDER BY total_revenue DESC
    LIMIT 100
    """
    df_seller_kpis = run_query(sql_seller_kpis)

    if not df_seller_kpis.empty:
        st.subheader("By Revenue")
        fig_revenue = px.bar(
            df_seller_kpis.head(10),
            x="total_revenue", y="seller_id",
            orientation="h",
            labels={"total_revenue": "Total Revenue", "seller_id": "Seller ID"}
        )
        st.plotly_chart(fig_revenue, use_container_width=True)

        st.subheader("By Number of Orders")
        fig_orders = px.bar(
            df_seller_kpis.sort_values("total_orders", ascending=False).head(10),
            x="total_orders", y="seller_id",
            orientation="h",
            labels={"total_orders": "Total Orders", "seller_id": "Seller ID"}
        )
        st.plotly_chart(fig_orders, use_container_width=True)

        st.subheader("By Average Review Score")
        fig_reviews = px.bar(
            df_seller_kpis.sort_values("avg_review_score", ascending=False).head(10),
            x="avg_review_score", y="seller_id",
            orientation="h",
            labels={"avg_review_score": "Avg. Review Score", "seller_id": "Seller ID"}
        )
        st.plotly_chart(fig_reviews, use_container_width=True)
    else:
        st.warning("No data found for seller KPIs.")

# --------------------------------
# Tab 3: Customer Review Analysis
# --------------------------------
with tab_reviews:
    st.header("Customer Review Analysis")

    # Review score distribution
    sql_review_dist = f"""
    SELECT
        SAFE_CAST(f.review_score AS INT64) AS review_score,
        COUNT(f.review_score) AS num_reviews
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_DATES}` d
        ON f.order_date_key = d.date_key
    JOIN `{TABLE_SELLERS}` s
        ON f.seller_id = s.seller_id
    WHERE f.review_score IS NOT NULL
    {get_seller_state_filter_sql_clause("s", st.session_state.selected_seller_states)}
    {get_year_filter_sql_clause("d", st.session_state.selected_years)}
    GROUP BY 1
    ORDER BY 1
    """
    df_review_dist = run_query(sql_review_dist)

    if not df_review_dist.empty:
        st.subheader("Review Score Distribution")
        fig_dist = px.bar(
            df_review_dist, x="review_score", y="num_reviews",
            labels={"review_score": "Review Score", "num_reviews": "Number of Reviews"}
        )
        st.plotly_chart(fig_dist, use_container_width=True)
    else:
        st.warning("No data found for review distribution.")

    # Average review score by seller state bar chart
    sql_review_by_state = f"""
    SELECT
        s.seller_state,
        AVG(SAFE_CAST(f.review_score AS FLOAT64)) AS avg_review_score
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_SELLERS}` s
        ON f.seller_id = s.seller_id
    JOIN `{TABLE_DATES}` d
        ON f.order_date_key = d.date_key
    WHERE f.review_score IS NOT NULL
    {get_seller_state_filter_sql_clause("s", st.session_state.selected_seller_states)}
    {get_year_filter_sql_clause("d", st.session_state.selected_years)}
    GROUP BY 1
    ORDER BY 2 DESC
    """
    df_review_by_state = run_query(sql_review_by_state)

    if not df_review_by_state.empty:
        st.subheader("Average Review Score by Seller State")

        # Geomap with transparent heatmap on average review score
        geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
        response = requests.get(geojson_url)
        geojson = response.json() if response.status_code == 200 else None
        
        if geojson:
            # Custom colorscale for reviews using a distinct, non-blue palette
            custom_colorscale_reviews = [
                [0.0, "rgba(0,0,0,0)"],
                [0.001, "rgb(255, 237, 160)"], # lightest yellow
                [0.2, "rgb(254, 204, 92)"],    # light orange
                [0.4, "rgb(253, 141, 60)"],    # orange
                [0.6, "rgb(240, 59, 32)"],     # red
                [1.0, "rgb(189, 0, 38)"]      # dark red
            ]
            
            df_review_by_state['avg_review_score_formatted'] = df_review_by_state['avg_review_score'].apply(lambda x: f"{x:,.2f}")
            
            fig_review_map = go.Figure(go.Choroplethmapbox(
                geojson=geojson,
                locations=df_review_by_state['seller_state'],
                z=df_review_by_state['avg_review_score'],
                colorscale=custom_colorscale_reviews,
                zmin=df_review_by_state['avg_review_score'].min(),
                zmax=df_review_by_state['avg_review_score'].max(),
                marker_opacity=0.6,
                marker_line_width=0.5,
                featureidkey="properties.sigla",
                hovertext=df_review_by_state['seller_state'] + ': ' + df_review_by_state['avg_review_score_formatted'],
                hoverinfo='text',
                colorbar=dict(title="Avg. Review Score")
            ))
            fig_review_map.update_layout(
                mapbox_style="open-street-map",
                mapbox_zoom=3,
                mapbox_center = {"lat": -14.2350, "lon": -51.9253},
                margin={"r":0,"t":0,"l":0,"b":0},
                title="Average Review Score by Seller State"
            )
            st.plotly_chart(fig_review_map, use_container_width=True)
        else:
            st.error("Failed to load Brazil states geojson file.")

        # Bar chart for review scores by state
        fig_state_rev = px.bar(
            df_review_by_state,
            x="avg_review_score", y="seller_state",
            orientation="h",
            labels={"avg_review_score": "Avg. Review Score", "seller_state": "Seller State"}
        )
        st.plotly_chart(fig_state_rev, use_container_width=True)
    else:
        st.warning("No data found for review scores by state.")
