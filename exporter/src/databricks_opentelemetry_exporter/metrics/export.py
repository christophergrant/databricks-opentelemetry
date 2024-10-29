from opentelemetry.sdk.metrics import MetricReader
from opentelemetry.sdk.metrics.export import (
    MetricExporter,
    MetricExportResult,
    MetricsData,
)
from typing import Callable, Sequence
from uuid import uuid4
import os
import json

class DatabricksVolumeMetricsExporter(MetricExporter):
    """
    Implementation of :class:`MetricExporter` that writes metrics to a
    random file in a Databricks Volume.

    This class will only work on Databricks. It requires a volume to be mounted.
    """

    def __init__(
        self,
        metrics_dir: str = None,
        formatter: Callable[[MetricsData], str] = lambda data: json.dumps(data.to_dict(), default=str) + '\n',
    ):
        if not metrics_dir:
            raise ValueError("metrics_dir must be provided")
        
        self.metrics_dir = metrics_dir
        self.formatter = formatter
        self.file = None

    def export(self, metrics_data: MetricsData) -> MetricExportResult:
        try:
            filename = f"{uuid4()}.json"
            filepath = os.path.join(self.metrics_dir, filename)
            print(f"Writing metrics to file: {filepath}")
            self.file = open(filepath, "w")

            self.file.write(self.formatter(metrics_data))
            self.file.flush()
            self.file.close()
            self.file = None
            return MetricExportResult.SUCCESS
        except Exception as e:
            print(f"Error exporting metrics: {str(e)}")
            return MetricExportResult.FAILURE

    def shutdown(self):
        if self.file:
            self.file.close()

class DatabricksVolumeMetricReader(MetricReader):
    """
    Implementation of :class:`MetricReader` that uses DatabricksVolumeMetricsExporter
    to export metrics.
    """

    def __init__(
        self,
        exporter: DatabricksVolumeMetricsExporter = None,
        metrics_dir: str = "/Volumes/cgrant/occ/arr/metrics/",
    ):
        super().__init__()
        self.exporter = exporter or DatabricksVolumeMetricsExporter(metrics_dir=metrics_dir)

    def _receive_metrics(self, metrics_data: MetricsData) -> None:
        self.exporter.export(metrics_data)

    def shutdown(self, timeout_millis: float = 30_000, **kwargs) -> None:
        self.exporter.shutdown()
