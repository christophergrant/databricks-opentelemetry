from pyspark.sql import SparkSession
from opentelemetry.sdk.resources import ResourceAttributes

DATABRICKS_JOB_ID = "databricks.job_id"
DATABRICKS_JOB_RUN_ID = "databricks.job_run_id"
DATABRICKS_TASK_ID = "databricks.task_id"

def _get_workspace_client():
    try:
        from databricks.sdk import WorkspaceClient
        return WorkspaceClient()
    except:
        return None

def get_cloud():
    client = _get_workspace_client()
    if client:
        try:
            return client.config.environment.cloud.name
        except:
            pass
    return None

def get_region():
    client = _get_workspace_client()
    if client:
        try:
            return client.metastores.summary().region
        except:
            pass
    return None

def get_hostname():
    client = _get_workspace_client()
    if client:
        try:
            return client.config.hostname
        except:
            pass
    return None

def get_user():
    client = _get_workspace_client()
    if client:
        try:
            return client.current_user.me().user_name
        except:
            pass
    return None

def _get_notebook_context():
    try:
        return dbutils.notebook.entry_point.getDbutils().notebook().getContext()
    except:
        return None

def get_job_id():
    context = _get_notebook_context()
    if context:
        try:
            return context.jobId().get()
        except:
            pass
    return None

def get_job_run_id():
    context = _get_notebook_context()
    if context:
        try:
            return context.jobRunId().get()
        except:
            pass
    return None

def get_task_id():
    context = _get_notebook_context()
    if context:
        try:
            return context.idInJob().get()
        except:
            pass
    return None

def get_dbr_version(spark):
    try:
        return spark.sql("select current_version().dbr_version as dbr_version").collect()[0]["dbr_version"]
    except:
        return None

def get_attributes(spark: SparkSession):
    return {
        ResourceAttributes.CLOUD_PROVIDER: get_cloud(),
        ResourceAttributes.CLOUD_REGION: get_region(), 
        ResourceAttributes.HOST_NAME: get_hostname(),
        DATABRICKS_JOB_ID: get_job_id(),
        DATABRICKS_JOB_RUN_ID: get_job_run_id(),
        DATABRICKS_TASK_ID: get_task_id(),
        ResourceAttributes.PROCESS_OWNER: get_user(),
        ResourceAttributes.PROCESS_RUNTIME_VERSION: get_dbr_version(spark)
    }