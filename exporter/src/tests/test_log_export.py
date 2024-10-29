import pytest
import json
import os
from pathlib import Path
import tempfile

from opentelemetry.sdk._logs import LogData, LogRecord
from opentelemetry.sdk._logs.export import LogExportResult

from databricks_opentelemetry_exporter.logs.export import (
    DatabricksVolumeLogExporter,
    create_databricks_volume_log_exporter,
    default_formatter
)

def test_default_formatter():
    record = LogRecord(
        timestamp=1234567890,
        trace_id=None,
        span_id=None,
        trace_flags=None,
        severity_text="INFO",
        severity_number=9,
        body="Test message",
        resource=None,
        attributes={}
    )
    
    formatted = default_formatter(record)
    # Verify it's valid JSON and ends with newline
    assert json.loads(formatted.rstrip())
    assert formatted.endswith('\n')

def test_create_exporter_validates_dir():
    with pytest.raises(ValueError):
        create_databricks_volume_log_exporter(None)
    
    with pytest.raises(AssertionError):
        create_databricks_volume_log_exporter("/nonexistent/path")

def test_exporter_writes_logs():
    with tempfile.TemporaryDirectory() as tmpdir:
        exporter = DatabricksVolumeLogExporter(tmpdir, default_formatter)
        
        record = LogRecord(
            timestamp=1234567890,
            trace_id=None,
            span_id=None,
            trace_flags=None,
            severity_text="INFO", 
            severity_number=9,
            body="Test message",
            resource=None,
            attributes={}
        )
        
        batch = [LogData(record, 1234567890)]
        
        result = exporter.export(batch)
        assert result == LogExportResult.SUCCESS
        
        # Verify a file was created
        files = os.listdir(tmpdir)
        assert len(files) == 1
        assert files[0].endswith('.json')
        
        # Verify file contents
        with open(os.path.join(tmpdir, files[0])) as f:
            content = f.read()
            assert json.loads(content.rstrip())
            assert "Testmessage" in content

def test_exporter_handles_empty_batch():
    with tempfile.TemporaryDirectory() as tmpdir:
        exporter = DatabricksVolumeLogExporter(tmpdir, default_formatter)
        result = exporter.export([])
        assert result == LogExportResult.SUCCESS
        assert len(os.listdir(tmpdir)) == 0  # No files created

def test_exporter_handles_formatting_error():
    def bad_formatter(record):
        raise Exception("Formatting error")
        
    with tempfile.TemporaryDirectory() as tmpdir:
        exporter = DatabricksVolumeLogExporter(tmpdir, bad_formatter)
        
        record = LogRecord(
            timestamp=1234567890,
            trace_id=None,
            span_id=None,
            trace_flags=None,
            severity_text="INFO",
            severity_number=9,
            body="Test message",
            resource=None,
            attributes={}
        )
        
        batch = [LogData(record, 1234567890)]
        result = exporter.export(batch)
        assert result == LogExportResult.FAILURE

def test_exporter_handles_file_collision():
    with tempfile.TemporaryDirectory() as tmpdir:
        exporter = DatabricksVolumeLogExporter(tmpdir, default_formatter)
        
        record = LogRecord(
            timestamp=1234567890,
            trace_id=None,
            span_id=None,
            trace_flags=None,
            severity_text="INFO",
            severity_number=9, 
            body="Test message",
            resource=None,
            attributes={}
        )
        
        batch = [LogData(record, 1234567890)]
        
        # Create two batches - should create two different files
        exporter.export(batch)
        exporter.export(batch)
        
        files = os.listdir(tmpdir)
        assert len(files) == 2
        assert files[0] != files[1]
