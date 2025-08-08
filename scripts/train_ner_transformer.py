# scripts/train_ner_transformer.py
"""
Fine-tune a transformer for NER (token-classification) using Hugging Face Trainer.

Usage (PowerShell):
  python train_ner_transformer.py `
    --data_dir ../data/ner_prepared `
    --model_name_or_path dslim/bert-base-NER `
    --output_dir ../backend/models/ner_model `
    --epochs 3 `
    --batch_size 8
"""

import os
import json
import argparse
from datasets import Dataset, DatasetDict
import numpy as np
from transformers import (
    AutoTokenizer, AutoModelForTokenClassification,
    DataCollatorForTokenClassification, TrainingArguments, Trainer
)
from seqeval.metrics import classification_report as seq_classification_report


def load_jsonl_as_hf_dataset(jsonl_dir):
    """Load train/validation/test JSONL files into dict."""
    def load_file(path):
        rows = []
        with open(path, "r", encoding="utf8") as f:
            for line in f:
                rows.append(json.loads(line))
        return rows

    return {
        "train": load_file(os.path.join(jsonl_dir, "train.jsonl")),
        "validation": load_file(os.path.join(jsonl_dir, "validation.jsonl")),
        "test": load_file(os.path.join(jsonl_dir, "test.jsonl")),
    }


def build_label_list(dataset_dict):
    """Collect unique labels from all splits."""
    labels = set()
    for split in ["train", "validation", "test"]:
        for r in dataset_dict[split]:
            for l in r["labels"]:
                labels.add(l)
    return sorted(list(labels))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", required=True, help="Directory with train/validation/test jsonl prepared by prepare_ner_data.py")
    parser.add_argument("--model_name_or_path", default="dslim/bert-base-NER", help="Pretrained model name or path")
    parser.add_argument("--output_dir", required=True, help="Where to save fine-tuned model")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--learning_rate", type=float, default=5e-5)
    parser.add_argument("--fp16", action="store_true", help="Use FP16 if available")
    parser.add_argument("--push_to_hub", action="store_true")
    args = parser.parse_args()

    # 1. Load dataset
    dataset_dict = load_jsonl_as_hf_dataset(args.data_dir)

    # 2. Build label mapping
    label_list = build_label_list(dataset_dict)
    label2id = {label: i for i, label in enumerate(label_list)}
    id2label = {i: label for label, i in label2id.items()}

    # 3. Convert to HF Datasets
    def to_hf(split_rows):
        return Dataset.from_list(split_rows)

    ds = DatasetDict({
        "train": to_hf(dataset_dict["train"]),
        "validation": to_hf(dataset_dict["validation"]),
        "test": to_hf(dataset_dict["test"])
    })

    # 4. Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path, use_fast=True)
    model = AutoModelForTokenClassification.from_pretrained(
        args.model_name_or_path,
        num_labels=len(label_list),
        id2label=id2label,
        label2id=label2id,
        ignore_mismatched_sizes=True  # prevents size mismatch crash
    )

    # 5. Map string labels to IDs
    def map_labels(example):
        example["labels"] = [label2id.get(l, label2id["O"]) for l in example["labels"]]
        return example

    ds = ds.map(map_labels, batched=False)

    # 6. Data collator
    data_collator = DataCollatorForTokenClassification(tokenizer, return_tensors="pt")

    # 7. Training arguments (Transformers 4.55.0 syntax)
    training_args = TrainingArguments(
    output_dir=args.output_dir,
    evaluation_strategy="epoch", 
    logging_steps=100,
    save_strategy="epoch",
    num_train_epochs=args.epochs,
    per_device_train_batch_size=args.batch_size,
    per_device_eval_batch_size=args.batch_size,
    learning_rate=args.learning_rate,
    weight_decay=0.01,
    fp16=args.fp16,
    push_to_hub=args.push_to_hub,
    remove_unused_columns=False
)



    # 8. Optional metrics
    def compute_metrics_tr(pred):
        logits, labels = pred
        preds = np.argmax(logits, axis=-1)

        pred_list = []
        true_list = []
        for i in range(len(preds)):
            p = []
            t = []
            for j in range(len(preds[i])):
                p.append(id2label.get(int(preds[i][j]), "O"))
                t.append(id2label.get(int(labels[i][j]), "O"))
            pred_list.append(p)
            true_list.append(t)

        report = seq_classification_report(true_list, pred_list, digits=4)
        print("\n=== SEQEVAL REPORT ===\n")
        print(report)
        return {}

    # 9. Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=ds["train"],
        eval_dataset=ds["validation"],
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=None  # printing report manually
    )

    # 10. Train
    trainer.train()

    # 11. Save model and label maps
    os.makedirs(args.output_dir, exist_ok=True)
    trainer.save_model(args.output_dir)
    with open(os.path.join(args.output_dir, "label2id.json"), "w", encoding="utf8") as f:
        json.dump(label2id, f, indent=2)
    with open(os.path.join(args.output_dir, "id2label.json"), "w", encoding="utf8") as f:
        json.dump(id2label, f, indent=2)

    print(f"✅ Model fine-tuned and saved to {args.output_dir}")
