# Databricks notebook source
# MAGIC %sh
# MAGIC mkdir -p /databricks/otel && 
# MAGIC wget -P /databricks/otel https://github.com/christophergrant/databricks-opentelemetry/releases/download/0.0.1/databricks-otelcol-amd64.zip 

# COMMAND ----------

# MAGIC %sh
# MAGIC unzip /databricks/otel/databricks-otelcol-amd64.zip -d /databricks/otel && chmod +x /databricks/otel/databricks-otelcol

# COMMAND ----------

# MAGIC %sh
# MAGIC
# MAGIC # Define the output file name
# MAGIC CONFIG_FILE="otelcol-config.yaml"
# MAGIC
# MAGIC # Write the configuration to the file
# MAGIC cat << 'EOF' > /databricks/otel/$CONFIG_FILE
# MAGIC receivers:
# MAGIC   hostmetrics:
# MAGIC     collection_interval: 1m
# MAGIC     scrapers:
# MAGIC       cpu:
# MAGIC       memory:
# MAGIC       disk:
# MAGIC       load:
# MAGIC       filesystem:
# MAGIC       network:
# MAGIC
# MAGIC exporters:
# MAGIC   prometheus:
# MAGIC     endpoint: "0.0.0.0:9090"
# MAGIC
# MAGIC processors:
# MAGIC
# MAGIC service:
# MAGIC   pipelines:
# MAGIC     metrics:
# MAGIC       receivers: [hostmetrics]
# MAGIC       exporters: [prometheus]
# MAGIC       processors: []
# MAGIC EOF
# MAGIC
# MAGIC # Print a message indicating completion
# MAGIC echo "Configuration has been written to $CONFIG_FILE"
# MAGIC

# COMMAND ----------

# MAGIC %sh
# MAGIC nohup /databricks/otel/databricks-otelcol --config /databricks/otel/otelcol-config.yaml > /databricks/otel/otelcol.log 2>&1 &
# MAGIC

# COMMAND ----------

import requests
import time

time.sleep(15)

response = requests.get('http://localhost:9090/metrics')
response.raise_for_status()

num_lines = len(response.text.splitlines())
assert num_lines > 10, f"Expected more than 10 lines, got {num_lines}"

# COMMAND ----------


