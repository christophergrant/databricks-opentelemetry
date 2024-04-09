# Databricks OpenTelemetry

OpenTelemetry is an open source toolkit for the instrumentation, collection, and exporting of telemetry data - namely logs, metrics, and traces.

This is the repository for a distribution of OpenTelemetry that is configured for usage on Databricks.

## Features

This repository contains:

- A Databricks-specific distribution of the OpenTelemetry collector and a set of init scripts for running and configuring these collectors on Databricks compute nodes.
- Setup scripts for setting up an OpenTelemetry endpoint on Databricks itself (optional)
- Guides for how to read metrics from Databricks compute nodes and applications
- Templated dashboards for visualizing important Databricks cluster metrics

## How to use this repo

### Installation

1. Clone this repo to your Databricks workspace. We recommend making it read-only to all users.
2. (Optionally) Spin up sample observability infrastructure on your Databricks workspace using bootstrap scripts in obs-infra/.
3. Install the collector by specifying a cluster init script and setting two environment variables to point to your observability endpoint.

### Limitations
- Does not work with serverless compute
- Data access mode conditionally supported, see below chart

| Data Access Mode        | Supported |
|-------------------------|:---------:|
| Single User             |     ✅    |
| Shared                  |     ❌    |
| No Isolation Shared     |     ✅    |
| Custom                  |     ✅    |

- [AWS Access Modes](https://docs.databricks.com/en/compute/configure.html#access-modes)
- [Azure Access Modes](https://learn.microsoft.com/en-us/azure/databricks/compute/configure#--access-modes)
- [GCP Access Modes](https://docs.gcp.databricks.com/en/compute/configure.html#access-modes)

For Shared access mode, we recommend using an upcoming feature that allows groups to be assigned to single-user clusters.

## Other Information

### Current otelcol build
| Exporters | Processors | Extensions | Receivers |
|-----------|------------|------------|-----------|
| [Debug Exporter v0.96.0](https://pkg.go.dev/go.opentelemetry.io/collector/exporter/debugexporter@v0.96.0) | [Attributes Processor v0.96.0](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/processor/attributesprocessor@v0.96.0) | [Bearer Token Auth Extension v0.96.0](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/extension/bearertokenauthextension@v0.96.0) | [Host Metrics Receiver v0.96.0](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/receiver/hostmetricsreceiver@v0.96.0) |
| [OTLP HTTP Exporter v0.96.0](https://pkg.go.dev/go.opentelemetry.io/collector/exporter/otlphttpexporter@v0.96.0) | [Filter Processor v0.96.0](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/processor/filterprocessor@v0.96.0) | | [Prometheus Receiver v0.96.0](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/receiver/prometheusreceiver@v0.96.0) |
| [Prometheus Exporter v0.96.0](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/exporter/prometheusexporter@v0.96.0) |  |  | [Apache Spark Receiver v0.96.0](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/receiver/apachesparkreceiver@v0.96.0) |

If other modules are required, you are free to take our build scripts and create your own collector.
