import os

def is_running_on_databricks() -> bool:
    if os.getenv("DATABRICKS_RUNTIME_VERSION"):
        return True
    return False
