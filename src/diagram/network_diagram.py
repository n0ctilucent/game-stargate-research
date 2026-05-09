import pandas as pd
import networkx as nx
from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.compute import Server
from diagrams.onprem.edge import Server as EdgeNode
from diagrams.onprem.mlops import Triton  # Representing NPU/TPU
from diagrams.gcp.ml import VertexAI
from diagrams.onprem.network import Internet

def generate_dynamic_diagram(registry_path="registry.parquet"):
    # 1. Load Registry Data
    try:
        df = pd.read_parquet(registry_path)
    except FileNotFoundError:
        print("Registry not found. Render aborting.")
        return

    # 2. Build NetworkX Graph for Path Analysis
    G = nx.DiGraph()
    
    # Add Nodes from Registry
    for _, row in df.iterrows():
        G.add_node(row['host_target'], 
                   acceleration=row['acceleration'], 
                   status="Active")

    # 3. Render Visualization
    with Diagram("Bitsmasher Cluster Topology", show=False, direction="LR"):
        internet = Internet("Public Access")
        vertex = VertexAI("Vertex AI (Gemini 1.5)")

        with Cluster("Control Plane"):
            stargate = Server("Stargate")
            
        with Cluster("Compute Tier"):
            skynet = Triton("Skynet (Hailo-8L)")
            
            # Dynamically generate Jetson Cluster from Registry Filter
            jetsons = []
            jetson_df = df[df['host_target'].str.contains("Edge-J")]
            for node_name in jetson_df['host_target'].unique():
                jetsons.append(EdgeNode(node_name))

        with Cluster("Execution Layer"):
            chonk = Server("Chonk (Paper 1.21)")
            testing_field = Server("AI Testing Field")

        # Define Edges using Registry Logic
        vertex >> Edge(label="Mutation Payload", color="blue") >> stargate
        stargate >> Edge(label="RCON / MCP") >> chonk
        
        # Draw Voxel Pipeline
        skynet >> Edge(label="Push Primitive") >> jetsons
        for j in jetsons:
            j >> Edge(color="green", style="dashed") >> stargate
            
        stargate >> Edge(label="Inject Refined") >> testing_field

        print("Diagram updated based on latest Pandas Registry state.")

if __name__ == "__main__":
    generate_dynamic_diagram()
