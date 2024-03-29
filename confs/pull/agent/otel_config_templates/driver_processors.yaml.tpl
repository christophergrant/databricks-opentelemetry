attributes:
  actions:
    - key: databricks_cluster_id 
      value: ${DB_CLUSTER_ID}
      action: insert
    - key: databricks_cluster_name
      value: ${DB_CLUSTER_NAME}
      action: insert
    - key: databricks_is_driver
      value: TRUE
      action: insert
filter:
  metrics:
    exclude:
      match_type: regexp
      metric_names:
        - .*_com_databricks_.*

