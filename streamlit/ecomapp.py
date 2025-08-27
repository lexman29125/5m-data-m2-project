import os
import streamlit as st
import pandas as pd
import plotly.express as px
from google.cloud import bigquery
from math import radians, cos, sin, asin, sqrt

# -------------------------
# BigQuery Configuration
# -------------------------
KEY_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not KEY_PATH or not os.path.exists(KEY_PATH):
    st.error("BigQuery credentials not found. Set GOOGLE_APPLICATION_CREDENTIALS to your service account JSON path.")
    st.stop()

PROJECT_ID = "sound-vehicle-468314-q4"
DATASET_NAME = "m2_prod"
LOCATION = "US"

client = bigquery.Client.from_service_account_json(
    KEY_PATH,
    project=PROJECT_ID,
    location=LOCATION
)

# -------------------------
# Table references
# -------------------------
TABLE_FACT_ORDER_ITEMS = f"{PROJECT_ID}.{DATASET_NAME}.fact_order_items"
TABLE_DIM_CUSTOMERS = f"{PROJECT_ID}.{DATASET_NAME}.dim_customers"
TABLE_DIM_PRODUCTS = f"{PROJECT_ID}.{DATASET_NAME}.dim_products"
TABLE_DIM_SELLERS = f"{PROJECT_ID}.{DATASET_NAME}.dim_sellers"
TABLE_DIM_DATES = f"{PROJECT_ID}.{DATASET_NAME}.dim_dates"
TABLE_DIM_PAYMENTS = f"{PROJECT_ID}.{DATASET_NAME}.dim_payments"
TABLE_DIM_GEO = f"{PROJECT_ID}.{DATASET_NAME}.dim_geolocation"

# -------------------------
# Utility functions
# -------------------------
def haversine(lat1, lon1, lat2, lon2):
    # Calculate distance in km between two lat/lon points
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 6371 * 2 * asin(sqrt(a))

@st.cache_data(ttl=3600)
def query_bq(sql):
    df = client.query(sql).to_dataframe()
    return df

# -------------------------
# Sidebar filters
# -------------------------
st.sidebar.header("Filters")
date_range = st.sidebar.date_input("Order Date Range", [])
customer_state = st.sidebar.multiselect("Customer State", [])
payment_type = st.sidebar.multiselect("Payment Type", [])

# -------------------------
# Build WHERE clause dynamically
# -------------------------
filters = []
if date_range and len(date_range) == 2:
    filters.append(f"order_date_key BETWEEN {int(date_range[0].strftime('%Y%m%d'))} AND {int(date_range[1].strftime('%Y%m%d'))}")
if customer_state:
    states = ", ".join([f"'{s}'" for s in customer_state])
    filters.append(f"customer_state IN ({states})")
if payment_type:
    types = ", ".join([f"'{p}'" for p in payment_type])
    filters.append(f"payment_type_key IN ({types})")

where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

# -------------------------
# Load fact + dimensions
# -------------------------
sql_fact = f"""
SELECT f.*, c.customer_state, s.seller_state
FROM `{TABLE_FACT_ORDER_ITEMS}` f
LEFT JOIN `{TABLE_DIM_CUSTOMERS}` c ON f.customer_id = c.customer_id
LEFT JOIN `{TABLE_DIM_SELLERS}` s ON f.seller_id = s.seller_id
{where_clause}
"""
df_fact = query_bq(sql_fact)

# Fix data types for numeric calculations
df_fact["price"] = pd.to_numeric(df_fact["price"], errors="coerce").fillna(0)
df_fact["review_score"] = pd.to_numeric(df_fact["review_score"], errors="coerce")

st.title("Olist E-Commerce Dashboard")

# -------------------------
# KPIs
# -------------------------
st.subheader("Key Metrics")
total_orders = len(df_fact)
total_revenue = df_fact["price"].sum()
average_review_score = df_fact["review_score"].mean() if not df_fact.empty else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Orders", total_orders)
col2.metric("Total Revenue", f"${total_revenue:,.2f}")
col3.metric("Average Review Score", f"{average_review_score:.2f}")

# -------------------------
# Revenue by Review Score
# -------------------------
st.subheader("Revenue by Review Score")
rev_by_score = df_fact.groupby("review_score")["price"].sum().reset_index()
fig_rev = px.bar(
    rev_by_score,
    x="review_score",
    y="price",
    labels={"price": "Revenue", "review_score": "Review Score"},
    title="Revenue by Review Score"
)
st.plotly_chart(fig_rev, use_container_width=True)

