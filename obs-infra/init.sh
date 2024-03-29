#!/bin/bash
set -euxo pipefail

# install otelcol
wget https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v0.96.0/otelcol_0.96.0_linux_amd64.deb
sudo dpkg -i otelcol_0.96.0_linux_amd64.deb

# TODO ARM support
#sudo apt-get update
#sudo apt-get -y install wget systemctl
#wget https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v0.96.0/otelcol_0.96.0_linux_arm64.deb
#sudo dpkg -i otelcol_0.96.0_linux_arm64.deb

# configure otelcol
tee /etc/otelcol/config.yaml >/dev/null <<'EOF'
receivers:
  otlp:
    protocols:
      http:

exporters:
  logging:
    loglevel: debug
  prometheus:
    endpoint: "0.0.0.0:9464"

service:
  pipelines:
    metrics:
      receivers: [otlp]
      exporters: [logging, prometheus]
EOF

systemctl enable otelcol
systemctl restart otelcol

PROMETHEUS_VERSION="2.51.0"

# Function to download and extract Prometheus
download_and_extract() {
	ARCHIVE_NAME="prometheus-${PROMETHEUS_VERSION}.${ARCH}.tar.gz"
	DOWNLOAD_URL="https://github.com/prometheus/prometheus/releases/download/v${PROMETHEUS_VERSION}/${ARCHIVE_NAME}"

	echo "Downloading Prometheus for ${ARCH} from ${DOWNLOAD_URL}"
	wget -q -O "/tmp/${ARCHIVE_NAME}" "${DOWNLOAD_URL}"
	if [ $? -ne 0 ]; then
		echo "Failed to download Prometheus. Exiting."
		exit 1
	fi

	echo "Extracting Prometheus..."
	tar -xzf "/tmp/${ARCHIVE_NAME}" -C "/opt/"
	if [ $? -ne 0 ]; then
		echo "Failed to extract Prometheus. Exiting."
		exit 1
	fi

	echo "Prometheus installation complete."
}

create_systemd_service() {
	echo "Creating Prometheus systemd service..."

	cat <<EOF >/etc/systemd/system/prometheus.service
[Unit]
Description=Prometheus Monitoring System
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
ExecStart=/opt/prometheus-${PROMETHEUS_VERSION}.${ARCH}/prometheus \
    --config.file=/opt/prometheus-${PROMETHEUS_VERSION}.${ARCH}/prometheus.yml \
    --storage.tsdb.path=/opt/prometheus-${PROMETHEUS_VERSION}.${ARCH}/data \
    --web.listen-address=:9090

[Install]
WantedBy=multi-user.target
EOF

	systemctl daemon-reload
	systemctl enable prometheus
	systemctl start prometheus
	echo "Prometheus systemd service created and started."
}

check_prometheus() {
	echo "Checking if Prometheus is running..."
	for i in {1..10}; do
		if systemctl -q is-active prometheus; then
			echo "Prometheus is up and running."
			break
		fi
		echo "Waiting for Prometheus to start..."
		sleep 10
	done
}

configure_prometheus() {
	local prometheus_config_file=/opt/prometheus-${PROMETHEUS_VERSION}.${ARCH}/prometheus.yml

	# Check if the Prometheus configuration file exists
	if [[ ! -f "$prometheus_config_file" ]]; then
		echo "Prometheus configuration file not found: $prometheus_config_file"
		return 1
	fi

	# Configuration to scrape OTLP Collector
	local scrape_config_otlp="
  - job_name: 'otlp_collector'
    scrape_interval: 10s
    static_configs:
      - targets: ['localhost:9464']"

	# Append configurations to the Prometheus configuration file
	echo "$scrape_config_otlp" >>"$prometheus_config_file"

	echo "Scrape configurations added to $prometheus_config_file"

}

ARCH=$(uname -m)
case "$ARCH" in
x86_64)
	ARCH="linux-amd64"
	;;
aarch64)
	ARCH="linux-arm64"
	;;
*)
	echo "Unsupported architecture: ${ARCH}"
	exit 1
	;;
esac

mkdir -p /opt/prometheus
download_and_extract
configure_prometheus
create_systemd_service
check_prometheus
