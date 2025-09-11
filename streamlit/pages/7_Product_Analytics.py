import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from olist_report import run_query, TABLE_FACT, TABLE_PRODUCTS, TABLE_CUSTOMERS, create_state_filter, get_state_filter_sql_clause, create_year_filter, get_year_filter_sql_clause, TABLE_DATES

# -------------------------
# Page Content
# -------------------------
st.title("Product Analytics")

# Create the customer state and year filters UI
selected_states = create_state_filter(TABLE_CUSTOMERS)
selected_years = create_year_filter(TABLE_DATES)
st.session_state.selected_states = selected_states
st.session_state.selected_years = selected_years

# Use tabs to organize content
tab1, tab2 = st.tabs(["Category Performance", "Reviews & Dimensions"])

with tab1:
    st.header("Top Performing Product Categories")

    # Query for product category performance, including customer state
    state_filter = get_state_filter_sql_clause("c", selected_states)
    year_filter = get_year_filter_sql_clause("d", st.session_state.selected_years)
    sql_category_performance = f"""
    SELECT
        pr.product_category_name_english AS category,
        c.customer_state,
        SUM(SAFE_CAST(f.price AS FLOAT64)) AS total_revenue,
        COUNT(DISTINCT f.order_id) AS total_orders
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_PRODUCTS}` pr
        ON f.product_id = pr.product_id
    JOIN `{TABLE_CUSTOMERS}` c
        ON f.customer_id = c.customer_id
    JOIN `{TABLE_DATES}` d
        ON f.order_date_key = d.date_key
    WHERE TRUE {state_filter} {year_filter}
    GROUP BY 1, 2
    """
    df_category_performance = run_query(sql_category_performance)
    
    if not df_category_performance.empty:
        # --- Treemap of Revenue by Category ---
        st.subheader("Revenue Contribution by Category (Treemap)")
        df_revenue_by_category = df_category_performance.groupby('category').agg(
            total_revenue=('total_revenue', 'sum')
        ).reset_index().sort_values('total_revenue', ascending=False)
        
        fig_treemap = px.treemap(
            df_revenue_by_category,
            path=[px.Constant("all"), 'category'],
            values='total_revenue',
            title='Proportion of Total Revenue by Category'
        )
        st.plotly_chart(fig_treemap, use_container_width=True)

        # --- Dual-Axis Chart of Revenue vs. Orders ---
        st.subheader("Revenue vs. Orders by Category")
        df_agg_by_category = df_category_performance.groupby('category').agg(
            total_revenue=('total_revenue', 'sum'),
            total_orders=('total_orders', 'sum')
        ).reset_index().sort_values('total_revenue', ascending=False)

        fig_dual_axis = go.Figure()
        fig_dual_axis.add_trace(go.Bar(
            x=df_agg_by_category['category'],
            y=df_agg_by_category['total_revenue'],
            name='Total Revenue',
            marker_color='rgb(26, 118, 255)'
        ))
        fig_dual_axis.add_trace(go.Scatter(
            x=df_agg_by_category['category'],
            y=df_agg_by_category['total_orders'],
            name='Total Orders',
            yaxis='y2',
            mode='lines+markers',
            marker_color='rgb(255, 140, 0)'
        ))
        fig_dual_axis.update_layout(
            title='Revenue and Orders by Category',
            yaxis=dict(title='Total Revenue'),
            yaxis2=dict(title='Total Orders', overlaying='y', side='right')
        )
        st.plotly_chart(fig_dual_axis, use_container_width=True)
        
        # --- Scatter Plot of Revenue vs. Avg. Price (Size by Orders) ---
        st.subheader("Revenue vs. Avg. Price Scatter Plot (Bubble size by # of Orders)")
        df_agg_by_category['avg_price'] = df_agg_by_category['total_revenue'] / df_agg_by_category['total_orders']

        # Add labels for categories with high orders or revenue
        df_agg_by_category['label'] = df_agg_by_category.apply(
            lambda row: row['category'] if row['avg_price'] > 4500 or row['total_revenue'] > 11000000 else '', axis=1
        )
        
        fig_scatter = px.scatter(
            df_agg_by_category,
            x='avg_price',
            y='total_revenue',
            size='total_orders',
            hover_name='category',
            title='Revenue vs. Average Price by Category (Size by # of Orders)',
            labels={'avg_price': 'Average Price', 'total_revenue': 'Total Revenue', 'total_orders': 'Total Orders'},
            text='label'
        )
        fig_scatter.update_traces(textposition='top center')
        st.plotly_chart(fig_scatter, use_container_width=True)

        # --- Stacked Bar Chart of Revenue by Category and Customer State ---
        st.subheader("Revenue by Category and Customer State")
        df_sorted_by_revenue = df_category_performance.groupby('category').sum().reset_index().sort_values('total_revenue', ascending=False)
        order_by_revenue = df_sorted_by_revenue['category'].tolist()

        fig_stacked_bar = px.bar(
            df_category_performance,
            x='category',
            y='total_revenue',
            color='customer_state',
            title='Revenue by Category, Stacked by Customer State',
            labels={'total_revenue': 'Total Revenue', 'category': 'Category', 'customer_state': 'Customer State'},
            category_orders={'category': order_by_revenue}
        )
        st.plotly_chart(fig_stacked_bar, use_container_width=True)
    else:
        st.warning("No data found for product category performance.")

