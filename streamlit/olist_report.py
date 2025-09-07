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

# Initialize session state for project ID and dataset if they don't exist
if 'project_id' not in st.session_state:
    st.session_state.project_id = os.getenv("PROJECT_ID")
if 'dataset' not in st.session_state:
    st.session_state.dataset = "m2_prod" # Set a default dataset
if 'selected_states' not in st.session_state:
    st.session_state.selected_states = []

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

# Haversine formula to calculate the distance between two points on the Earth
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles.
    return c * r

# Function to define the customer state filter UI
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

# Function to generate the WHERE clause for customer state filters
def get_state_filter_sql_clause(alias, selected_states):
    """Generates the SQL WHERE clause for customer state filters."""
    if selected_states:
        states = ", ".join([f"'{s}'" for s in selected_states])
        return f" AND {alias}.customer_state IN ({states})"
    return ""

# -------------------------
# Main Page Content
# -------------------------
st.title("Welcome to the Olist E-Commerce Analytics Hub")
st.markdown("### Choose a report from the sidebar to begin your analysis.")

# Use the sidebar for user input
with st.sidebar:
    st.header("BigQuery Connection Settings")
    
    # Text input for Project ID, linked to session_state
    project_id_input = st.text_input(
        "Enter your Google Cloud Project ID:",
        value=st.session_state.project_id,
        key="project_id_input"
    )
    
    # Text input for Dataset, linked to session_state
    dataset_input = st.text_input(
        "Enter your BigQuery Dataset:",
        value=st.session_state.dataset,
        key="dataset_input"
    )

    # When the user changes the input, update session_state
    if project_id_input != st.session_state.project_id:
        st.session_state.project_id = project_id_input
        st.rerun()

    if dataset_input != st.session_state.dataset:
        st.session_state.dataset = dataset_input
        st.rerun()

    # Check if project ID is provided before proceeding
    if st.session_state.project_id:
        PROJECT_ID = st.session_state.project_id
        DATASET = st.session_state.dataset
        
        # Define tables using the session state variables
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
    else:
        st.warning("Please enter your Google Cloud Project ID in the sidebar to proceed.")