# Job Failed: BrokenPipeError: [Errno 32] Broken pipe
Option A — Increase the file descriptor limit Temporarily raise limit (for current shell session) ulimit -n 4096

Option B — Batch your CSVs • Instead of reading hundreds of files at once, process them in smaller groups. • In meltano.yml, only list a subset of CSVs as streams per run.

Option C - Provision a GCP VM with more I/O to run job

Option D - Reduce batch size • In your meltano.yml or tap configuration, reduce how many records are buffered before flushing.

config:
batch_size: 500 # default might be 1000+

Combination of options A, B and D, the local machine is able to complete the jobs successfully with ~10mins per batch.

# Job Failed 2:
When running product_category_name_translation.csv

[info ] google.api_core.exceptions.BadRequest: 400 POST https://bigquery.googleapis.com/bigquery/v2/projects/sound-vehicle-468314-q4/datasets/m2_ingestion/tables?prettyPrint=false: Invalid field name "﻿product_category_name". Fields must contain the allowed characters, and be at most 300 characters long. For allowed characters, please refer to https://cloud.google.com/bigquery/docs/schemas#column_names

Possible Solution 2 (Not working):
In meltano.yml for tap-csv, add:

plugins: extractors: - name: tap-csv config: files: - entity: product_category_name_translation path: ./data/product_category_name_translation.csv keys: [product_category_name] clean_headers: true