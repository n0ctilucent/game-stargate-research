mport Cluster, Diagram, Edge
from diagrams.onprem.compute import Server
from diagrams.onprem.edge import Server as Jetson
from diagrams.gcp.ml import VertexAI
from internal.registry_manager import RegistryManager

def render_live_topology():
    reg = RegistryManager()
    df = reg.df

    with Diagram("Bitsmasher Stargate Control Plane", show=False, direction="TB"):
        vertex = VertexAI("Vertex AI ($10/mo Tier)")
        
        with Cluster("Stargate Control Hub"):
            stargate = Server("Stargate")
            registry_db = Server("Pandas/LFS Registry")

        with Cluster("Voxel Acceleration Cluster"):
            # Map the recovered Jetson nodes
            jetsons = [Jetson(f"Edge-J0{i}") for i in range(1, 5)]

        with Cluster("Minecraft World-State"):
            chonk = Server("Chonk (Paper 26.1.5)")
            testing_field = Server("AI Testing Field")

        # Logic Flow
        vertex >> Edge(label="Stylistic Enhancement", color="blue") >> stargate
        stargate >> jetsons >> Edge(label="Greeble Injection") >> chonk
        stargate >> registry_db

if __name__ == "__main__":
    render_live_topology()a
