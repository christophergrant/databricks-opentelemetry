from databricks_opentelemetry_exporter.logs.export import create_databricks_volume_log_exporter

import logging
import os
from pathlib import Path

from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

def init_logging(export_path: str) -> LoggingHandler:
    """Initialize OpenTelemetry logging with Databricks exporter.
    
    Args:
        path: Path to the log directory where logs will be written
        
    Returns:
        LoggingHandler that can be added to Python loggers
    """

    path = Path(export_path)

    assert path.exists() & path.is_dir() & os.access(path, os.W_OK)

    # build the Resource -> LoggerProvider -> LogExporter -> LoggingHandler
    resource = Resource(
        attributes={
            ResourceAttributes.SERVICE_NAMESPACE: "acmecorp", 
            ResourceAttributes.SERVICE_NAME: "databricks",
        }
    )
    logger_provider = LoggerProvider(resource=resource)
    exporter = create_databricks_volume_log_exporter(log_dir=path)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
    handler =  LoggingHandler(logger_provider=logger_provider)

    # Add the handler to the root logger
    logging.getLogger().addHandler(handler) 

    # return handler
    return handler
