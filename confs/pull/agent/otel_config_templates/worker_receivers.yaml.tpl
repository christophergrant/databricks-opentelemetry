prometheus:
  config:
    scrape_configs:
      - job_name: 'node_exporter'
        scrape_interval: 10s
        static_configs:
          - targets: ['${SPARK_NODE_IP}:9100']

#      - job_name: 'spark_metrics'
#        scrape_interval: 10s
#        metrics_path: '/metrics/prometheus'
#        static_configs:
#          - targets: ['localhost:40001']

