terraform {
  required_providers {
    databricks = {
      source = "databricks/databricks"
    }
  }
}

provider "databricks" {
}

variable "repo_path" {
  description = "The workspace path to the databricks-openteletry repository"
  type        = string
  default     = "/Repos/databricks/opentelemetry"
}

variable "spin_up_obs_node" {
  description = "Whether to enable the optional feature"
  type        = bool
  default     = true
}

data "databricks_node_type" "stable" {
  local_disk = true
  min_cores  = 16
}

data "databricks_spark_version" "latest" {
  long_term_support = true
}

resource "databricks_cluster" "opentelemetry" {

  count = var.spin_up_obs_node ? 1 : 0

  cluster_name            = "opentelemetry"
  spark_version           = data.databricks_spark_version.latest.id
  node_type_id            = data.databricks_node_type.stable.id
  autotermination_minutes = 0
  num_workers             = 0

  spark_conf = {
    # Single-node
    "spark.databricks.cluster.profile" : "singleNode"
    "spark.master" : "local[*]"
  }

  custom_tags = {
    "ResourceClass" = "SingleNode"
  }

  init_scripts {
    workspace {
      destination = "${var.repo_path}/setup/init.sh"
    }
  }

  cluster_log_conf {
    dbfs {
      destination = "dbfs:/cluster-logs"
    }
  }

}

resource "databricks_repo" "databricks_opentelemetry" {
  url  = "https://github.com/christophergrant/databricks-opentelemetry.git"
  path = var.repo_path
}


output "cluster_id" {
  # Output the id of the obs cluster only if it exists
  value       = length(databricks_cluster.opentelemetry) > 0 ? databricks_cluster.opentelemetry[0].id : ""
  description = "The ID of the Databricks cluster"
}

