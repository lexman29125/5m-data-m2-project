# Meltano EL Job Failed: BrokenPipeError: [Errno 32] Broken pipe
Option A — Increase the file descriptor limit Temporarily raise limit (for current shell session) ulimit -n 4096

Option B — Batch your CSVs • Instead of reading hundreds of files at once, process them in smaller groups. • In meltano.yml, only list a subset of CSVs as streams per run.

Option C - Provision a GCP VM with more I/O to run job

Option D - Reduce batch size • In your meltano.yml or tap configuration, reduce how many records are buffered before flushing.

config:
batch_size: 500 # default might be 1000+

Combination of options A, B and D, the local machine is able to complete the jobs successfully with ~10mins per batch.

Option E - Stage using DuckDB

Stage in DuckDB first

DuckDB is a columnar, vectorized database that can:
	•	Ingest CSVs really fast (COPY or read_csv_auto).
	•	Store them in a compact columnar format (Parquet/Arrow).
	•	Push data in batch instead of row-by-row.

So the flow becomes:
	1.	Load CSV → DuckDB (super fast, optimized).
	2.	Export from DuckDB → Parquet or Arrow.
	3.	Load Parquet/Arrow → BigQuery (bulk load, much faster).

Why it speeds things up
	•	Columnar storage (Parquet/Arrow) = fewer bytes to move than raw CSV.
	•	Parallel I/O → DuckDB vectorizes reads/writes.
	•	BigQuery loves Parquet (native ingestion optimization).

Caveats
	•	You’re adding an extra staging step (CSV → DuckDB → BigQuery) vs direct stream.
	•	If the CSV is small, the overhead isn’t worth it.
	•	If the pipeline already uses Google Cloud Storage (GCS) as staging, pushing CSV → GCS → BigQuery might be simpler than adding DuckDB.

# Meltano EL Job Failed 2:
When running product_category_name_translation.csv

[info ] google.api_core.exceptions.BadRequest: 400 POST https://bigquery.googleapis.com/bigquery/v2/projects/sound-vehicle-468314-q4/datasets/m2_ingestion/tables?prettyPrint=false: Invalid field name "﻿product_category_name". Fields must contain the allowed characters, and be at most 300 characters long. For allowed characters, please refer to https://cloud.google.com/bigquery/docs/schemas#column_names

## Possible Solution 2 (Not working):
In meltano.yml for tap-csv, add:

plugins: extractors: - name: tap-csv config: files: - entity: product_category_name_translation path: ./data/product_category_name_translation.csv keys: [product_category_name] clean_headers: true

## Solution (Worked):

Notice BigQuery is literally complaining about: Invalid field name "product_category_name"

That invisible character before p (﻿) is Unicode U+FEFF (Byte Order Mark) aka BOM. Your sed command didn’t strip it successfully.

### On MacOS run:

LC_CTYPE=C sed -i '' '1s/^\xef\xbb\xbf//' product_category_name_translation.csv

### To verify if BOM is cleared:

od -c product_category_name_translation.csv | head -1

### If BOM is present, you’ll see:

0000000 357 273 277   p   r   o   d   u   c   t   _   c   a   t   e   g
(357 273 277 is octal for EF BB BF).

### Clear Meltano’s cached schema

singer taps/targets cache the inferred schema from the first run. If the BOM was present earlier, the schema JSON still has "﻿product_category_name".
	•	Look in .meltano/run/ or .meltano/cache/ and delete the relevant JSON files for this stream (product_category_name_translation).
	•	Or just blow away the cache completely:
rm -rf .meltano/

# dbt run Job Error:

When executing "dbt run"

ERROR creating sql view model m2_prod.stg_geolocation 
SKIP relation m2_prod.dim_geolocation ................................. [SKIP]
11:08:26  11 of 17 SKIP relation m2_prod.dim_customers ................................... [SKIP]
ERROR creating sql table model m2_prod.dim_dates
SKIP relation m2_prod.dim_sellers ..................................... [SKIP]
ERROR creating sql incremental model m2_prod.fact_order_items ......... [ERROR in 2.10s]
11:08:30  BigQuery adapter: https://console.cloud.google.com/bigquery?project=sound-vehicle-468314-q4&j=bq:US:2d3e4ede-cd37-48aa-8f98-a300035fa0b6&page=queryresults
11:08:30  15 of 17 ERROR creating sql table model m2_prod.dim_products ................... [ERROR in 1.19s]

## Solution:

Update sql files.

