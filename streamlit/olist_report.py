import os
import streamlit as st
import pandas as pd
from google.cloud import bigquery
from math import radians, cos, sin, asin, sqrt

# -------------------------
# Page Setup & Shared Functions
# -------------------------
st.set_page_config(
    page_title="Olist E-Commerce Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def get_bq_client():
    """Initializes and caches the BigQuery client."""
    KEY_PATH = "/Users/alexfoo/Documents/NTU_DSAI/sound-vehicle-468314-q4-c77615633d50.json"
    # KEY_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not KEY_PATH or not os.path.exists(KEY_PATH):
        st.error("Please set the GOOGLE_APPLICATION_CREDENTIALS environment variable.")
        st.stop()
    return bigquery.Client.from_service_account_json(KEY_PATH, location="US")

@st.cache_data(ttl=3600)
def run_query(sql: str) -> pd.DataFrame:
    """Runs a SQL query and caches the result."""
    client = get_bq_client()
    try:
        return client.query(sql).to_dataframe()
    except Exception as e:
        st.error(f"An error occurred while running a query: {e}")
        st.stop()
        return pd.DataFrame()

# -------------------------
# Table Definitions (from dbt Star Schema)
# -------------------------
PROJECT_ID = "sound-vehicle-468314-q4"
DATASET = "m2_prod"
TABLE_FACT = f"{PROJECT_ID}.{DATASET}.fact_order_items"
TABLE_CUSTOMERS = f"{PROJECT_ID}.{DATASET}.dim_customers"
TABLE_PRODUCTS = f"{PROJECT_ID}.{DATASET}.dim_products"
TABLE_SELLERS = f"{PROJECT_ID}.{DATASET}.dim_sellers"
TABLE_PAYMENTS = f"{PROJECT_ID}.{DATASET}.dim_payments"
TABLE_GEOLOCATION = f"{PROJECT_ID}.{DATASET}.dim_geolocation"
TABLE_DATES = f"{PROJECT_ID}.{DATASET}.dim_dates"
TABLE_STG_ORDERS = f"{PROJECT_ID}.m2_ingestion.order"
TABLE_STG_CUSTOMERS = f"{PROJECT_ID}.m2_ingestion.customer"
TABLE_STG_SELLERS = f"{PROJECT_ID}.m2_ingestion.seller"

# -------------------------
# Main Page Content
# -------------------------
st.title("Welcome to the Olist E-Commerce Analytics Hub")
st.markdown("### Choose a report from the sidebar to begin your analysis.")
st.info("This application provides a series of dashboards to analyze Olist's e-commerce data. All data is fetched directly from a star schema in Google BigQuery.")