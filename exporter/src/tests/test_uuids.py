import pytest
from databricks_opentelemetry_exporter.util.uuids import uuid7
import re


def test_uuid7_format():
    # Test that generated UUID matches expected format
    uuid = uuid7()
    uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')
    assert uuid_pattern.match(uuid), f"UUID {uuid} does not match expected format"


def test_uuid7_uniqueness():
    # Test that multiple generated UUIDs are unique
    uuids = [uuid7() for _ in range(1000)]
    assert len(set(uuids)) == len(uuids), "Generated UUIDs are not unique"


def test_uuid7_monotonicity():
    # Test that UUIDs are monotonically increasing (timestamp portion)
    uuid1 = uuid7()
    uuid2 = uuid7()
    # Compare first 8 chars which contain timestamp
    assert uuid2[:8] >= uuid1[:8], "UUIDs are not monotonically increasing"


def test_uuid7_version():
    # Test that UUID version is 7
    uuid = uuid7()
    version = uuid[14]
    assert version == '7', f"UUID version {version} is not 7"


def test_uuid7_variant():
    # Test that UUID variant bits are correct (should be 0b10)
    uuid = uuid7()
    variant_char = uuid[19]
    assert variant_char in '89ab', f"UUID variant {variant_char} is not correct"
