from dagster import asset, get_dagster_logger, AssetKey
import subprocess
import os

logger = get_dagster_logger()

# Path to your Meltano project (where meltano.yml lives)
MELTANO_DIR = "/home/ser/DSAI/5m-data-m2-project-2/5m-data-m2-project/meltano-ingestion"
def run_meltano_command(cmd: list[str]) -> str:
    """Run a Meltano command and return its output, raising Exception on failure."""
    full_cmd = ["meltano"] + cmd
    logger.info(f"Running meltano command: {' '.join(full_cmd)} (cwd={MELTANO_DIR})")
    try:
        output = subprocess.check_output(
            full_cmd,
            stderr=subprocess.STDOUT,
            cwd=MELTANO_DIR
        ).decode()
        logger.info(output)
        return output
    except subprocess.CalledProcessError as e:
        logger.error(e.output.decode())
        raise Exception(e.output.decode())

@asset(deps=[AssetKey("ingestion")])
def meltano_run_elt() -> None:
    """Run the Meltano pipeline: tap-csv -> target-bigquery."""
    run_meltano_command(["run", "tap-csv", "target-bigquery"])

