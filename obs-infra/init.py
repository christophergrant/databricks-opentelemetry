import subprocess
import json
from databricks.sdk import WorkspaceClient

def get_terraform_output(output_name):
    result = subprocess.run(["terraform", "output", "-json", output_name], capture_output=True, text=True)
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        raise Exception("Error obtaining Terraform output")

cluster_id = get_terraform_output("cluster_id")

w = WorkspaceClient()

def generate_driver_proxy_url(ws: WorkspaceClient, cluster_id: str, is_api: bool, port: int, endpoint:str = "") -> str:
    workspace_id = ws.get_workspace_id()
    cloud = ws.config.environment.cloud
    org_id = str(workspace_id)

    url_prefix = "https://dbc-dp-"
    url_suffix = "cloud.databricks.com"

    # https://www.youtube.com/watch?v=CZKecJvD26k
    if cloud == "azure":
        url_prefix = "https://adb-dp-"
        url_suffix = "azuredatabricks.net"
        org_id = f"{org_id}.{workspace_id % 20}" # sharding is encoded in the dp URL

    url_path = f"{'driver-proxy-api' if is_api else 'driver-proxy'}/o/{str(workspace_id)}/{cluster_id}/{port}/{endpoint}"
    return f"{url_prefix}{workspace_id}.{url_suffix}/{url_path}"


print("\033[1;36mConfiguring agent installation on other Databricks nodes:\033[0m")
print(f"  \033[1;34mOTLP_HTTP_ENDPOINT:\033[0m {generate_driver_proxy_url(w, cluster_id, is_api=True, port=4318)}")
print("  \033[1;34mDB_API_TOKEN:\033[0m \033[4;33m{{your_scope/your_secret}}\033[0m")
print("  \033[1;32mNote:\033[0m Add a workspace init script to your target clusters using path:")
print("  \033[35m/Workspace/Repos/databricks/opentelemetry/init.sh\033[0m")

print("\n\033[1;33mSecurity Recommendation:\033[0m")
print("  - It's advised to securely store the \033[1;34mDB_API_TOKEN\033[0m as a secret for enhanced security. Please note that this token is accessible to those with shell access to the cluster. We recommend downscaling the permissions of that token.")

print("\n\033[1;36mMonitoring and Metrics Links:\033[0m")
print(f"  - Prometheus Dashboard URL: {generate_driver_proxy_url(w, cluster_id, is_api=False, port=9090)}")
print(f"  - Metrics Endpoint (for debugging): {generate_driver_proxy_url(w, cluster_id, is_api=False, port=9464, endpoint='metrics')}")

# Optionally print out cluster policy JSON
# If there's a condition under which you want to print this, ensure that's checked.
should_print_policy = True # Example condition, adjust based on actual use case
if should_print_policy:

    cluster_policy = {
        "spark_env_vars.OTLP_HTTP_ENDPOINT": {
        "type": "fixed",
        "value": f"{generate_driver_proxy_url(w, cluster_id, is_api=True, port=4318)}",
        "description": "Sets the OTLP HTTP Endpoint URL."
    },
    "spark_env_vars.DB_API_TOKEN": {
        "type": "fixed",
        "value": "{{your_scope/your_secret}}",
        "description": "Sets the Databricks API Token."
    },
    "init_scripts.0.workspace.destination": {
        "type": "fixed",
        "value": "/Repos/databricks/opentelemetry/init.sh",
        "description": "Specifies an initialization script to run when the cluster starts."
    }
    }

    print("\n\033[1;36m(OPTIONAL) Cluster Policy Configuration:\033[0m")
    print(json.dumps(cluster_policy, indent=2))


