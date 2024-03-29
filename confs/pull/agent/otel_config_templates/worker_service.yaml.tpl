pipelines:
  metrics:
    receivers: [prometheus]
    processors: [attributes]
    exporters: [otlp]
