import os
import pandas as pd
from datetime import datetime
from google import genai

class VertexBridge:
    def __init__(self, project_id=None, location="us-central1", model_name="gemini-1.5-flash-002"):
        # Pivot to the unified GenAI SDK to clear the June 2026 Deprecation Warning.
        # This will automatically pick up the GEMINI_API_KEY from your .envrc 
        # as specified in the Emerald Mirror deployment checklist.
        self.client = genai.Client()
        self.model_name = model_name
        self.registry_path = "registry.parquet"
        self.monthly_budget_calls = 150

    def _check_budget(self):
        """Audit the Pandas registry for current month API usage."""
        if not os.path.exists(self.registry_path):
            return True
        df = pd.read_parquet(self.registry_path)
        if df.empty:
            return True
        df['last_sync'] = pd.to_datetime(df['last_sync'])
        current_month = df[df['last_sync'].dt.month == datetime.now().month]
        usage = current_month[current_month['vertex_enhanced'] == True].shape[0]
        return usage < self.monthly_budget_calls

    def enhance_voxels(self, primitive_metadata, style_tag):
        """Sends local voxel metadata + vision classification to the AI."""
        if not self._check_budget():
            return "BUDGET_EXCEEDED: Falling back to local Llama-3 reasoning."

        prompt = f"""
        Act as the Lead Architect for the Bitsmasher Minecraft Cluster.
        We have a primitive foundation: {primitive_metadata}
        The Edge-T vision sensor reports the build context is: {style_tag}
        Task: Provide an 'Emerald Mirror' greebling delta in JSON format.
        Focus on depth, lighting, and material contrast.
        """
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text
