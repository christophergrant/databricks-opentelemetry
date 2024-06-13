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
2. (Optionally) Spin up sample observability infrastructure on your Databricks workspace using bootstrap scripts in setup/.
3. Install the collector by specifying a cluster init script and setting any environment variables required by the init script
    - If testing against the sample infrastructure, use the script [sample_init.sh](agent/sample_init.sh) and set both `DB_API_TOKEN` and `OTLP_HTTP_ENDPOINT`
    - If deploying against an OTLP collector that's not hosted on a Databricks cluster, use [init.sh](agent/init.sh) and set `OTLP_HTTP_ENDPOINT`

### Debugging

#### Debugging the Cluster Collector

If you aren't seeing any metrics flowing through to your target observability system you should start your debugging journey by verifying that the OTEL collector running on your cluster is running smoothly.

1. Check the status of the Open Telemetry collector service.  In a notebook run this cell:

``` 
%sh

systemctl status databricks-otelcol.service
```

You should expect to see the `Active` field set to `active (running)`.  Whether the service is up or down, you're not getting
metrics so you should still proceed to the next step and analyze the service logs to gather more signal.

2. Check the collector service's logs.  In a notebook run this cell:

```
%sh

journalctl -u databricks-otelcol.service
```

The collector's logs are pretty good and will tell you if there were any issues exporting metrics such as network reachability
or issues with your configuration.  

If all is going well from the collector's perspective you'll see a bunch of friendly looking INFO messages stating that metrics
are being exported.  If this is the case the problem is likely upstream in the target collector.

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
