from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import (
    SpanExporter,
    SpanExportResult,
)

from typing import Callable, Sequence
from uuid import uuid4
import os
import json

class DatabricksVolumeTraceExporter(SpanExporter):
    """
    Implementation of :class:`SpanExporter` that writes trace spans to a
    random file in a Databricks Volume.

    This class will only work on Databricks. It requires a volume to be mounted.
    """

    def __init__(
        self,
        trace_dir: str = None,
        formatter: Callable[[ReadableSpan], str] = lambda span: json.dumps(span.to_json(), default=str) + '\n',
    ):
        if not trace_dir:
            raise ValueError("trace_dir must be provided")
        self.trace_dir = trace_dir
        self.formatter = formatter
        self.file = None

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        filename = f"{uuid4()}.json"
        filepath = os.path.join(self.trace_dir, filename)
        print(f"Writing trace spans to file: {filepath}")
        self.file = open(filepath, "w")

        for span in spans:
            self.file.write(self.formatter(span))
        self.file.flush()
        self.file.close()
        self.file = None
        return SpanExportResult.SUCCESS

    def shutdown(self):
        if self.file:
            self.file.close()
