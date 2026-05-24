import pandas as pd
import networkx as nx
import os
from datetime import datetime

class RegistryManager:
    def __init__(self, db_path="registry.parquet"):
        self.db_path = db_path
        self.columns = [
            'model_id', 'version', 'host_target', 'acceleration', 
            'format', 'vertex_enhanced', 'last_sync', 'tokens_used'
        ]
        self._load_or_init()

    def _load_or_init(self):
        if os.path.exists(self.db_path):
            self.df = pd.read_parquet(self.db_path)
        else:
            self.df = pd.DataFrame(columns=self.columns)
            self.df.to_parquet(self.db_path)

    def log_sync_event(self, model_id, host, enhanced=False):
        """Logs the exact moment a voxel payload is processed."""
        new_event = {
            'model_id': model_id,
            'version': '1.0-sync-test',
            'host_target': host,
            'acceleration': 'Hailo-8L' if 'skynet' in host else 'None',
            'format': 'schem',
            'vertex_enhanced': enhanced,
            'last_sync': datetime.now(),
            'tokens_used': 0
        }
        self.df = pd.concat([self.df, pd.DataFrame([new_event])], ignore_index=True)
        self.df.to_parquet(self.db_path)
        return new_event['last_sync']
