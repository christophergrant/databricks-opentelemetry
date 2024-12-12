from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import (
    SpanExporter,
    SpanExportResult,
)

from typing import Callable, Sequence
import os
import json

from databricks_opentelemetry_exporter.util.uuids import uuid7

def default_formatter(span: ReadableSpan) -> str:
    return (
        span.to_json().replace("\n", "")
         + "\n"
    )

class DatabricksVolumeTraceExporter(SpanExporter):
    """
    Implementation of :class:`SpanExporter` that writes trace spans to a
    random file in a Databricks Volume.

    This class will only work on Databricks. It requires a volume to be mounted.
    """

    def __init__(
        self,
        trace_dir: str = None,
        formatter: Callable[[ReadableSpan], str] = default_formatter,
    ):
        if not trace_dir:
            raise ValueError("trace_dir must be provided")
        if not os.path.exists(trace_dir):
            raise ValueError(f"trace_dir {trace_dir} does not exist")
        if not os.path.isdir(trace_dir):
            raise ValueError(f"trace_dir {trace_dir} is not a directory")
        if not os.access(trace_dir, os.W_OK):
            raise ValueError(f"trace_dir {trace_dir} is not writable")
            
        self.trace_dir = trace_dir
        self.formatter = formatter

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        try:
            filename = f"{uuid7()}.json"
            filepath = os.path.join(self.trace_dir, filename)

            with open(filepath, "w") as f:
                for span in spans:
                    f.write(self.formatter(span))
                f.flush()
                os.fsync(f.fileno())

            return SpanExportResult.SUCCESS
        except Exception:
            return SpanExportResult.FAILURE

    def shutdown(self):
        pass
