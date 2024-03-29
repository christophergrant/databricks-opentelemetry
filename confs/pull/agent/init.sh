#!/bin/bash

set -euxo pipefail

# This script is tailored for use with Databricks nodes, which at time of writing, are Debian and Ubuntu-based systems.
# It is intended to identify the system's architecture and map it to a standardized
# architecture name used in Debian and Ubuntu ecosystems.
#
# Note: While the script aims for POSIX compliance and broad compatibility, its
# functionality and architecture mapping are specifically designed with Debian and
# Ubuntu-based systems in mind. It may not fully apply or function as expected in
# non-Debian/Ubuntu environments or with non-POSIX compliant shells.

# Please do not touch!
DATABRICKS_OBS_VERSION=0.0.1

DB_IS_DRIVER=${DB_IS_DRIVER:-false}
DB_DRIVER_IP=${DB_DRIVER_IP:-}
NODE_EXPORTER_VERSION=1.7.0
OTEL_COLLECTOR_VERSION=0.92.0
TEMPLATE_STORAGE_DIR=/dbfs/databricks-obs/otel/otel_config_templates/ # end slash is important
OTEL_LOCAL_DIR=/etc/otelcol/
export SPARK_NODE_IP=$(hostname -I | awk '{print $1}')

validate_and_map_arch() {
	arch=$(uname -m)

	case "$arch" in
	x86_64)
		echo "amd64"
		;;
	aarch64)
		echo "arm64"
		;;
	*)
		echo "Unsupported architecture: $arch. Only x86_64 (amd64) and aarch64 (arm64) are supported." >&2
		exit 1
		;;
	esac
}

CPU_ARCHITECTURE=$(validate_and_map_arch)

is_gpu_instance_type() {
	instance_to_check="$1"

	# Define the list of supported instance types with comments
	read -r -d '' supported_instance_types <<-EOM
		      # AWS Instances
		        g4dn.xlarge
		        g4dn.2xlarge
		        g4dn.4xlarge
		        g4dn.8xlarge
		        g4dn.12xlarge
		        g4dn.16xlarge
		        g5.2xlarge
		        g5.4xlarge
		        g5.8xlarge
		        g5.12xlarge
		        g5.16xlarge
		        g5.24xlarge
		        g5.48xlarge
		        g5.xlarge
		        p2.xlarge
		        p2.8xlarge
		        p2.16xlarge
		        p3.2xlarge
		        p3.8xlarge
		        p3.16xlarge
		        p3dn.24xlarge
		        p4d.24xlarge
		        p4de.24xlarge
		        p5.48xlarge
		      # Azure Instances
		      # TODO
		      # GCP Instances
		      # TODO
	EOM

	# Filter out comments and then check each instance type
	for instance in $(echo "$supported_instance_types" | grep -v '^#'); do
		if [ "$instance" = "$instance_to_check" ]; then
			return 0 # Instance found
		fi
	done

	return 1 # Instance not found
}

configure_otel_collector() {
	# Check the value of DB_IS_DRIVER and choose the appropriate templates
	if [[ "$DB_IS_DRIVER" == "TRUE" ]]; then
		RECEIVERS_TEMPLATE="${TEMPLATE_STORAGE_DIR}driver_receivers.yaml.tpl"
		EXPORTERS_TEMPLATE="${TEMPLATE_STORAGE_DIR}driver_exporters.yaml.tpl"
		SERVICE_TEMPLATE="${TEMPLATE_STORAGE_DIR}driver_service.yaml.tpl"
		PROCESSORS_TEMPLATE="${TEMPLATE_STORAGE_DIR}driver_processors.yaml.tpl"
	else
		RECEIVERS_TEMPLATE="${TEMPLATE_STORAGE_DIR}worker_receivers.yaml.tpl"
		EXPORTERS_TEMPLATE="${TEMPLATE_STORAGE_DIR}worker_exporters.yaml.tpl"
		SERVICE_TEMPLATE="${TEMPLATE_STORAGE_DIR}worker_service.yaml.tpl"
		PROCESSORS_TEMPLATE="${TEMPLATE_STORAGE_DIR}worker_processors.yaml.tpl"
	fi

	# Use envsubst to replace environment variables in the templates
	# and generate the corresponding .yaml files
	envsubst <"${RECEIVERS_TEMPLATE}" >"${OTEL_LOCAL_DIR}receivers.yaml"
	envsubst <"${EXPORTERS_TEMPLATE}" >"${OTEL_LOCAL_DIR}exporters.yaml"
	envsubst <"${SERVICE_TEMPLATE}" >"${OTEL_LOCAL_DIR}service.yaml"
	envsubst <"${PROCESSORS_TEMPLATE}" >"${OTEL_LOCAL_DIR}processors.yaml"

	# Generate the master config.yaml file
	cat <<EOF >"${OTEL_LOCAL_DIR}config.yaml"
# Include receivers configuration
receivers: \${file:${OTEL_LOCAL_DIR}receivers.yaml}

# Include exporters configuration
exporters: \${file:${OTEL_LOCAL_DIR}exporters.yaml}

# Include service configuration
service: \${file:${OTEL_LOCAL_DIR}service.yaml}
#
# Include service configuration
processors: \${file:${OTEL_LOCAL_DIR}processors.yaml}
EOF

	echo "Master config generated as config.yaml"
}

