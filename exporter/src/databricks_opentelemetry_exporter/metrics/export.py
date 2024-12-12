from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    MetricsData,
    MetricExporter, 
    MetricExportResult,
)

import json
import os
import random
import string

class DatabricksVolumeMetricsExporter(MetricExporter):
    """Custom OpenTelemetry exporter that writes metrics to random files"""
    
    def __init__(self, output_dir="./metrics_output"):
        self.output_dir = output_dir

    def export(self, metrics_data: MetricsData) -> MetricExportResult:
        try:
            # Generate random filename
            filename = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            filepath = os.path.join(self.output_dir, f"metrics_{filename}.json")

            # Convert metrics to dict format
            metrics_dict = {
                "resource": {
                    "attributes": dict(metrics_data.resource.attributes)
                },
                "scope_metrics": []
            }

            for scope_metrics in metrics_data.resource_metrics[0].scope_metrics:
                scope_data = {
                    "scope": {
                        "name": scope_metrics.scope.name,
                        "version": scope_metrics.scope.version,
                    },
                    "metrics": []
                }
                
                for metric in scope_metrics.metrics:
                    metric_data = {
                        "name": metric.name,
                        "description": metric.description,
                        "unit": metric.unit,
                        "data": []
                    }
                    
                    for point in metric.data.data_points:
                        point_data = {
                            "value": point.value,
                            "timestamp": point.timestamp,
                            "attributes": dict(point.attributes)
                        }
                        metric_data["data"].append(point_data)
                    
                    scope_data["metrics"].append(metric_data)
                
                metrics_dict["scope_metrics"].append(scope_data)

            # Write to file
            with open(filepath, 'w') as f:
                json_str = json.dumps(metrics_dict, indent=2).replace("\n", "")
                f.write(json_str + "\n")

            return MetricExportResult.SUCCESS
        except Exception:
            return MetricExportResult.FAILURE

    def shutdown(self):
        pass

    def force_flush(self, timeout_millis: float = 10_000) -> bool:
        return True

    def get_preferred_temporality(self) -> AggregationTemporality:
        return AggregationTemporality.CUMULATIVE