# -------------------------
# Delivery Time Distribution
# -------------------------
st.subheader("Delivery Time Distribution (Days)")
fig_del = px.histogram(
    df_fact,
    x="delivery_time_days",
    nbins=30,
    labels={"delivery_time_days": "Delivery Time (days)"},
    title="Delivery Time Distribution"
)
st.plotly_chart(fig_del, use_container_width=True)

# -------------------------
# Top Products
# -------------------------
st.subheader("Top Products by Revenue")
sql_top_products = f"""
SELECT p.product_category_name_english AS category, SUM(CAST(f.price AS FLOAT64)) AS revenue
FROM `{TABLE_FACT_ORDER_ITEMS}` f
LEFT JOIN `{TABLE_DIM_PRODUCTS}` p ON f.product_id = p.product_id
{where_clause}
GROUP BY category
ORDER BY revenue DESC
LIMIT 10
"""
df_top = query_bq(sql_top_products)
fig_top = px.bar(
    df_top,
    x="category",
    y="revenue",
    labels={"revenue":"Revenue", "category":"Product Category"},
    title="Top 10 Product Categories by Revenue"
)
st.plotly_chart(fig_top, use_container_width=True)

# -------------------------
# Geospatial Maps
# -------------------------
st.subheader("Customer & Seller Locations")

sql_geo = f"""
SELECT c.customer_id, c.customer_city, c.customer_state, c.latitude AS cust_lat, c.longitude AS cust_lon,
       s.seller_id, s.seller_city, s.seller_state, s.latitude AS seller_lat, s.longitude AS seller_lon
FROM `{TABLE_FACT_ORDER_ITEMS}` f
LEFT JOIN `{TABLE_DIM_CUSTOMERS}` c ON f.customer_id = c.customer_id
LEFT JOIN `{TABLE_DIM_SELLERS}` s ON f.seller_id = s.seller_id
{where_clause}
"""
df_geo = query_bq(sql_geo)

fig_map = px.scatter_mapbox(
    df_geo, lat="cust_lat", lon="cust_lon",
    hover_name="customer_id",
    color_discrete_sequence=["blue"],
    zoom=3,
    height=400,
    title="Customer Locations"
)
fig_map.add_scattermapbox(
    lat=df_geo["seller_lat"],
    lon=df_geo["seller_lon"],
    mode="markers",
    marker=dict(color="red", size=8),
    text=df_geo["seller_id"],
    name="Sellers"
)
fig_map.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig_map, use_container_width=True)

# -------------------------
# Delivery Routes Map
# -------------------------
st.subheader("Delivery Routes")
sample_size = st.slider("Max routes to display", min_value=100, max_value=1000, value=200, step=50)
df_routes = df_geo.head(sample_size).copy()
df_routes["distance_km"] = df_routes.apply(
    lambda row: haversine(row.seller_lat, row.seller_lon, row.cust_lat, row.cust_lon),
    axis=1
)

# To plot lines on mapbox, build lines as scatter traces (one per route)
import plotly.graph_objects as go

fig_routes = go.Figure()

for _, row in df_routes.iterrows():
    fig_routes.add_trace(go.Scattermapbox(
        mode="lines+markers",
        lat=[row["seller_lat"], row["cust_lat"]],
        lon=[row["seller_lon"], row["cust_lon"]],
        line=dict(width=2, color=px.colors.sequential.Viridis[int(row["distance_km"]) % len(px.colors.sequential.Viridis)]),
        marker=dict(size=6),
        hoverinfo="text",
        text=f"Distance: {row['distance_km']:.2f} km<br>Customer ID: {row['customer_id']}"
    ))

fig_routes.update_layout(
    mapbox=dict(style="open-street-map", zoom=3, center={"lat": df_routes["cust_lat"].mean(), "lon": df_routes["cust_lon"].mean()}),
    height=500,
    margin={"r":0,"t":0,"l":0,"b":0},
    title="Delivery Routes with Distances"
)
st.plotly_chart(fig_routes, use_container_width=True)

# -------------------------
# Data download
# -------------------------
st.subheader("Download Filtered Data")
csv = df_fact.to_csv(index=False)
st.download_button("Download CSV", data=csv, file_name="olist_filtered_data.csv", mime="text/csv")
