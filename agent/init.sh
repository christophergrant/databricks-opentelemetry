#!/bin/bash

set -euxo pipefail

# Initialize environment, outputting debugging symbols where required
initialize_env() {
	export SPARK_LOCAL_IP=$(hostname -I | awk '{print $1}')
	env
	mkdir -p /databricks/otelcol
}

# Generate an OpenTelemetry configuration
generate_config() {
	local config_path="/databricks/otelcol/config.yaml"
	cat <<EOF | envsubst >$config_path
extensions:
  bearertokenauth:
    scheme: Bearer
    token: ${env:DB_API_TOKEN}

receivers:
  hostmetrics:
    collection_interval: 10s
    scrapers:
      cpu:
      memory:
      disk:
      load:
        cpu_average: true
      filesystem:
      network:
      process:
      paging:
      processes:

  prometheus:
    config:
      scrape_configs:
        - job_name: spark_metrics
          scrape_interval: 10s
          metrics_path: /metrics/prometheus
          static_configs:
            - targets: [${env:SPARK_LOCAL_IP}:40001]
        - job_name: spark_aggregated_executor_metrics
          scrape_interval: 10s
          metrics_path: /metrics/executors/prometheus
          static_configs:
            - targets: [${env:SPARK_LOCAL_IP}:40001]

exporters:
  otlphttp:
    endpoint: ${env:OTLP_HTTP_ENDPOINT}
    auth:
      authenticator: bearertokenauth
  debug:

processors:
  attributes:
    actions:
      - key: databricks_cluster_id
        value: ${env:DB_CLUSTER_ID}
        action: insert
      - key: databricks_cluster_name
        value: ${env:DB_CLUSTER_NAME}
        action: insert
      - key: databricks_is_driver
        value: ${env:DB_IS_DRIVER}
        action: insert

service:
  extensions: [bearertokenauth]
  pipelines:
    metrics:
      receivers: [hostmetrics, prometheus]
      processors: [attributes]
      exporters: [debug, otlphttp]
EOF

}

# Download, install, and start a systemd service for OpenTelemetry
setup_otelcol() {
	# If in restricted networking environment, will need to reconfigure this to pull from a trusted, non-public source
	#   Can pull from some other storage like S3, ADLS or GCS, Unity Catalog Volumes, or DBFS instead
	wget -P /databricks/otelcol https://github.com/christophergrant/databricks-opentelemetry/releases/download/0.0.2/databricks-otelcol-amd64.zip
	unzip /databricks/otelcol/databricks-otelcol-amd64.zip -d /databricks/otelcol && chmod +x /databricks/otelcol/databricks-otelcol

	cat <<EOT | sudo tee /etc/systemd/system/databricks-otelcol.service
[Unit]
Description=Databricks OpenTelemetry Collector Service
After=network.target

[Service]
Type=simple
WorkingDirectory=/databricks/otelcol
ExecStart=/databricks/otelcol/databricks-otelcol --config /databricks/otelcol/config.yaml
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOT

	sudo systemctl daemon-reload
	sudo systemctl enable databricks-otelcol.service
	sudo systemctl start databricks-otelcol.service
}

# Function to initialize Spark Prometheus Servlet
# https://spark.apache.org/docs/latest/monitoring.html#metrics
init_spark_prometheus_servelet() {
	cat <<EOF >/databricks/spark/conf/metrics.properties
*.source.jvm.class=org.apache.spark.metrics.source.JvmSource
*.sink.prometheusServlet.class=org.apache.spark.metrics.sink.PrometheusServlet
*.sink.prometheusServlet.path=/metrics/prometheus
master.sink.prometheusServlet.path=/metrics/master/prometheus
applications.sink.prometheusServlet.path=/metrics/applications/prometheus
EOF
}

# Function to set Spark configurations
# https://spark.apache.org/docs/latest/monitoring.html#list-of-available-metrics-providers
set_spark_confs() {
	local SPARK_DEFAULTS_CONF_PATH="/databricks/driver/conf/00-databricks-otel.conf"

	cat <<EOF >>$SPARK_DEFAULTS_CONF_PATH
"spark.executor.processTreeMetrics.enabled" = "true"
"spark.metrics.appStatusSource.enabled" = "true"
"spark.metrics.namespace" = ""
"spark.sql.streaming.metricsEnabled" = "true"
"spark.ui.prometheus.enabled" = "true"
EOF
}

# Main logic
initialize_env
generate_config
set_spark_confs
init_spark_prometheus_servelet
setup_otelcol