with tab2:
    st.header("Product Insights")
    
    # Query for review score by product category
    state_filter = get_state_filter_sql_clause("c", selected_states)
    year_filter = get_year_filter_sql_clause("d", st.session_state.selected_years)
    sql_reviews_by_category = f"""
    SELECT
        pr.product_category_name_english AS category,
        AVG(SAFE_CAST(f.review_score AS FLOAT64)) AS avg_review_score
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_PRODUCTS}` pr
        ON f.product_id = pr.product_id
    JOIN `{TABLE_CUSTOMERS}` c
        ON f.customer_id = c.customer_id
    JOIN `{TABLE_DATES}` d
        ON f.order_date_key = d.date_key
    WHERE f.review_score IS NOT NULL
        AND TRUE {state_filter} {year_filter}
    GROUP BY 1
    ORDER BY avg_review_score DESC
    LIMIT 20
    """
    df_reviews_by_category = run_query(sql_reviews_by_category)
    
    if not df_reviews_by_category.empty:
        st.subheader("Average Review Score by Category")
        fig_reviews = px.bar(df_reviews_by_category, x="avg_review_score", y="category", orientation="h",
                             labels={"avg_review_score": "Avg. Review Score", "category": "Category"})
        st.plotly_chart(fig_reviews, use_container_width=True)
    else:
        st.warning("No data found for reviews by category.")
        
    # Query for product weight vs. review score
    state_filter = get_state_filter_sql_clause("c", selected_states)
    year_filter = get_year_filter_sql_clause("d", st.session_state.selected_years)
    sql_weight_vs_review = f"""
    SELECT
        SAFE_CAST(pr.product_weight_g AS FLOAT64) AS weight_g,
        AVG(SAFE_CAST(f.review_score AS FLOAT64)) AS avg_review_score
    FROM `{TABLE_FACT}` f
    JOIN `{TABLE_PRODUCTS}` pr
        ON f.product_id = pr.product_id
    JOIN `{TABLE_CUSTOMERS}` c
        ON f.customer_id = c.customer_id
    JOIN `{TABLE_DATES}` d
        ON f.order_date_key = d.date_key
    WHERE
        pr.product_weight_g IS NOT NULL
        AND f.review_score IS NOT NULL
        AND TRUE {state_filter} {year_filter}
    GROUP BY 1
    """
    df_weight_vs_review = run_query(sql_weight_vs_review)

    if not df_weight_vs_review.empty:
        st.subheader("Product Weight vs. Review Score")
        fig_weight_review = px.scatter(df_weight_vs_review, x="weight_g", y="avg_review_score",
                                       labels={"weight_g": "Product Weight (g)", "avg_review_score": "Avg. Review Score"})
        st.plotly_chart(fig_weight_review, use_container_width=True)
    else:
        st.warning("No data found for product weight vs. review score.")
