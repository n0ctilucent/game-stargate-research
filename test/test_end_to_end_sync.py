import pytest
from internal.registry_manager import RegistryManager
from internal.vertex_bridge import VertexBridge
import time
from datetime import datetime

def test_voxel_time_sync_loop():
    # 1. Initialization
    reg = RegistryManager("registry.parquet")
    # Note: Using placeholder project-id until provided
    bridge = VertexBridge(project_id="PROJECT_ID_PENDING") 
    
    # 2. Simulate Edge-T Vision Detection
    # The 'vibe' is detected on the edge and sent to the control plane
    vibe_timestamp = datetime.now()
    model_id = f"test-build-{int(time.time())}"
    
    print(f"==> Edge-T detected 'Industrial' vibe at {vibe_timestamp}")
    
    # 3. Log to Registry (The 'Time' Sync Check)
    sync_time = reg.log_sync_event(model_id, "chonk:ai_field_01", enhanced=True)
    
    # Calculate drift between detection and logging
    drift = (sync_time - vibe_timestamp).total_seconds()
    print(f"==> Registry logged at {sync_time} (Drift: {drift}s)")
    
    assert drift < 0.5, f"Time drift too high: {drift}s. Check ntpsec status!"

    # 4. Verify Registry Persistence
    updated_df = reg.df
    assert model_id in updated_df['model_id'].values
    assert updated_df.iloc[-1]['vertex_enhanced'] == True
