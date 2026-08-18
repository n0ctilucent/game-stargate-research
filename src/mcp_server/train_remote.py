"""
Remote Fine-Tuning Script executed inside Vertex AI Container.
"""
import argparse
import os
import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
from peft import LoraConfig
from trl import SFTTrainer

def parse_args():
    parser = argparse.ArgumentParser(description="Vertex AI Fine-Tuning Task")
    parser.add_argument("--model_id", type=str, default="google/gemma-2b", help="Base model checkpoint")
    parser.add_argument("--data_path", type=str, required=True, help="GCS URI or local path to tokenized dataset")
    parser.add_argument("--output_dir", type=str, default=os.getenv("AIP_MODEL_DIR", "/tmp/output"), help="Output directory for model artifacts")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=4, help="Per-device batch size")
    parser.add_argument("--lr", type=float, default=2e-4, help="Learning rate")
    return parser.parse_args()

def main():
    args = parse_args()
    print(f"=== Starting Vertex AI Training Job ===")
    print(f"Base Model: {args.model_id}")
    print(f"Dataset Path: {args.data_path}")
    print(f"Output Target: {args.output_dir}")

    # 1. Load Tokenizer & Model
    tokenizer = AutoTokenizer.from_pretrained(args.model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto"
    )

    # 2. Configure LoRA (Adapters keep training efficient)
    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]
    )

    # 3. Load Tokenized Dataset from GCS
    dataset = load_dataset("json", data_files={"train": args.data_path})

    # 4. Training Hyperparameters
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=2,
        learning_rate=args.lr,
        logging_steps=10,
        bf16=True,  # Optimal precision for NVIDIA L4 GPUs
        save_strategy="epoch",
        report_to="none"
    )

    # 5. Execute Training
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset["train"],
        peft_config=peft_config,
        dataset_text_field="text",
        max_seq_length=512,
        tokenizer=tokenizer,
        args=training_args,
    )

    trainer.train()

    # 6. Save Adapter Weights
    print(f"Saving fine-tuned LoRA adapters to {args.output_dir}")
    trainer.model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print("=== Training Complete ===")

if __name__ == "__main__":
    main()
