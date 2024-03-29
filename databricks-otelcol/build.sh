env GOOS=linux GOARCH=amd64 builder --config ./databricks-otelcol/builder-config-amd64.yaml
env GOOS=linux GOARCH=arm64 builder --config ./databricks-otelcol/builder-config-arm64.yaml
