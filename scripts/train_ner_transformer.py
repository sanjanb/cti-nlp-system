# scripts/train_ner_transformer.py
"""
Fine-tune a transformer for NER (token-classification) using Hugging Face Trainer.

Usage:
  python train_ner_transformer.py \
    --data_dir ../data/ner_prepared \
    --model_name_or_path dslim/bert-base-NER \
    --output_dir ../backend/models/ner_model \
    --epochs 3 \
    --batch_size 8
"""

import os
import json
import argparse
from pathlib import Path
from datasets import load_dataset, Dataset, DatasetDict, ClassLabel, Sequence
import numpy as np
from transformers import (
    AutoTokenizer, AutoModelForTokenClassification,
    DataCollatorForTokenClassification, TrainingArguments, Trainer
)
from seqeval.metrics import classification_report as seq_classification_report

def load_jsonl_as_hf_dataset(jsonl_dir):
    def load_file(path):
        rows = []
        with open(path, "r", encoding="utf8") as f:
            for line in f:
                rows.append(json.loads(line))
        return rows
    train = load_file(os.path.join(jsonl_dir, "train.jsonl"))
    val = load_file(os.path.join(jsonl_dir, "validation.jsonl"))
    test = load_file(os.path.join(jsonl_dir, "test.jsonl"))
    return {"train": train, "validation": val, "test": test}

def build_label_list(dataset_dict):
    labels = set()
    for split in ["train", "validation", "test"]:
        for r in dataset_dict[split]:
            for l in r["labels"]:
                labels.add(l)
    labels = sorted(list(labels))
    # remove special tokens or empty? we keep 'O' and B-/I- labels
    return labels

def align_labels_with_tokenizer(batch, tokenizer, label2id):
    # input_ids and labels are already present from prepare step, but Trainer expects label ids
    # We'll map label strings to integers here. Also keep special tokens as -100 if needed.
    labels = []
    for example in batch:
        lbls = example["labels"]
        # Map each label string to id
        lbl_ids = [label2id.get(x, label2id.get("O")) for x in lbls]
        labels.append(lbl_ids)
    batch["labels"] = labels
    return batch

def compute_metrics(predictions, references, id2label):
    # predictions: logits -> convert to label strings
    preds = np.argmax(predictions, axis=2)
    pred_labels = []
    true_labels = []
    for i in range(len(preds)):
        pred = []
        true = []
        for j in range(len(preds[i])):
            p = id2label.get(int(preds[i][j]), "O")
            t = id2label.get(int(references[i][j]), "O")
            pred.append(p)
            true.append(t)
        pred_labels.append(pred)
        true_labels.append(true)
    # Use seqeval
    # seqeval expects lists of labels per token (excluding special tokens ideally)
    return seq_classification_report(true_labels, pred_labels, digits=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", required=True, help="Directory with train/validation/test jsonl prepared by prepare_ner_data.py")
    parser.add_argument("--model_name_or_path", default="dslim/bert-base-NER", help="Pretrained model name")
    parser.add_argument("--output_dir", required=True, help="Where to save fine-tuned model")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--learning_rate", type=float, default=5e-5)
    parser.add_argument("--fp16", action="store_true", help="Use FP16 if available")
    parser.add_argument("--push_to_hub", action="store_true")
    args = parser.parse_args()

    # Load prepared JSONL
    dataset_dict = load_jsonl_as_hf_dataset(args.data_dir)
    # Build label list
    label_list = build_label_list(dataset_dict)
    # Create mapping
    label_list_sorted = label_list  # keep order
    label2id = {label: i for i, label in enumerate(label_list_sorted)}
    id2label = {i: label for label, i in label2id.items()}

    # Convert to Hugging Face Dataset
    from datasets import Dataset
    def to_hf(split_rows):
        # dataset expects dict of lists
        return Dataset.from_list(split_rows)
    ds = DatasetDict({
        "train": to_hf(dataset_dict["train"]),
        "validation": to_hf(dataset_dict["validation"]),
        "test": to_hf(dataset_dict["test"])
    })

    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path, use_fast=True)
    model = AutoModelForTokenClassification.from_pretrained(
        args.model_name_or_path,
        num_labels=len(label_list_sorted),
        id2label=id2label,
        label2id=label2id
    )

    # Map labels to ids in dataset
    def map_labels(example):
        example["labels"] = [label2id.get(l, label2id.get("O")) for l in example["labels"]]
        return example
    ds = ds.map(map_labels, batched=False)

    data_collator = DataCollatorForTokenClassification(tokenizer, return_tensors="pt")

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        evaluation_strategy="epoch",
        logging_strategy="steps",
        logging_steps=100,
        save_strategy="epoch",
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        weight_decay=0.01,
        fp16=args.fp16,
        push_to_hub=args.push_to_hub,
        remove_unused_columns=False,
    )

    def compute_metrics_tr(pred):
        logits, labels = pred
        preds = np.argmax(logits, axis=-1)
        # convert to label strings
        pred_list = []
        true_list = []
        for i in range(len(preds)):
            p = []
            t = []
            for j in range(len(preds[i])):
                # skip padding? here we keep all tokens; for better metrics you may want to ignore special tokens
                p.append(id2label.get(int(preds[i][j]), "O"))
                t.append(id2label.get(int(labels[i][j]), "O"))
            pred_list.append(p)
            true_list.append(t)
        # Use seqeval for classification report (string)
        from seqeval.metrics import classification_report as seq_rep
        report = seq_rep(true_list, pred_list, digits=4)
        print("\n=== SEQEVAL REPORT ===\n")
        print(report)
        # returning nothing for Trainer (it expects dict). For fine-grained logging use callbacks.
        return {}

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=ds["train"],
        eval_dataset=ds["validation"],
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=None  # we print seqeval report in callback/training logs
    )

    trainer.train()

    # Save
    os.makedirs(args.output_dir, exist_ok=True)
    trainer.save_model(args.output_dir)
    # Save label maps
    with open(os.path.join(args.output_dir, "label2id.json"), "w", encoding="utf8") as f:
        json.dump(label2id, f, indent=2)
    with open(os.path.join(args.output_dir, "id2label.json"), "w", encoding="utf8") as f:
        json.dump(id2label, f, indent=2)

    print(f"Model fine-tuned and saved to {args.output_dir}")
