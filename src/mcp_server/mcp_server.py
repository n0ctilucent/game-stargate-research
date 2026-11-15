import os
import pathlib
from fastmcp import FastMCP
from google.cloud import storage, aiplatform

_BASE_DIR = pathlib.Path(__file__).resolve().parent

mcp = FastMCP("research.bitsmasher.net")

@mcp.tool
def greet(name: str) -> str:
    """Health check greeting tool."""
    return f"Hello, {name}!"

@mcp.tool
def stage_and_train_vertex(
    staging_file: str = "/mnt/clusterfs2/staging/test_corpus.jsonl",
    gcs_bucket_name: str = "auth-research-franklin-ml-pipeline",
    model_id: str = "google/gemma-2-2b"
) -> str:
    """Uploads tokenized JSONL to GCS and launches a non-blocking Vertex AI CustomTrainingJob."""
    local_path = pathlib.Path(staging_file)
    if not local_path.exists():
        return f"Error: Local staging artifact not found at {staging_file}"

    project_id = os.getenv("GCP_PROJECT_ID", "auth-research-franklin")
    location = os.getenv("GCP_LOCATION", "us-central1")
    hf_token = os.getenv("HF_TOKEN", "")

    # 1. Upload dataset to Google Cloud Storage
    try:
        gcs_client = storage.Client(project=project_id)
        bucket = gcs_client.bucket(gcs_bucket_name)
        blob = bucket.blob(f"training/{local_path.name}")
        blob.upload_from_filename(str(local_path))
        gcs_data_uri = f"gs://{gcs_bucket_name}/training/{local_path.name}"
    except Exception as e:
        return f"GCS Upload Failed: {str(e)}"

    # 2. Launch Vertex AI Custom Training Job
    try:
        aiplatform.init(project=project_id, location=location)

        job = aiplatform.CustomTrainingJob(
            display_name="bitsmasher-gemma-finetune",
            script_path=str(_BASE_DIR / "train_remote.py"),
            container_uri="us-docker.pkg.dev/deeplearning-platform-release/gcr.io/huggingface-pytorch-training.cu121.2-2.bj:latest",
            requirements=["transformers", "peft", "trl", "datasets", "accelerate"]
        )

        job.run(
            args=[
                "--model_id", model_id,
                "--data_path", gcs_data_uri,
                "--output_dir", f"/gcs/{gcs_bucket_name}/output/model/",
                "--epochs", "3",
                "--batch_size", "2"
            ],
            environment_variables={"HF_TOKEN": hf_token},
            replica_count=1,
            machine_type="g2-standard-8",
            accelerator_type="NVIDIA_L4",
            accelerator_count=1,
            no_wait=True
        )
        return f"SUCCESS: Uploaded to {gcs_data_uri}. Vertex AI Job submitted to NVIDIA L4 GPU."
    except Exception as e:
        return f"Vertex AI Job Dispatch Failed: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8989)
