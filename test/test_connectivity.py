import pandas as pd
import os
import pytest

def test_registry_exists():
    """Verify the registry.parquet is present in the root."""
    assert os.path.exists("registry.parquet"), "Registry file missing from root."

def test_registry_load():
    """Verify that Pandas can read the registry schema."""
    try:
        df = pd.read_parquet("registry.parquet")
        # Ensure core columns exist even if empty
        expected_cols = ['model_id', 'vertex_enhanced', 'last_sync']
        for col in expected_cols:
            assert col in df.columns, f"Missing required column: {col}"
    except Exception as e:
        pytest.fail(f"Failed to load registry: {e}")
