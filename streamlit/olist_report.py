# olist_report.py

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

# Initialize session state defaults
if 'project_id' not in st.session_state:
    st.session_state.project_id = os.getenv("PROJECT_ID")
if 'dataset' not in st.session_state:
    st.session_state.dataset = "m2_prod"  # Default dataset
if 'selected_states' not in st.session_state:
    st.session_state.selected_states = []
if 'selected_years' not in st.session_state:
    st.session_state.selected_years = []

@st.cache_resource
def get_bq_client():
    """Initializes and caches the BigQuery client."""
    KEY_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
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
# Utility Functions
# -------------------------
def haversine(lon1, lat1, lon2, lat2):
    """Calculate the great circle distance in km between two points."""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Earth radius in km
    return c * r

# -------------------------
# Filters
# -------------------------
def create_state_filter(table_customers_path):
    """Creates a multiselect filter for customer states."""
    sql = f"SELECT DISTINCT customer_state FROM `{table_customers_path}` ORDER BY customer_state"
    df_states = run_query(sql)
    all_states = df_states['customer_state'].tolist()

    selected_states = st.multiselect(
        "Filter by Customer State:",
        options=all_states,
        default=all_states,
        help="Select one or more states to filter the reports."
    )
    return selected_states

def get_state_filter_sql_clause(alias, selected_states):
    """Generates the SQL WHERE clause for state filters."""
    if selected_states:
        states = ", ".join([f"'{s}'" for s in selected_states])
        return f" AND {alias}.customer_state IN ({states})"
    return ""

def create_year_filter(table_dates_path):
    """Creates a multiselect filter for order years (2016–2025)."""
    sql = f"SELECT DISTINCT year FROM `{table_dates_path}` WHERE year BETWEEN 2016 AND 2025 ORDER BY year"
    df_years = run_query(sql)
    all_years = df_years['year'].tolist()

    selected_years = st.multiselect(
        "Filter by Year:",
        options=all_years,
        default=all_years,
        help="Select one or more years to filter the reports."
    )
    return selected_years

def get_year_filter_sql_clause(alias, selected_years):
    """Generates the SQL WHERE clause for year filters."""
    if selected_years:
        years = ", ".join([str(y) for y in selected_years])
        return f" AND {alias}.year IN ({years})"
    return ""

# -------------------------
# Main Page Content
# -------------------------
st.title("Welcome to the Olist E-Commerce Analytics Hub")
st.markdown("### Choose a report from the sidebar to begin your analysis.")

# -------------------------
# Sidebar
# -------------------------
with st.sidebar:
    st.header("BigQuery Connection Settings")

    project_id_input = st.text_input(
        "Enter your Google Cloud Project ID:",
        value=st.session_state.project_id,
        key="project_id_input"
    )
    dataset_input = st.text_input(
        "Enter your BigQuery Dataset:",
        value=st.session_state.dataset,
        key="dataset_input"
    )

    if project_id_input != st.session_state.project_id:
        st.session_state.project_id = project_id_input
        st.rerun()

    if dataset_input != st.session_state.dataset:
        st.session_state.dataset = dataset_input
        st.rerun()

    if st.session_state.project_id:
        PROJECT_ID = st.session_state.project_id
        DATASET = st.session_state.dataset

        # Define tables
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

        st.success(f"Connected to **{PROJECT_ID}** and dataset **{DATASET}**.")

        # Filters
        st.subheader("Filters")
        st.session_state.selected_states = create_state_filter(TABLE_CUSTOMERS)
        st.session_state.selected_years = create_year_filter(TABLE_DATES)

    else:
        st.warning("Please enter your Google Cloud Project ID in the sidebar to proceed.")