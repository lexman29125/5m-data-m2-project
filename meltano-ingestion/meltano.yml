version: 1
default_environment: dev
project_id: eed08545-8f1e-4497-bb7a-7d3d30ec8fdf
environments:
- name: dev
- name: staging
- name: prod
plugins:
  extractors:
  - name: tap-csv
    variant: meltanolabs
    pip_url: git+https://github.com/MeltanoLabs/tap-csv.git
    config:
      files:
      - entity: customer
        path: ../assets/olist_customers_dataset.csv
        keys: [customer_id]
      - entity: geolocation
        path: ../assets/olist_geolocation_dataset.csv
        keys: [geolocation_zip_code_prefix]
      - entity: orders_item
        path: ../assets/olist_order_items_dataset.csv
        keys: [order_item_id]
      - entity: orders_payment
        path: ../assets/olist_order_payments_dataset.csv
        keys: [order_payment_id]
      - entity: orders_review
        path: ../assets/olist_order_reviews_dataset.csv
        keys: [order_reviews_id]
      - entity: order
        path: ../assets/olist_orders_dataset.csv
        keys: [order_id]
      - entity: product
        path: ../assets/olist_products_dataset.csv
        keys: [product_id]
      - entity: seller
        path: ../assets/olist_sellers_dataset.csv
        keys: [seller_id]
      - entity: product_category_name_translation
        path: ../assets/product_category_name_translation.csv
        keys: [product_category_id]

      flattening_enabled: true
      flattening_max_depth: 1
  loaders:
  - name: target-bigquery
    variant: z3z1ma
    pip_url: git+https://github.com/z3z1ma/target-bigquery.git
    config:
      project: sound-vehicle-468314-q4
      dataset: m2_ingestion
      credentials_path: 
        /Users/alexfoo/Documents/NTU_DSAI/sound-vehicle-468314-q4-c77615633d50.json
      method: batch_job
      denormalized: true
      flattening_enabled: true
      flattening_max_depth: 1