dbt run --full-refresh

### Error:
(elt) alexfoo@as-MacBook-Air dbt_olist % dbt run --full-refresh             
11:39:12  Running with dbt=1.9.6
11:39:13  Registered adapter: bigquery=1.9.1
11:39:14  Found 17 models, 1 seed, 23 data tests, 8 sources, 492 macros
11:39:14  
11:39:14  Concurrency: 4 threads (target='dev')
11:39:14  
11:39:15  1 of 17 START sql table model m2_prod.my_first_dbt_model ....................... [RUN]
11:39:15  2 of 17 START sql view model m2_prod.stg_customers ............................. [RUN]
11:39:15  3 of 17 START sql view model m2_prod.stg_geolocation ........................... [RUN]
11:39:15  4 of 17 START sql view model m2_prod.stg_order_items ........................... [RUN]
/Users/alexfoo/miniconda3/envs/elt/lib/python3.10/site-packages/dbt/adapters/bigquery/connections.py:570: FutureWarning: job_retry must be explicitly set to None if job_id is set.
BigQuery cannot retry a failed job by using the exact
same ID. Setting job_id without explicitly disabling
job_retry will raise an error in the future. To avoid this
warning, either use job_id_prefix instead (preferred) or
set job_retry=None.
  query_job = client.query(
11:39:17  4 of 17 OK created sql view model m2_prod.stg_order_items ...................... [CREATE VIEW (0 processed) in 1.68s]
11:39:17  3 of 17 OK created sql view model m2_prod.stg_geolocation ...................... [CREATE VIEW (0 processed) in 1.68s]
11:39:17  2 of 17 OK created sql view model m2_prod.stg_customers ........................ [CREATE VIEW (0 processed) in 1.68s]
11:39:17  5 of 17 START sql view model m2_prod.stg_order_payments ........................ [RUN]
11:39:17  6 of 17 START sql view model m2_prod.stg_order_reviews ......................... [RUN]
11:39:17  7 of 17 START sql view model m2_prod.stg_orders ................................ [RUN]
/Users/alexfoo/miniconda3/envs/elt/lib/python3.10/site-packages/dbt/adapters/bigquery/connections.py:570: FutureWarning: job_retry must be explicitly set to None if job_id is set.
BigQuery cannot retry a failed job by using the exact
same ID. Setting job_id without explicitly disabling
job_retry will raise an error in the future. To avoid this
warning, either use job_id_prefix instead (preferred) or
set job_retry=None.
  query_job = client.query(
11:39:19  7 of 17 OK created sql view model m2_prod.stg_orders ........................... [CREATE VIEW (0 processed) in 1.49s]
11:39:19  5 of 17 OK created sql view model m2_prod.stg_order_payments ................... [CREATE VIEW (0 processed) in 1.50s]
11:39:19  1 of 17 OK created sql table model m2_prod.my_first_dbt_model .................. [CREATE TABLE (2.0 rows, 0 processed) in 3.19s]
11:39:19  6 of 17 OK created sql view model m2_prod.stg_order_reviews .................... [CREATE VIEW (0 processed) in 1.50s]
11:39:19  8 of 17 START sql view model m2_prod.stg_products .............................. [RUN]
11:39:19  9 of 17 START sql view model m2_prod.stg_sellers ............................... [RUN]
11:39:19  10 of 17 START sql table model m2_prod.dim_geolocation ......................... [RUN]
11:39:19  11 of 17 START sql table model m2_prod.dim_customers ........................... [RUN]
/Users/alexfoo/miniconda3/envs/elt/lib/python3.10/site-packages/dbt/adapters/bigquery/connections.py:570: FutureWarning: job_retry must be explicitly set to None if job_id is set.
BigQuery cannot retry a failed job by using the exact
same ID. Setting job_id without explicitly disabling
job_retry will raise an error in the future. To avoid this
warning, either use job_id_prefix instead (preferred) or
set job_retry=None.
  query_job = client.query(
11:39:20  8 of 17 OK created sql view model m2_prod.stg_products ......................... [CREATE VIEW (0 processed) in 1.45s]
11:39:20  9 of 17 OK created sql view model m2_prod.stg_sellers .......................... [CREATE VIEW (0 processed) in 1.45s]
11:39:20  12 of 17 START sql table model m2_prod.dim_dates ............................... [RUN]
11:39:20  13 of 17 START sql table model m2_prod.dim_payments ............................ [RUN]
/Users/alexfoo/miniconda3/envs/elt/lib/python3.10/site-packages/dbt/adapters/bigquery/connections.py:570: FutureWarning: job_retry must be explicitly set to None if job_id is set.
BigQuery cannot retry a failed job by using the exact
same ID. Setting job_id without explicitly disabling
job_retry will raise an error in the future. To avoid this
warning, either use job_id_prefix instead (preferred) or
set job_retry=None.
  query_job = client.query(
11:39:21  BigQuery adapter: https://console.cloud.google.com/bigquery?project=sound-vehicle-468314-q4&j=bq:US:037a65b0-0c49-4047-a752-766eb6e19160&page=queryresults
11:39:21  12 of 17 ERROR creating sql table model m2_prod.dim_dates ...................... [ERROR in 1.16s]
11:39:21  14 of 17 START sql view model m2_prod.my_second_dbt_model ...................... [RUN]
11:39:23  14 of 17 OK created sql view model m2_prod.my_second_dbt_model ................. [CREATE VIEW (0 processed) in 1.32s]
11:39:23  15 of 17 START sql incremental model m2_prod.fact_order_items .................. [RUN]
/Users/alexfoo/miniconda3/envs/elt/lib/python3.10/site-packages/dbt/adapters/bigquery/connections.py:570: FutureWarning: job_retry must be explicitly set to None if job_id is set.
BigQuery cannot retry a failed job by using the exact
same ID. Setting job_id without explicitly disabling
job_retry will raise an error in the future. To avoid this
warning, either use job_id_prefix instead (preferred) or
set job_retry=None.
  query_job = client.query(
11:39:24  10 of 17 OK created sql table model m2_prod.dim_geolocation .................... [CREATE TABLE (19.0k rows, 61.3 MiB processed) in 4.91s]
11:39:24  16 of 17 START sql table model m2_prod.dim_products ............................ [RUN]
/Users/alexfoo/miniconda3/envs/elt/lib/python3.10/site-packages/dbt/adapters/bigquery/connections.py:570: FutureWarning: job_retry must be explicitly set to None if job_id is set.
BigQuery cannot retry a failed job by using the exact
same ID. Setting job_id without explicitly disabling
job_retry will raise an error in the future. To avoid this
warning, either use job_id_prefix instead (preferred) or
set job_retry=None.
  query_job = client.query(
11:39:24  BigQuery adapter: https://console.cloud.google.com/bigquery?project=sound-vehicle-468314-q4&j=bq:US:95ae9a3b-f2d5-4957-bba1-824f4e7c213f&page=queryresults
11:39:24  15 of 17 ERROR creating sql incremental model m2_prod.fact_order_items ......... [ERROR in 1.17s]
11:39:24  17 of 17 START sql table model m2_prod.dim_sellers ............................. [RUN]
/Users/alexfoo/miniconda3/envs/elt/lib/python3.10/site-packages/dbt/adapters/bigquery/connections.py:570: FutureWarning: job_retry must be explicitly set to None if job_id is set.
BigQuery cannot retry a failed job by using the exact
same ID. Setting job_id without explicitly disabling
job_retry will raise an error in the future. To avoid this
warning, either use job_id_prefix instead (preferred) or
set job_retry=None.
  query_job = client.query(
11:39:24  13 of 17 OK created sql table model m2_prod.dim_payments ....................... [CREATE TABLE (5.0 rows, 1.2 MiB processed) in 3.87s]
11:39:25  11 of 17 OK created sql table model m2_prod.dim_customers ...................... [CREATE TABLE (99.4k rows, 78.6 MiB processed) in 6.01s]
11:39:27  16 of 17 OK created sql table model m2_prod.dim_products ....................... [CREATE TABLE (33.0k rows, 2.1 MiB processed) in 3.37s]
11:39:27  17 of 17 OK created sql table model m2_prod.dim_sellers ........................ [CREATE TABLE (3.1k rows, 61.5 MiB processed) in 3.52s]
11:39:27  
11:39:27  Finished running 1 incremental model, 7 table models, 9 view models in 0 hours 0 minutes and 13.13 seconds (13.13s).
11:39:27  
11:39:27  Completed with 2 errors, 0 partial successes, and 0 warnings:
11:39:27  
11:39:27    Database Error in model dim_dates (models/marts/dim_dates.sql)
  Unrecognized name: order_purchase_timestamp at [18:11]
  compiled code at target/run/dbt_olist/models/marts/dim_dates.sql
11:39:27  
11:39:27    Database Error in model fact_order_items (models/marts/fact_order_items.sql)
  Unrecognized name: order_purchase_timestamp at [22:14]
  compiled code at target/run/dbt_olist/models/marts/fact_order_items.sql
11:39:27  
11:39:27  Done. PASS=15 WARN=0 ERROR=2 SKIP=0 TOTAL=17

### Fix:

Alright, the logs are telling us exactly what went wrong:
	•	Two errors occurred in your run:
	1.	dim_dates model

Unrecognized name: order_purchase_timestamp at [18:11]

	2.	fact_order_items model

Unrecognized name: order_purchase_timestamp at [22:14]

This means that BigQuery does not know the column order_purchase_timestamp in the context where you’re referencing it. It’s not a dbt bug—your SQL is trying to use a column that either:
	•	Doesn’t exist in the upstream table or view you’re selecting from,
	•	Or is misnamed (typo, different casing, underscores, etc.),
	•	Or the reference is in the wrong scope (e.g., referencing a column from a table that isn’t joined yet).

How to fix it
	1.	Check your source models
For example, dim_dates.sql probably has something like:

select distinct
    date(order_purchase_timestamp) as order_date,
    ...
from {{ ref('stg_orders') }}

Go to the upstream table/view (stg_orders) and confirm that order_purchase_timestamp actually exists there. In BigQuery:

select *
from `project.dataset.stg_orders`
limit 10


	2.	Correct column names if needed
	•	Maybe it’s purchase_timestamp or order_purchased_at in the source.
	•	Update your dim_dates.sql and fact_order_items.sql to match the real column name.
	3.	Re-run with full-refresh after fixing the column name:

dbt run --full-refresh

# dbt test Job Error:

Failure in test not_null_fact_order_items_payment_type_key
Failure in test not_null_my_first_dbt_model_id
Failure in test unique_dim_customers_customer_id
Failure in test unique_fact_order_items_order_id

## Solution & Reasons:
	•	not_null_fact_order_items_payment_type_key → There are rows in fact_order_items where payment_type_key is NULL. Likely because some orders don’t have a payment record. You can:
	•	Option A: Fix staging model stg_order_payments or the join in fact_order_items to handle missing payment info using LEFT JOIN and COALESCE.
	•	Option B: Decide that NULL payments are acceptable and remove the not_null test on that column.
	•	unique_dim_customers_customer_id → There are duplicates in dim_customers.customer_id.
Likely caused by multiple geolocation rows per zip code. You can:
	•	Aggregate stg_geolocation with ANY_VALUE or AVG so the join produces unique customer_id rows.
	•	Ensure dim_customers select has DISTINCT c.customer_id.
	•	unique_fact_order_items_order_id → Multiple order_item_ids exist per order_id.
This is expected: one order has multiple items. You shouldn’t test order_id uniqueness in the fact table. Instead:
	•	Change the test to unique(order_id, order_item_id) or remove it.
	•	not_null_my_first_dbt_model_id → This comes from my_first_dbt_model, which is a sample model you no longer need.

## Rerun dbt test:

dbt clean
dbt deps
dbt seed
dbt run --full-refresh
dbt test

# After ver 2 dbt code merge: dbt run error:

08:20:19  Completed with 2 errors, 0 partial successes, and 0 warnings:
08:20:19  
08:20:19    Database Error in model dim_customers (models/marts/dim_customers.sql)
  Name geolocation_id not found inside g at [20:7]
  compiled code at target/run/dbt_olist/models/marts/dim_customers.sql
08:20:19  
08:20:19    Database Error in model dim_sellers (models/marts/dim_sellers.sql)
  Name geolocation_id not found inside g at [19:7]
  compiled code at target/run/dbt_olist/models/marts/dim_sellers.sql

### The errors were:
	
Both errors are the same: the query is referencing g.geolocation_id, but the alias g doesn’t contain that column. Usually g is a table alias for dim_geolocation (or a CTE), so either:
	•	dim_geolocation doesn’t have geolocation_id in the schema, or
	•	The alias g in your SQL isn’t actually pointing to the table that contains geolocation_id.

### Solution: Update dim_customers.sql, dim_sellers.sql, Dim_geolocation.sql, schema.yml

This means stg_geolocation doesn’t have a column called geolocation_id. Likely it has:
	•	geolocation_zip_code_prefix

…but not geolocation_id.

Replace in code-> g.geolocation_id → g.geolocation_zip_code_prefix