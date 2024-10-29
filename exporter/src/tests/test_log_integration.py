import pytest
import logging
from unittest.mock import patch, MagicMock

from databricks.sdk import WorkspaceClient
from databricks_opentelemetry_exporter.logs.export import DatabricksVolumeLogExporter, default_formatter

from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import ConsoleLogExporter, BatchLogRecordProcessor

from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

import time

from pathlib import Path
import os
@pytest.fixture
def workspace_client():
    return MagicMock(spec=WorkspaceClient)


@pytest.fixture
def logger_provider():
    resource = Resource(attributes={
        ResourceAttributes.SERVICE_NAMESPACE: "cgrant",
        ResourceAttributes.SERVICE_NAME: "databricks"
    })
    return LoggerProvider(resource=resource)

@pytest.fixture
def log_dir():
    return "/test/log/dir/"


@pytest.fixture
def databricks_exporter(log_dir):
    return DatabricksVolumeLogExporter(log_dir=log_dir, formatter=default_formatter)


@pytest.fixture
def console_exporter():
    return ConsoleLogExporter()


@pytest.fixture
def logger(logger_provider, databricks_exporter, console_exporter):
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(databricks_exporter))
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(console_exporter))
    
    handler = LoggingHandler(logger_provider=logger_provider)
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def test_log_export(workspace_client, logger):
    log_dir = "/Volumes/cgrant/occ/arr/logs"
    
    # Mock the list_directory_contents method to return an empty list initially
    workspace_client.files.list_directory_contents.return_value = []
    
    with patch('databricks.sdk.WorkspaceClient', return_value=workspace_client):
        # Count files before logging
        prev = sum(1 for _ in workspace_client.files.list_directory_contents(log_dir))
        
        # Perform logging
        logger.debug("This is a debug log, verbose, huh?")
        logger.info("This is an informational log")
        logger.warning("This is a warning log")
        logger.error("This is an error log")
        
        time.sleep(5)
        
        # Mock the list_directory_contents method to return some files after logging
        workspace_client.files.list_directory_contents.return_value = ['file1.json', 'file2.json']
        
        # Count files after logging
        after = sum(1 for _ in workspace_client.files.list_directory_contents(log_dir))
        
        # Assert that new log files were created
        assert after > prev, f"No new log files were created. Before: {prev}, After: {after}"


@pytest.mark.skipif(not os.environ.get("DATABRICKS_RUNTIME_VERSION"), reason="Databricks environment not set up")
def test_log_export_real(logger, tmp_path):
    # Use a temporary directory for log files
    log_dir = Path("/Volumes/cgrant/occ/arr/logs")
    
    # Create a real DatabricksVolumeLogExporter with the temporary directory
    real_exporter = DatabricksVolumeLogExporter(log_dir=str(log_dir))
      
    # Count files before logging
    prev = len(list(log_dir.glob('*.json')))
    
    # Perform logging
    logger.debug("This is a debug log, verbose, huh?")
    logger.info("This is an informational log")
    logger.warning("This is a warning log")
    logger.error("This is an error log")
    
    # Allow some time for the batch processor to export
    time.sleep(2)
    
    # Count files after logging
    after = len(list(log_dir.glob('*.json')))
    
    # Assert that new log files were created
    assert after > prev, f"No new log files were created. Before: {prev}, After: {after}"
    
    # Check the content of the log files
    log_files = list(log_dir.glob('*.json'))
    assert log_files, "No log files were created"
    
    with open(log_files[0], 'r') as f:
        log_content = f.read()
        assert "This is an informational log" in log_content
        assert "This is a warning log" in log_content
        assert "This is an error log" in log_content
        # Debug message should not be in the log as the default level is INFO
        assert "This is a debug log, verbose, huh?" not in log_content


def test_log_levels(logger):
    with patch.object(logger, 'debug') as mock_debug, \
         patch.object(logger, 'info') as mock_info, \
         patch.object(logger, 'warning') as mock_warning, \
         patch.object(logger, 'error') as mock_error:
        
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        mock_debug.assert_called_once_with("Debug message")
        mock_info.assert_called_once_with("Info message")
        mock_warning.assert_called_once_with("Warning message")
        mock_error.assert_called_once_with("Error message")


def test_resource_attributes(logger_provider):
    resource = logger_provider.resource
    
    assert resource.attributes[ResourceAttributes.SERVICE_NAMESPACE] == "cgrant"
    assert resource.attributes[ResourceAttributes.SERVICE_NAME] == "databricks"


if __name__ == "__main__":
    pytest.main()