from dagster import asset, get_dagster_logger, AssetKey
import os
import subprocess
# from .meltano_pipeline import meltano_run_elt

# Paths
DBT_PROJECT_DIR = os.path.join(os.path.dirname(__file__), "../../../dbt_olist")
DBT_PROFILES_DIR = DBT_PROJECT_DIR   # adjust if you later move to ~/.dbt

logger = get_dagster_logger()

def run_dbt_command(cmd: list[str]) -> str:
    """Run a dbt command and return its output, raising Exception on failure."""
    full_cmd = cmd + ["--profiles-dir", DBT_PROFILES_DIR]
    logger.info(f"Running dbt command: {' '.join(full_cmd)}")
    try:
        output = subprocess.check_output(full_cmd, stderr=subprocess.STDOUT).decode()
        logger.info(output)
        return output
    except subprocess.CalledProcessError as e:
        logger.error(e.output.decode())
        raise Exception(e.output.decode())

@asset(deps=[AssetKey("meltano_run_elt")])
def pipeline_dbt_deps() -> None:
    """Install dbt packages (from packages.yml)."""
    run_dbt_command(["dbt", "deps", "--project-dir", DBT_PROJECT_DIR])

@asset(deps=[pipeline_dbt_deps])
def pipeline_dbt_seed() -> None:
    """Runs dbt seed."""
    run_dbt_command(["dbt", "seed", "--project-dir", DBT_PROJECT_DIR])

@asset(deps=[pipeline_dbt_seed])
def pipeline_dbt_run() -> None:
    """Runs dbt run --full-refresh."""
    run_dbt_command(["dbt", "run", "--full-refresh", "--project-dir", DBT_PROJECT_DIR])

@asset(deps=[pipeline_dbt_run])
def pipeline_dbt_test() -> None:
    """Runs dbt test."""
    run_dbt_command(["dbt", "test", "--project-dir", DBT_PROJECT_DIR])