install_otel_collector() {
	local URL="https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v${OTEL_COLLECTOR_VERSION}/otelcol_${OTEL_COLLECTOR_VERSION}_linux_${CPU_ARCHITECTURE}.deb"
	local PACKAGE_NAME="otelcol_${OTEL_COLLECTOR_VERSION}_linux_${CPU_ARCHITECTURE}.deb"
	local INSTALL_PATH="/etc/otelcol"

	echo "Enter OTel Collector..."
	sudo mkdir -p "$INSTALL_PATH"
	configure_otel_collector

	echo "Installing OTel Collector..."
	wget "$URL"
	sudo DEBIAN_FRONTEND=noninteractive apt-get install -o Dpkg::Options::="--force-confold" -y ./"$PACKAGE_NAME" # i hate this
}

install_node_exporter() {
	echo "Installing Node Exporter..."
	local URL="https://github.com/prometheus/node_exporter/releases/download/v${NODE_EXPORTER_VERSION}/node_exporter-${NODE_EXPORTER_VERSION}.linux-${CPU_ARCHITECTURE}.tar.gz"
	local INSTALL_PATH="/opt/node_exporter"
	local ENABLED_COLLECTORS=(
		"cpu"
		"meminfo"
		"diskstats"
		"filesystem"
		"netdev"
		"loadavg"
		"vmstat"
		"stat"
		"netstat"
	)

	# Construct the flags for enabling specific connectors
	local ENABLE_FLAGS=""
	for collector in "${ENABLED_COLLECTORS[@]}"; do
		ENABLE_FLAGS+=" --collector.${collector}"

	done
	local EXEC_START="/opt/node_exporter/node_exporter --collector.disable-defaults ${ENABLE_FLAGS}"

	sudo mkdir -p /opt/node_exporter
	wget -O - "$URL" | sudo tar xz -C $INSTALL_PATH --strip-components=1
	echo "Creating and starting Node Exporter systemd service..."
	create_and_start_systemd_service "node-exporter" "$EXEC_START"
}

install_nvidia_dcgm() {
	echo "Installing Nvidia's DCGM exporter..."
	# Will need to import the binaries from Volumes or something... no binaries are distributed.
	# See if DCGM is pre-installed
	# maybe can skip this step if dcgmi being installed is all we need.
	# maybe see if dcgmi is installed, and if there is a gpu attached to the container
	# Add commands to fetch and install Node Exporter for your architecture
}

create_and_start_systemd_service() {
	local service_name=$1
	local exec_start=$2
	cat <<EOF >/etc/systemd/system/$service_name.service
[Unit]
Description=$service_name service

[Service]
ExecStart=$exec_start
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

	systemctl daemon-reload
	systemctl enable $service_name
	systemctl start $service_name
	verify_service_running $service_name
}

verify_service_running() {
	local service_name=$1

	if sudo systemctl is-active --quiet "$service_name"; then
		echo "$service_name is running."
	else
		echo "Error: $service_name is not running."
		exit 1
	fi
}

init_spark_prometheus_servelet() {
	cat <<EOF >/databricks/spark/conf/metrics.properties
*.source.jvm.class=org.apache.spark.metrics.source.JvmSource
*.sink.prometheusServlet.class=org.apache.spark.metrics.sink.PrometheusServlet
*.sink.prometheusServlet.path=/metrics/prometheus
master.sink.prometheusServlet.path=/metrics/master/prometheus
applications.sink.prometheusServlet.path=/metrics/applications/prometheus
EOF

}

set_spark_confs() {
	local SPARK_DEFAULTS_CONF_PATH="$DB_HOME/driver/conf/00-databricksobs-spark.conf"
	echo "Setting Spark confs at $SPARK_DEFAULTS_CONF_PATH"
	if [ ! -e $SPARK_DEFAULTS_CONF_PATH]; then
		touch $SPARK_DEFAULTS_CONF_PATH
	fi

	cat <<EOF >>$SPARK_DEFAULTS_CONF_PATH
"spark.executor.processTreeMetrics.enabled" = "true"
"spark.metrics.appStatusSource.enabled" = "true"
"spark.metrics.namespace" = ""
"spark.sql.streaming.metricsEnabled" = "true"
"spark.ui.prometheus.enabled" = "true"
EOF
}

# Main logic
apt-get install gettext -y
install_node_exporter
set_spark_confs
init_spark_prometheus_servelet
install_otel_collector

# TODO add check for GPU and run nvidia_dcgm

# TODO add validation for ensuring that these services are up

# TODO add detailed logging
