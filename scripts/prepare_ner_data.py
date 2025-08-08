# scripts/prepare_ner_data.py
"""
Prepare NER training data for HuggingFace token-classification.

Usage:
    python prepare_ner_data.py \
      --input_csv ../data/cyber-threat-intelligence_all.csv \
      --text_col text \
      --entities_col entities \
      --out_dir ../data/ner_prepared \
      --model_name dslim/bert-base-NER \
      --split 0.8 0.1 0.1

Notes:
- entities_col should contain a JSON string or Python-like list of dicts describing entities.
  Example entity dict format per row:
    [{"start": 10, "end": 16, "entity": "MALWARE"}, {"start":20,"end":30,"entity":"IPV4"}]
- If your entities format is different, inspect the parser function `parse_entities_field`.
"""

import argparse
import json
import os
import ast
from tqdm.auto import tqdm

import pandas as pd
from transformers import AutoTokenizer

def parse_entities_field(value):
    """
    Try to parse the entities column to a list of dicts.
    Accept JSON strings, Python-like strings, or empty values.
    Expected dict keys: start, end, entity (or label)
    """
    if pd.isna(value):
        return []
    if isinstance(value, list):
        return value
    s = str(value).strip()
    # If empty or '[]'
    if s == "" or s == "[]" or s.lower() == "nan":
        return []
    # Try json loads
    try:
        parsed = json.loads(s)
        return parsed if isinstance(parsed, list) else []
    except Exception:
        pass
    # Try ast literal_eval
    try:
        parsed = ast.literal_eval(s)
        return parsed if isinstance(parsed, list) else []
    except Exception:
        pass
    # Try to handle simple bracketed "[(...)]" forms
    return []

def char_labels_to_token_labels(text, entities, tokenizer, label_all_tokens=True):
    """
    Convert char-span entity annotations to token-level BIO labels using tokenizer.
    Returns: tokens (list of str), labels (list of BIO labels)
    """
    # entities: list of dicts containing start,end and entity or label
    ents = []
    for e in entities:
        # Normalize keys
        e_start = e.get("start") or e.get("begin") or e.get("span_start")
        e_end = e.get("end") or e.get("stop") or e.get("span_end")
        e_label = e.get("entity") or e.get("label") or e.get("type") or e.get("tag")
        if e_start is None or e_end is None or e_label is None:
            continue
        try:
            e_start = int(e_start)
            e_end = int(e_end)
            ents.append({"start": e_start, "end": e_end, "label": str(e_label).upper()})
        except Exception:
            continue

    # tokenize with offsets
    encoding = tokenizer(text, return_offsets_mapping=True, truncation=True)
    offsets = encoding["offset_mapping"]
    # map tokens -> BIO
    labels = ["O"] * len(offsets)
    for ent in ents:
        ent_start = ent["start"]
        ent_end = ent["end"]
        ent_label = ent["label"]
        # find tokens that overlap with char span
        token_indices = []
        for i, (off_start, off_end) in enumerate(offsets):
            if off_end == 0 and off_start == 0:
                # special tokens may have (0,0)
                continue
            # overlap condition
            if not (off_end <= ent_start or off_start >= ent_end):
                token_indices.append(i)
        if not token_indices:
            # entity not aligned (maybe because of tokenization/truncation)
            continue
        # assign B- and I- with label
        labels[token_indices[0]] = f"B-{ent_label}"
        for ti in token_indices[1:]:
            labels[ti] = f"I-{ent_label}"

    # decode tokens to readable tokens (for debugging)—use tokenizer.convert_ids_to_tokens if needed
    tokens = tokenizer.convert_ids_to_tokens(encoding["input_ids"])
    # Return only tokens and labels. Note special tokens like [CLS]/[SEP] will have labels 'O' or (0,0)
    return tokens, labels, encoding

def build_dataset_from_csv(input_csv, text_col, entities_col, model_name, out_dir, split_ratios=(0.8,0.1,0.1), max_samples=None):
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    df = pd.read_csv(input_csv)
    df.columns = [c.strip() for c in df.columns]
    if text_col not in df.columns:
        raise KeyError(f"text column '{text_col}' not found in {input_csv}. Available: {df.columns}")

    rows = []
    for i, r in tqdm(df.iterrows(), total=len(df)):
        if max_samples and len(rows) >= max_samples:
            break
        text = r[text_col]
        ents = parse_entities_field(r.get(entities_col, "[]"))
        tokens, labels, encoding = char_labels_to_token_labels(str(text), ents, tokenizer)
        # convert to simple list form for saving
        rows.append({
            "id": str(i),
            "text": str(text),
            "input_ids": encoding["input_ids"],
            "attention_mask": encoding["attention_mask"],
            # tokens and labels aligned to tokens (same length as input_ids)
            "tokens": tokens,
            "labels": labels
        })

    # shuffle and split
    from sklearn.model_selection import train_test_split
    train_val, test = train_test_split(rows, test_size=split_ratios[2], random_state=42)
    train, val = train_test_split(train_val, test_size=split_ratios[1]/(split_ratios[0]+split_ratios[1]), random_state=42)

    os.makedirs(out_dir, exist_ok=True)
    def write_jsonl(list_rows, path):
        with open(path, "w", encoding="utf8") as f:
            for r in list_rows:
                f.write(json.dumps(r) + "\n")

    write_jsonl(train, os.path.join(out_dir, "train.jsonl"))
    write_jsonl(val, os.path.join(out_dir, "validation.jsonl"))
    write_jsonl(test, os.path.join(out_dir, "test.jsonl"))
    print(f"Prepared datasets written to {out_dir}: train({len(train)}), val({len(val)}), test({len(test)})")
    return out_dir

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_csv", required=True, help="Path to input CSV")
    parser.add_argument("--text_col", default="text", help="Column name containing text")
    parser.add_argument("--entities_col", default="entities", help="Column name containing entity annotations")
    parser.add_argument("--model_name", default="dslim/bert-base-NER", help="Tokenizer/model name for alignment")
    parser.add_argument("--out_dir", default="../data/ner_prepared", help="Output dir for prepared files")
    parser.add_argument("--split", nargs=3, type=float, default=[0.8,0.1,0.1], help="Train/Val/Test split ratios")
    parser.add_argument("--max_samples", type=int, default=None, help="Max rows to process (for quick tests)")
    args = parser.parse_args()

    build_dataset_from_csv(
        args.input_csv,
        args.text_col,
        args.entities_col,
        args.model_name,
        args.out_dir,
        split_ratios=args.split,
        max_samples=args.max_samples
    )
