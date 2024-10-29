import os

def get_databricks_runtime_version():
    _DATABRICKS_VERSION_FILE_PATH = "/databricks/DBR_VERSION"
    if ver := os.environ.get("DATABRICKS_RUNTIME_VERSION"):
        return ver
    if os.path.exists(_DATABRICKS_VERSION_FILE_PATH):
        # In Databricks DCS cluster, it doesn't have DATABRICKS_RUNTIME_VERSION
        # environment variable, we have to read version from the version file.
        with open(_DATABRICKS_VERSION_FILE_PATH) as f:
            return f.read().strip()
    return None

def is_spark_connect_mode():
    try:
        from pyspark.sql.utils import is_remote
    except ImportError:
        return False
    return is_remote()


def is_databricks_serverless(spark):
    """
    Return True if running on Databricks Serverless notebook or
    on Databricks Connect client that connects to Databricks Serverless.
    """

    return is_spark_connect_mode() and any(
        k == "x-databricks-session-id" for k, v in spark.client.metadata()
    )