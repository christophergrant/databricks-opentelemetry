prometheus:
  config:
    scrape_configs:
      - job_name: 'node_exporter'
        scrape_interval: 10s
        static_configs:
          - targets: ['${SPARK_NODE_IP}:9100']
      - job_name: 'spark_metrics'
        scrape_interval: 10s
        metrics_path: '/metrics/prometheus'
        static_configs:
          - targets: ['${SPARK_NODE_IP}:40001']
      - job_name: 'spark_exec_metrics'
        scrape_interval: 10s
        metrics_path: '/metrics/executors/prometheus'
        static_configs:
          - targets: ['${SPARK_NODE_IP}:40001']

otlp:
  protocols:
    grpc:
      endpoint: "0.0.0.0:4317"

