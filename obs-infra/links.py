# Databricks notebook source
# would not recommend relying on these brittle helper methods for production - NO WARRANTY
api_url = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().getOrElse(None)
token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().getOrElse(None)
workspace_id = dbutils.notebook.entry_point.getDbutils().notebook().getContext().workspaceId().getOrElse(None)
host = dbutils.notebook.entry_point.getDbutils().notebook().getContext().browserHostName().getOrElse(None)
cluster_id=dbutils.notebook.entry_point.getDbutils().notebook().getContext().clusterId().getOrElse(None)

def generate_html_link(url, text, new_tab=False):
  target = ' target="_blank"' if new_tab else ""
  return f'<a href="{url}"{target}>{text}</a>'


# COMMAND ----------

displayHTML(generate_html_link(f"https://{host}/driver-proxy/o/{workspace_id}/{cluster_id}/9090", "Prometheus"))
displayHTML(generate_html_link(f"https://{host}/driver-proxy/o/{workspace_id}/{cluster_id}/9464/metrics", "OTEL Prometheus Exporter (debug)", ))

# COMMAND ----------

print(f"OTLP_HTTP_ENDPOINT=https://{host}/driver-proxy-api/o/{workspace_id}/{cluster_id}/4318")
print("DB_API_TOKEN={{your_scope/your_secret}}")
print("Additionally, add a workspace init script to your target clusters using path /Workspace/databricks-opentelemetry/init.sh")
# COMMAND ----------



