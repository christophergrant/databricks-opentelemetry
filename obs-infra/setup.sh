#!/bin/bash

set -euxo pipefail

PROFILE=DEFAUL

# check if otelcol exists at /dbfs/databricks-otelcol, if it doesn't, upload it
databricks --profile $PROFILE api get /api/2.0/dbfs/get-status --json '{"path":"dbfs:/databricks-otelcol"}' || {
	# scope hack to avoid failing due to `set -e`
	databricks --profile "$PROFILE" fs cp push/agent/databricks-otelcol/databricks-otelcol/databricks-otelcol dbfs:/databricks-otelcol --overwrite
}

# upload repo including init script, links.py
databricks --profile $PROFILE workspace mkdirs /Workspace/databricks-opentelemetry
databricks --profile $PROFILE workspace import /Workspace/databricks-opentelemetry/init.sh --format AUTO --file push/agent/init.sh --overwrite
databricks --profile $PROFILE workspace import /Workspace/databricks-opentelemetry/links.py --format AUTO --file push/obs-infra/links.py --overwrite
databricks --profile $PROFILE workspace import /Workspace/databricks-opentelemetry/obs-infra-init.sh --format AUTO --file push/obs-infra/init.sh --overwrite

# launch mothership cluster
databricks --profile $PROFILE clusters create --json @prometheus.json

echo "Please go to your workspace and open /Workspace/databricks-opentelemetry/links. Once the prometheus cluster is up, run all of the cells in the notebook and follow the last set of steps there."
