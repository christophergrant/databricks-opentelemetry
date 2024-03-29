pipelines:
  metrics:
    receivers: [otlp, prometheus]
    processors: [filter, attributes]
    exporters: [prometheus]
