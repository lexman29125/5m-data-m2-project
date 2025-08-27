import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.cloud import bigquery
from math import radians, cos, sin, asin, sqrt

# -------------------------
# Setup
# -------------------------
st.set_page_config(page_title="Olist E‑Commerce Dashboard", layout="wide")

KEY_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not KEY_PATH or not os.path.exists(KEY_PATH):
    st.error("Set GOOGLE_APPLICATION_CREDENTIALS to your service account JSON path.")
    st.stop()

client = bigquery.Client.from_service_account_json(KEY_PATH)

PROJECT_ID = "sound-vehicle-468314-q4"
DATASET = "m2_prod"
TABLE_FACT = f"{PROJECT_ID}.{DATASET}.fact_order_items"
TABLE_CUSTOMERS = f"{PROJECT_ID}.{DATASET}.dim_customers"
TABLE_PRODUCTS = f"{PROJECT_ID}.{DATASET}.dim_products"
TABLE_SELLERS = f"{PROJECT_ID}.{DATASET}.dim_sellers"
TABLE_PAYMENTS = f"{PROJECT_ID}.{DATASET}.dim_payments"

@st.cache_data(ttl=3600)
def query(sql: str) -> pd.DataFrame:
    return client.query(sql).to_dataframe()

@st.cache_data(ttl=3600)
def get_options():
    states = query(f"SELECT DISTINCT customer_state FROM `{TABLE_CUSTOMERS}` WHERE customer_state IS NOT NULL ORDER BY customer_state")["customer_state"].tolist()
    payments = query(f"SELECT DISTINCT payment_type FROM `{TABLE_PAYMENTS}` WHERE payment_type IS NOT NULL ORDER BY payment_type")["payment_type"].tolist()
    return states, payments

states, payments = get_options()

# -------------------------
# Sidebar Filters
# -------------------------
st.sidebar.header("Filters")

date_range = st.sidebar.date_input("Order Date Range", [])
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = None, None

selected_states = st.sidebar.multiselect("Customer State", states, default=states)
selected_payments = st.sidebar.multiselect("Payment Type", payments, default=payments)

conditions = []
if start_date and end_date:
    conditions.append(f"CAST(order_date_key AS STRING) BETWEEN '{start_date.strftime('%Y%m%d')}' AND '{end_date.strftime('%Y%m%d')}'")
if selected_states:
    state_list = ", ".join(f"'{state}'" for state in selected_states)
    conditions.append(f"c.customer_state IN ({state_list})")
if selected_payments:
    payment_list = ", ".join(f"'{ptype}'" for ptype in selected_payments)
    conditions.append(f"p.payment_type IN ({payment_list})")
where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

# -------------------------
# Data Query
# -------------------------
sql_main = f"""
SELECT
  f.order_id,
  f.price,
  f.review_score,
  f.delivery_time_days,
  c.customer_state,
  p.payment_type,
  pr.product_category_name_english AS product_category,
  s.latitude AS seller_lat, s.longitude AS seller_lon,
  c.latitude AS cust_lat, c.longitude AS cust_lon
FROM `{TABLE_FACT}` f
LEFT JOIN `{TABLE_CUSTOMERS}` c ON f.customer_id = c.customer_id
LEFT JOIN `{TABLE_PAYMENTS}` p ON f.payment_type_key = p.payment_type_key
LEFT JOIN `{TABLE_PRODUCTS}` pr ON f.product_id = pr.product_id
LEFT JOIN `{TABLE_SELLERS}` s ON f.seller_id = s.seller_id
{where_clause}
"""
df = query(sql_main)

# Clean types
df["price"] = pd.to_numeric(df["price"], errors="coerce")
df["review_score"] = pd.to_numeric(df["review_score"], errors="coerce")
df["delivery_time_days"] = pd.to_numeric(df["delivery_time_days"], errors="coerce")
df = df.dropna(subset=["cust_lat", "cust_lon", "seller_lat", "seller_lon"])

# -------------------------
# KPIs
# -------------------------
st.title("Olist E‑Commerce Dashboard")

total_orders = len(df)
total_revenue = df["price"].sum()
avg_review = df["review_score"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Total Orders", f"{total_orders:,}")
col2.metric("Total Revenue", f"${total_revenue:,.2f}")
col3.metric("Avg Review Score", f"{avg_review:.2f}")

# -------------------------
# Delivery Time Distribution
# -------------------------
st.subheader("Delivery Time Distribution (Days)")
fig_deliv = px.histogram(df, x="delivery_time_days", nbins=30,
                         labels={"delivery_time_days": "Delivery Days"})
st.plotly_chart(fig_deliv, use_container_width=True)

# -------------------------
# Top Products by Revenue
# -------------------------
st.subheader("Top Products by Revenue")
top_products = (
    df.groupby("product_category")["price"]
    .sum()
    .reset_index()
    .sort_values("price", ascending=False)
    .head(10)
)
fig_top = px.bar(top_products, x="product_category", y="price",
                 labels={"product_category": "Category", "price": "Revenue"})
st.plotly_chart(fig_top, use_container_width=True)

# -------------------------
# Revenue by Review Score
# -------------------------
st.subheader("Revenue by Review Score")
rev_by_review = df.groupby("review_score")["price"].sum().reset_index()
fig_review = px.bar(rev_by_review, x="review_score", y="price",
                    labels={"review_score": "Review Score", "price": "Revenue"})
st.plotly_chart(fig_review, use_container_width=True)

# -------------------------
# Map: Customer & Seller Locations
# -------------------------
st.subheader("Customer & Seller Locations")
fig_map = px.scatter_mapbox(df, lat="cust_lat", lon="cust_lon", color_discrete_sequence=["blue"],
                            zoom=3, height=400, hover_name="order_id")
fig_map.add_scattermapbox(lat=df["seller_lat"], lon=df["seller_lon"],
                          mode="markers", marker=dict(color="red", size=6),
                          name="Sellers", hovertext=df["order_id"])
fig_map.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig_map, use_container_width=True)

# -------------------------
# Delivery Route Map
# -------------------------
def haversine(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon, dlat = lon2 - lon1, lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 6371 * 2 * asin(sqrt(a))

st.subheader("Delivery Routes")
sample_size = st.slider("Max Routes to Display", min_value=100, max_value=1000, value=200, step=100)
df_sample = df.head(sample_size).copy()
df_sample["distance_km"] = df_sample.apply(
    lambda x: haversine(x.seller_lat, x.seller_lon, x.cust_lat, x.cust_lon), axis=1
)

fig_routes = go.Figure()
for _, row in df_sample.iterrows():
    fig_routes.add_trace(go.Scattermapbox(
        mode="lines",
        lon=[row.seller_lon, row.cust_lon],
        lat=[row.seller_lat, row.cust_lat],
        line=dict(width=2, color="orange"),
        hoverinfo="text",
        text=f"{row.order_id} - {row.distance_km:.1f} km"
    ))
fig_routes.update_layout(mapbox=dict(
    style="open-street-map",
    zoom=3,
    center=dict(lat=df_sample.cust_lat.mean(), lon=df_sample.cust_lon.mean())
), height=500, margin=dict(l=0, r=0, t=30, b=0))
st.plotly_chart(fig_routes, use_container_width=True)

# -------------------------
# Download CSV
# -------------------------
st.subheader("Download Filtered Data")
if not df.empty:
    csv = df.to_csv(index=False)
    st.download_button("Download CSV", data=csv, file_name="olist_filtered_data.csv", mime="text/csv")
else:
    st.warning("No data found for selected filters.")
