import pandas as pd
import networkx as nx
import os
from datetime import datetime

class RegistryManager:
    def __init__(self, db_path="../registry.parquet"):
        self.db_path = db_path
        self.columns = [
            'model_id', 'version', 'host_target', 'acceleration', 
            'format', 'vertex_enhanced', 'last_sync', 'tokens_used'
        ]
        self.G = nx.DiGraph()
        self._load_or_init()

    def _load_or_init(self):
        if os.path.exists(self.db_path) and os.path.getsize(self.db_path) > 0:
            self.df = pd.read_parquet(self.db_path)
        else:
            self.df = pd.DataFrame(columns=self.columns)
            self.df.to_parquet(self.db_path)

    def register_deployment(self, model_data):
        """Logs a deployment and updates the topology graph."""
        model_data['last_sync'] = datetime.now()
        new_row = pd.DataFrame([model_data])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self.df.to_parquet(self.db_path)
        
    def sync_topology(self):
        """Builds NetworkX graph from cluster state for Gephi/Analysis."""
        # Add core infrastructure
        self.G.add_node("Stargate", role="Control", hardware="Pi5-8GB")
        self.G.add_node("VertexAI", role="Cloud", hardware="Gemini-Pro")
        self.G.add_node("Chonk", role="Execution", hardware="Ryzen9")
        
        # Add dynamic Jetson nodes from recovered hardware
        for i in range(1, 5):
            node_id = f"Edge-J0{i}"
            self.G.add_node(node_id, role="Voxel-Math", hardware="Jetson-2GB")
            self.G.add_edge("Skynet", node_id, relationship="worker_dispatch")
            self.G.add_edge(node_id, "Stargate", relationship="schematic_return")

        # Export for Gephi manual analysis
        nx.write_gexf(self.G, "../cluster_topology.gexf")
