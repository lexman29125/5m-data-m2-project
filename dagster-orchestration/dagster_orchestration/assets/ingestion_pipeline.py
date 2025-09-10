import subprocess
from dagster import asset, Definitions
import pandas as pd
SCRIPT_PATH = "/home/ser/DSAI/5m-data-m2-project-2/5m-data-m2-project/scripts/ingest.py"

@asset
def ingestion():
    """Delegates dataset download/unzip to external script."""
    result = subprocess.run(["python", SCRIPT_PATH], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Script failed: {result.stderr}")
    print(result.stdout)
    return pd.DataFrame({"status": [result.returncode]})


