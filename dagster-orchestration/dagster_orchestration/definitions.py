from dagster import (
    AssetSelection,
    Definitions,
    ScheduleDefinition,
    define_asset_job,
    load_assets_from_modules,
)
from dagster_duckdb_pandas import DuckDBPandasIOManager


from .assets import dbtpipeline
from .assets import meltano_pipeline  # <-- import the Meltano asset
from .assets import ingestion_pipeline



# define the job that will materialize the assets




dbt_assets = load_assets_from_modules([dbtpipeline])
meltano_assets = load_assets_from_modules([meltano_pipeline])
ingestion_assets = load_assets_from_modules([ingestion_pipeline])

from dagster import define_asset_job

# Define jobs
etl_job = define_asset_job(
    name="etl_job",
    selection=[
        "ingestion",
        "meltano_run_elt",          # Meltano first
        "pipeline_dbt_deps",
        "pipeline_dbt_seed",        # then dbt seed
        "pipeline_dbt_run",         # dbt run
        "pipeline_dbt_test",        # dbt test
    ]
)

dbt_only_job = define_asset_job(
    name="dbt_pipeline",
    selection=["pipeline_dbt_deps","pipeline_dbt_seed", "pipeline_dbt_run", "pipeline_dbt_test"]
)

# Schedule dbt_only_job to run every day at midnight
dbt_schedule = ScheduleDefinition(
    job=dbt_only_job,
    cron_schedule="0 0 * * *"
)

# IO manager
database_io_manager = DuckDBPandasIOManager(database="analytics.pandas_releases")

# Definitions
defs = Definitions(
    assets=[*dbt_assets, *meltano_assets, *ingestion_assets],
    jobs=[etl_job, dbt_only_job],  # <-- include the jobs here
    schedules=[dbt_schedule],
    resources={
        "io_manager": database_io_manager,
    },
)


