import pandas as pd
from datetime import datetime
import vertexai
from vertexai.generative_models import GenerativeModel

class VertexBridge:
    def __init__(self, project_id, location="us-central1"):
        # Initialize the Google Cloud Vertex AI SDK
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel("gemini-1.5-pro")
        self.registry_path = "registry.parquet"

    def get_monthly_usage(self):
        """Calculates current monthly spend from the registry."""
        df = pd.read_parquet(self.registry_path)
        # Filter for current month and count Vertex-enhanced operations
        df['last_sync'] = pd.to_datetime(df['last_sync'])
        usage = df[df['last_sync'].dt.month == datetime.now().month].shape[0]
        return usage

    def enhance_voxels(self, primitive_metadata, style_tag):
        """
        Sends the 'Foundation' data to Vertex AI for 'Emerald Mirror' greebling.
        """
        if self.get_monthly_usage() > 100:
            return "BUDGET_EXCEEDED: Falling back to local Llama-3 logic."

        prompt = f"""
        System: Act as an architect for the Bitsmasher Minecraft Cluster.
        Context: The Edge-T node detected a '{style_tag}' vibe.
        Task: Enhance this primitive building: {primitive_metadata}.
        Output: Return a JSON delta of block mutations for the Jetson cluster to process.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
