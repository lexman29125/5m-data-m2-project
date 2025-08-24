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