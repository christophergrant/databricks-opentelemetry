# Databricks OpenTelemetry

Databricks distribution for OpenTelemetry is an unofficial version of the upstream OpenTelemetry collector and includes out-of-the-box binaries and configurations for usage on all 3 Databricks cloud platforms.


## Features

- A Databricks-specific distribution of the OpenTelemetry collector
- A set of init scripts for running and configuring the collector
- Bootstrap scripts for those who do not yet have production-ready observability infrastructure, including setups for Prometheus and Grafana on a single-node cluster
- Grafana dashboard templates for visualizing pertinent Databricks cluster metrics

## Getting Started

### Prerequisites

- A Databricks workspace
- (Optional) Existing observability infrastructure that includes an opentelemetry endpoint

### Installation

1. Clone this repo to your Databricks workspace. We recommend making it read-only for non-admin users and service principals.
2. (Optionally) Spin up sample observability infrastructure on your Databricks workspace using bootstrap scripts.
3. Install the collector by specifying a cluster init script and setting two environment variables to point to your observability endpoint.

### Limitations
- Does not work with serverless compute
- Data access mode support matrix

| Data Access Mode        | Supported |
|-------------------------|:---------:|
| Single User             |     ✅    |
| Shared                  |     ❌    |
| No Isolation Shared     |     ✅    |
| Custom                  |     ✅    |

- [AWS Access Modes](https://docs.databricks.com/en/compute/configure.html#access-modes)
- [Azure Access Modes](https://learn.microsoft.com/en-us/azure/databricks/compute/configure#--access-modes)
- [GCP Access Modes](https://docs.gcp.databricks.com/en/compute/configure.html#access-modes)


## Other Information

### Current otelcol build
| Exporters | Processors | Extensions | Receivers |
|-----------|------------|------------|-----------|
| [Debug Exporter v0.96.0](https://pkg.go.dev/go.opentelemetry.io/collector/exporter/debugexporter@v0.96.0) | [Attributes Processor v0.96.0](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/processor/attributesprocessor@v0.96.0) | [Bearer Token Auth Extension v0.96.0](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/extension/bearertokenauthextension@v0.96.0) | [Host Metrics Receiver v0.96.0](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/receiver/hostmetricsreceiver@v0.96.0) |
| [OTLP HTTP Exporter v0.96.0](https://pkg.go.dev/go.opentelemetry.io/collector/exporter/otlphttpexporter@v0.96.0) | [Filter Processor v0.96.0](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/processor/filterprocessor@v0.96.0) | | [Prometheus Receiver v0.96.0](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/receiver/prometheusreceiver@v0.96.0) |
| [Prometheus Exporter v0.96.0](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/exporter/prometheusexporter@v0.96.0) |  |  | [Apache Spark Receiver v0.96.0](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/receiver/apachesparkreceiver@v0.96.0) |

If other modules are required, you are free to take our build scripts and create your own collector.
