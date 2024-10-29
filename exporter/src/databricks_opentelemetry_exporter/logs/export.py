from typing import Callable, Sequence
import os
from pathlib import Path
import threading

from databricks_opentelemetry_exporter.util.uuids import uuid7

from opentelemetry.sdk._logs import LogData, LogRecord
from opentelemetry.sdk._logs._internal.export import (
    LogExporter,
    LogExportResult,
)

def default_formatter(record: LogRecord) -> str:
    return (
        record.to_json().replace("\n", "")
        #.replace(" ", "")
         + "\n"
    )


def create_databricks_volume_log_exporter(
    log_dir: str = None,
    formatter: Callable[[LogRecord], str] = default_formatter,
) -> "DatabricksVolumeLogExporter":
    """
    Create an instance of DatabricksVolumeLogExporter.

    This function will only work on Databricks. It requires a volume to be mounted.
    """
    if not log_dir:
        raise ValueError("log_dir must be provided")
    path = Path(log_dir)
    assert path.exists() & path.is_dir() & os.access(path, os.W_OK)
    return DatabricksVolumeLogExporter(log_dir, formatter)


class DatabricksVolumeLogExporter(LogExporter):
    def __init__(self, log_dir: str, formatter: Callable[[LogRecord], str], disable_file_check: bool = False):
        self.log_dir = log_dir
        self.formatter = formatter
        self._lock = threading.Lock()
        # Remove unused self.file attribute
        # _dir_checked can be removed since we check on init
        
        # Check directory exists and is writable on init
        if not disable_file_check:
            if not os.path.exists(self.log_dir):
                raise PermissionError(f"Directory does not exist: {self.log_dir}")
            elif not os.access(self.log_dir, os.W_OK):
                raise PermissionError(f"No write permission for directory: {self.log_dir}")

    def _write_logs_to_file(self, filepath: str, batch: Sequence[LogData]):
        # Use 'x' mode to ensure we don't overwrite existing files
        try:
            with open(filepath, "x") as file:
                for data in batch:
                    try:
                        file.write(self.formatter(data.log_record))
                    except Exception as e:
                        # Log formatting errors shouldn't fail the whole batch
                        print(f"Error formatting log record: {str(e)}")
                file.flush()
                os.fsync(file.fileno())  # Ensure data is written to disk
        except FileExistsError:
            # Generate new filename if collision occurs
            new_filepath = os.path.join(self.log_dir, f"{uuid7()}.json")
            self._write_logs_to_file(new_filepath, batch)

    def export(self, batch: Sequence[LogData]) -> LogExportResult:
        if not batch:  # Don't create empty files
            return LogExportResult.SUCCESS
            
        try:
            with self._lock:  # Lock during file creation to prevent race conditions
                filename = f"{uuid7()}.json"
                filepath = os.path.join(self.log_dir, filename)
                self._write_logs_to_file(filepath, batch)

            return LogExportResult.SUCCESS
        except Exception as e:
            # Use proper logging instead of print
            import logging
            logging.error(f"Error exporting logs: {str(e)}")
            return LogExportResult.FAILURE

    def shutdown(self):
        # Implement proper shutdown
        # Could add cleanup of old log files here if needed
        pass