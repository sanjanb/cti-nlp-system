"""
Enhanced NER Model with Transformer Fine-tuning and All Improvements
- Data Augmentation for Named Entity Recognition
- Advanced Feature Engineering and Contextual Embeddings
- Multiple Transformer Models with Hyperparameter Optimization
- Ensemble Methods and Cross-Validation
- Comprehensive Error Analysis for Entity Recognition
"""

import os
import json
import argparse
import pandas as pd
import numpy as np
from datasets import Dataset, DatasetDict
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import re
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import classification_report, f1_score

# Hugging Face imports
from transformers import (
    AutoTokenizer, AutoModelForTokenClassification,
    DataCollatorForTokenClassification, TrainingArguments, Trainer,
    EarlyStoppingCallback
)
from seqeval.metrics import (
    classification_report as seq_classification_report,
    f1_score as seq_f1_score,
    accuracy_score as seq_accuracy_score
)

# For ensemble and advanced techniques
import torch
from transformers import pipeline
import warnings
warnings.filterwarnings('ignore')

class EnhancedNERTrainer:
    def __init__(self, data_dir="../data/ner_prepared"):
        self.data_dir = data_dir
        self.models = {}
        self.tokenizers = {}
        self.entity_keywords = {
            'ORG': ['company', 'corporation', 'microsoft', 'google', 'apple', 'organization'],
            'PERSON': ['analyst', 'researcher', 'hacker', 'user', 'admin'],
            'MISC': ['malware', 'virus', 'trojan', 'ransomware', 'exploit', 'vulnerability'],
            'LOC': ['country', 'city', 'region', 'network', 'server', 'domain']
        }
        self.model_configs = {
            'distilbert': 'distilbert-base-uncased',
            'bert': 'bert-base-uncased',
            'roberta': 'roberta-base',
            'bert_ner': 'dslim/bert-base-NER'
        }
    
    def load_jsonl_as_hf_dataset(self, jsonl_dir):
        """Load train/validation/test JSONL files into dict."""
        def load_file(path):
            rows = []
            if os.path.exists(path):
                with open(path, "r", encoding="utf8") as f:
                    for line in f:
                        rows.append(json.loads(line))
            return rows

        dataset_dict = {
            "train": load_file(os.path.join(jsonl_dir, "train.jsonl")),
            "validation": load_file(os.path.join(jsonl_dir, "validation.jsonl")),
            "test": load_file(os.path.join(jsonl_dir, "test.jsonl")),
        }
        
        # Filter out empty datasets
        dataset_dict = {k: v for k, v in dataset_dict.items() if v}
        
        return dataset_dict
    
    def build_label_list(self, dataset_dict):
        """Collect unique labels from all splits."""
        labels = set()
        for split in dataset_dict.keys():
            for r in dataset_dict[split]:
                for l in r["labels"]:
                    labels.add(l)
        return sorted(list(labels))
    
    def augment_ner_data(self, dataset_dict, augment_factor=2):
        """Augment NER data with entity-aware techniques"""
        print("Performing NER-specific data augmentation...")
        
        augmented_data = {}
        
        for split in ['train']:  # Only augment training data
            if split not in dataset_dict:
                continue
                
            original_data = dataset_dict[split]
            augmented_samples = []
            
            # Analyze entity distribution
            entity_counts = Counter()
            for sample in original_data:
                for label in sample['labels']:
                    if label != 'O':
                        entity_counts[label] += 1
            
            print(f"Entity distribution in {split}: {entity_counts}")
            
            # Augment samples with rare entities
            for sample in original_data:
                augmented_samples.append(sample)  # Keep original
                
                # Check if sample contains rare entities
                rare_entities = [label for label in sample['labels'] 
                               if label != 'O' and entity_counts[label] < entity_counts.most_common()[0][1] * 0.3]
                
                if rare_entities:
                    # Create variations for samples with rare entities
                    variations = self._create_ner_variations(sample, augment_factor)
                    augmented_samples.extend(variations)
            
            augmented_data[split] = augmented_samples
            print(f"{split}: {len(original_data)} -> {len(augmented_samples)} samples")
        
        # Copy validation and test without augmentation
        for split in ['validation', 'test']:
            if split in dataset_dict:
                augmented_data[split] = dataset_dict[split]
        
        return augmented_data
    
    def _create_ner_variations(self, sample, max_variations=2):
        """Create variations of NER samples"""
        variations = []
        tokens = sample['tokens']
        labels = sample['labels']
        
        # Variation 1: Add context prefix/suffix
        context_prefixes = [
            "Security alert:",
            "Threat detected:",
            "Analysis shows:",
            "Report indicates:"
        ]
        
        for prefix in context_prefixes[:max_variations]:
            new_tokens = prefix.split() + tokens
            new_labels = ['O'] * len(prefix.split()) + labels
            
            variations.append({
                'tokens': new_tokens,
                'labels': new_labels
            })
        
        # Variation 2: Entity substitution (simple)
        entity_substitutions = {
            'Microsoft': ['Google', 'Apple', 'Amazon'],
            'Windows': ['Linux', 'macOS', 'Android'],
            'malware': ['virus', 'trojan', 'ransomware']
        }
        
        new_tokens = tokens.copy()
        for i, token in enumerate(tokens):
            if token in entity_substitutions and len(variations) < max_variations:
                for substitute in entity_substitutions[token][:1]:  # Use first substitute
                    substituted_tokens = tokens.copy()
                    substituted_tokens[i] = substitute
                    
                    variations.append({
                        'tokens': substituted_tokens,
                        'labels': labels.copy()
                    })
                    break
        
        return variations[:max_variations]
    
    def extract_ner_features(self, dataset_dict):
        """Extract features relevant to NER performance"""
        print("Extracting NER-specific features...")
        
        features = {
            'entity_distribution': Counter(),
            'token_length_stats': [],
            'entity_length_stats': [],
            'context_patterns': defaultdict(int)
        }
        
        for split in dataset_dict:
            for sample in dataset_dict[split]:
                tokens = sample['tokens']
                labels = sample['labels']
                
                # Entity distribution
                for label in labels:
                    features['entity_distribution'][label] += 1
                
                # Token and entity length statistics
                features['token_length_stats'].extend([len(token) for token in tokens])
                
                # Entity span analysis
                current_entity = None
                entity_length = 0
                
                for label in labels:
                    if label.startswith('B-'):
                        if current_entity:
                            features['entity_length_stats'].append(entity_length)
                        current_entity = label[2:]
                        entity_length = 1
                    elif label.startswith('I-') and current_entity:
                        entity_length += 1
                    else:
                        if current_entity:
                            features['entity_length_stats'].append(entity_length)
                            current_entity = None
                            entity_length = 0
                
                # Context patterns (simple)
                text = ' '.join(tokens).lower()
                for pattern in ['attack', 'threat', 'malicious', 'exploit']:
                    if pattern in text:
                        features['context_patterns'][pattern] += 1
        
        return features
    
    def create_ner_models(self):
        """Create multiple NER models for ensemble"""
        print("Creating NER model configurations...")
        
        models = {}
        
        for name, model_path in self.model_configs.items():
            try:
                print(f"Loading {name} ({model_path})...")
                models[name] = {
                    'model_path': model_path,
                    'config': {
                        'learning_rate': 2e-5,
                        'epochs': 3,
                        'batch_size': 16
                    }
                }
            except Exception as e:
                print(f"Failed to load {name}: {e}")
        
        return models
    
    def optimize_ner_hyperparameters(self, model_path, train_dataset, val_dataset, 
                                   label_list, optimization_type='random'):
        """Hyperparameter optimization for NER models"""
        print(f"Optimizing hyperparameters for {model_path} using {optimization_type} search...")
        
        # Define hyperparameter space
        if optimization_type == 'grid':
            learning_rates = [1e-5, 2e-5, 5e-5]
            batch_sizes = [8, 16, 32]
            epochs = [3, 5]
        else:  # random search
            learning_rates = [1e-5, 2e-5, 3e-5, 5e-5]
            batch_sizes = [8, 16]
            epochs = [3, 4, 5]
        
        best_f1 = 0
        best_params = None
        best_model = None
        
        # Try different combinations
        param_combinations = []
        if optimization_type == 'grid':
            for lr in learning_rates:
                for bs in batch_sizes:
                    for ep in epochs:
                        param_combinations.append({'lr': lr, 'batch_size': bs, 'epochs': ep})
        else:
            import random
            random.seed(42)
            for _ in range(6):  # Try 6 random combinations
                param_combinations.append({
                    'lr': random.choice(learning_rates),
                    'batch_size': random.choice(batch_sizes),
                    'epochs': random.choice(epochs)
                })
        
        for i, params in enumerate(param_combinations):
            print(f"Trial {i+1}/{len(param_combinations)}: {params}")
            
            try:
                model, tokenizer = self._train_single_ner_model(
                    model_path, train_dataset, val_dataset, label_list,
                    learning_rate=params['lr'],
                    batch_size=params['batch_size'],
                    epochs=params['epochs'],
                    output_dir=f'../models/temp_ner_{i}'
                )
                
                # Evaluate
                f1 = self._evaluate_ner_model(model, tokenizer, val_dataset, label_list)
                
                if f1 > best_f1:
                    best_f1 = f1
                    best_params = params
                    best_model = (model, tokenizer)
                
                print(f"F1 score: {f1:.4f}")
                
            except Exception as e:
                print(f"Trial {i+1} failed: {e}")
                continue
        
        print(f"Best parameters: {best_params}")
        print(f"Best F1 score: {best_f1:.4f}")
        
        return best_model, best_params
    
    def _train_single_ner_model(self, model_path, train_dataset, val_dataset, label_list,
                               learning_rate=2e-5, batch_size=16, epochs=3, output_dir='../models/temp'):
        """Train a single NER model with given parameters"""
        
        # Load tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True)
        model = AutoModelForTokenClassification.from_pretrained(
            model_path,
            num_labels=len(label_list),
            id2label={i: label for i, label in enumerate(label_list)},
            label2id={label: i for i, label in enumerate(label_list)},
            ignore_mismatched_sizes=True
        )
        
        # Tokenize datasets
        def tokenize_and_align_labels(examples):
            tokenized_inputs = tokenizer(examples["tokens"], truncation=True, is_split_into_words=True)
            
            labels = []
            for i, label in enumerate(examples["labels"]):
                word_ids = tokenized_inputs.word_ids(batch_index=i)
                previous_word_idx = None
                label_ids = []
                for word_idx in word_ids:
                    if word_idx is None:
                        label_ids.append(-100)
                    elif word_idx != previous_word_idx:
                        label_ids.append(label_list.index(label[word_idx]))
                    else:
                        label_ids.append(-100)
                    previous_word_idx = word_idx
                labels.append(label_ids)
            
            tokenized_inputs["labels"] = labels
            return tokenized_inputs
        
        # Convert to HuggingFace datasets
        train_hf = Dataset.from_list(train_dataset)
        val_hf = Dataset.from_list(val_dataset) if val_dataset else None
        
        train_tokenized = train_hf.map(tokenize_and_align_labels, batched=True)
        val_tokenized = val_hf.map(tokenize_and_align_labels, batched=True) if val_hf else None
        
        # Data collator
        data_collator = DataCollatorForTokenClassification(tokenizer, return_tensors="pt")
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            evaluation_strategy="epoch" if val_tokenized else "no",
            logging_steps=100,
            save_strategy="epoch",
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            weight_decay=0.01,
            fp16=True,
            remove_unused_columns=False,
            load_best_model_at_end=True if val_tokenized else False,
            metric_for_best_model="eval_f1" if val_tokenized else None,
            save_total_limit=2
        )
        
        # Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_tokenized,
            eval_dataset=val_tokenized,
            data_collator=data_collator,
            tokenizer=tokenizer,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=2)] if val_tokenized else None
        )
        
        # Train
        trainer.train()
        
        return model, tokenizer
    
    def _evaluate_ner_model(self, model, tokenizer, test_dataset, label_list):
        """Evaluate NER model and return F1 score"""
        
        # Create pipeline
        ner_pipeline = pipeline(
            "ner",
            model=model,
            tokenizer=tokenizer,
            aggregation_strategy="simple",
            device=0 if torch.cuda.is_available() else -1
        )
        
        true_labels = []
        pred_labels = []
        
        for sample in test_dataset:
            tokens = sample['tokens']
            labels = sample['labels']
            
            # Get predictions
            text = ' '.join(tokens)
            try:
                predictions = ner_pipeline(text)
                
                # Convert predictions back to token-level labels
                pred_token_labels = ['O'] * len(tokens)
                
                for pred in predictions:
                    # Simple word-level alignment
                    entity_label = pred['entity_group'] if 'entity_group' in pred else pred['entity']
                    
                    # Find corresponding tokens (simplified)
                    start_word = len(text[:pred['start']].split())
                    end_word = len(text[:pred['end']].split())
                    
                    for i in range(max(0, start_word), min(len(tokens), end_word)):
                        if i < len(pred_token_labels):
                            pred_token_labels[i] = f"B-{entity_label}" if i == start_word else f"I-{entity_label}"
                
                true_labels.append(labels)
                pred_labels.append(pred_token_labels)
                
            except Exception as e:
                print(f"Prediction failed for sample: {e}")
                true_labels.append(labels)
                pred_labels.append(['O'] * len(tokens))
        
        # Calculate F1 score
        f1 = seq_f1_score(true_labels, pred_labels)
        
        return f1
    
    def ner_error_analysis(self, model, tokenizer, test_dataset, label_list, model_name="NER"):
        """Comprehensive error analysis for NER"""
        print(f"Performing error analysis for {model_name}...")
        
        # Create pipeline
        ner_pipeline = pipeline(
            "ner",
            model=model,
            tokenizer=tokenizer,
            aggregation_strategy="simple",
            device=0 if torch.cuda.is_available() else -1
        )
        
        true_labels = []
        pred_labels = []
        error_examples = []
        
        for i, sample in enumerate(test_dataset):
            tokens = sample['tokens']
            labels = sample['labels']
            text = ' '.join(tokens)
            
            try:
                predictions = ner_pipeline(text)
                
                # Convert predictions to token-level
                pred_token_labels = ['O'] * len(tokens)
                
                for pred in predictions:
                    entity_label = pred['entity_group'] if 'entity_group' in pred else pred['entity']
                    start_word = len(text[:pred['start']].split())
                    end_word = len(text[:pred['end']].split())
                    
                    for j in range(max(0, start_word), min(len(tokens), end_word)):
                        if j < len(pred_token_labels):
                            pred_token_labels[j] = f"B-{entity_label}" if j == start_word else f"I-{entity_label}"
                
                true_labels.append(labels)
                pred_labels.append(pred_token_labels)
                
                # Collect error examples
                if labels != pred_token_labels:
                    error_examples.append({
                        'text': text,
                        'true_labels': labels,
                        'pred_labels': pred_token_labels,
                        'tokens': tokens
                    })
                
            except Exception as e:
                print(f"Error in sample {i}: {e}")
                true_labels.append(labels)
                pred_labels.append(['O'] * len(tokens))
        
        # Generate classification report
        report = seq_classification_report(true_labels, pred_labels, digits=4)
        print("=== NER Classification Report ===")
        print(report)
        
        # Entity-level analysis
        entity_stats = defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0})
        
        for true_seq, pred_seq in zip(true_labels, pred_labels):
            true_entities = self._extract_entities(true_seq)
            pred_entities = self._extract_entities(pred_seq)
            
            for entity_type in set(true_entities.keys()) | set(pred_entities.keys()):
                true_set = set(true_entities.get(entity_type, []))
                pred_set = set(pred_entities.get(entity_type, []))
                
                entity_stats[entity_type]['tp'] += len(true_set & pred_set)
                entity_stats[entity_type]['fp'] += len(pred_set - true_set)
                entity_stats[entity_type]['fn'] += len(true_set - pred_set)
        
        # Plot entity-level performance
        entity_f1_scores = {}
        for entity_type, stats in entity_stats.items():
            if entity_type == 'O':
                continue
            precision = stats['tp'] / (stats['tp'] + stats['fp']) if (stats['tp'] + stats['fp']) > 0 else 0
            recall = stats['tp'] / (stats['tp'] + stats['fn']) if (stats['tp'] + stats['fn']) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            entity_f1_scores[entity_type] = f1
        
        # Visualizations
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        if entity_f1_scores:
            plt.bar(entity_f1_scores.keys(), entity_f1_scores.values())
            plt.title('F1 Score by Entity Type')
            plt.ylabel('F1 Score')
            plt.xticks(rotation=45)
        
        plt.subplot(2, 2, 2)
        label_counts = Counter([label for seq in true_labels for label in seq if label != 'O'])
        if label_counts:
            plt.bar(label_counts.keys(), label_counts.values())
            plt.title('True Entity Distribution')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(f'../results/ner_{model_name.lower()}_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Show error examples
        print(f"\n=== Error Examples ({len(error_examples)} total) ===")
        for i, example in enumerate(error_examples[:5]):
            print(f"\nExample {i+1}:")
            print(f"Text: {example['text']}")
            print(f"Tokens: {example['tokens']}")
            print(f"True:   {example['true_labels']}")
            print(f"Pred:   {example['pred_labels']}")
            print("-" * 80)
        
        return report, entity_f1_scores, error_examples
    
    def _extract_entities(self, labels):
        """Extract entity spans from BIO labels"""
        entities = defaultdict(list)
        current_entity = None
        start_idx = None
        
        for i, label in enumerate(labels):
            if label.startswith('B-'):
                if current_entity:
                    entities[current_entity].append((start_idx, i-1))
                current_entity = label[2:]
                start_idx = i
            elif label.startswith('I-'):
                if not current_entity or label[2:] != current_entity:
                    # Handle inconsistent tagging
                    if current_entity:
                        entities[current_entity].append((start_idx, i-1))
                    current_entity = label[2:]
                    start_idx = i
            else:  # O tag
                if current_entity:
                    entities[current_entity].append((start_idx, i-1))
                    current_entity = None
                    start_idx = None
        
        if current_entity:
            entities[current_entity].append((start_idx, len(labels)-1))
        
        return entities
    
    def train_enhanced_ner_ensemble(self, use_augmentation=True, optimization_type='random'):
        """Train enhanced NER models with ensemble"""
        print("Starting enhanced NER ensemble training...")
        
        # Create results directory
        os.makedirs('../results', exist_ok=True)
        os.makedirs('../models', exist_ok=True)
        
        # Load data
        dataset_dict = self.load_jsonl_as_hf_dataset(self.data_dir)
        
        if not dataset_dict:
            print("No data found! Please check your data directory.")
            return None, None, None
        
        print(f"Loaded datasets: {list(dataset_dict.keys())}")
        
        # Data augmentation
        if use_augmentation:
            dataset_dict = self.augment_ner_data(dataset_dict)
        
        # Extract features and analyze data
        features = self.extract_ner_features(dataset_dict)
        print(f"Entity distribution: {features['entity_distribution']}")
        
        # Build label list
        label_list = self.build_label_list(dataset_dict)
        print(f"Labels: {label_list}")
        
        # Create models
        model_configs = self.create_ner_models()
        
        trained_models = {}
        results = {}
        
        # Train each model
        for model_name, config in model_configs.items():
            print(f"\n=== Training {model_name} ===")
            
            try:
                # Optimize hyperparameters
                best_model, best_params = self.optimize_ner_hyperparameters(
                    config['model_path'],
                    dataset_dict['train'],
                    dataset_dict.get('validation', []),
                    label_list,
                    optimization_type
                )
                
                if best_model:
                    model, tokenizer = best_model
                    trained_models[model_name] = {'model': model, 'tokenizer': tokenizer}
                    
                    # Evaluate on test set
                    if 'test' in dataset_dict:
                        test_f1 = self._evaluate_ner_model(model, tokenizer, dataset_dict['test'], label_list)
                        results[model_name] = {
                            'test_f1': test_f1,
                            'best_params': best_params
                        }
                        print(f"{model_name} Test F1: {test_f1:.4f}")
                    
                    # Error analysis
                    if 'test' in dataset_dict:
                        report, entity_f1, errors = self.ner_error_analysis(
                            model, tokenizer, dataset_dict['test'], label_list, model_name
                        )
                        results[model_name]['entity_f1'] = entity_f1
                        results[model_name]['error_count'] = len(errors)
                    
                    # Save model
                    model_save_path = f'../models/enhanced_ner_{model_name}'
                    os.makedirs(model_save_path, exist_ok=True)
                    model.save_pretrained(model_save_path)
                    tokenizer.save_pretrained(model_save_path)
                    
                    print(f"Saved {model_name} to {model_save_path}")
                
            except Exception as e:
                print(f"Training failed for {model_name}: {e}")
                continue
        
        # Save results
        if results:
            results_df = pd.DataFrame(results).T
            results_df.to_csv('../results/ner_model_comparison_results.csv')
            print(f"\nResults saved to ../results/ner_model_comparison_results.csv")
        
        return trained_models, results, features

if __name__ == "__main__":
    # Initialize the enhanced NER trainer
    ner_trainer = EnhancedNERTrainer()
    
    # Train with all enhancements
    models, results, features = ner_trainer.train_enhanced_ner_ensemble(
        use_augmentation=True,
        optimization_type='random'  # Options: 'grid', 'random'
    )
    
    if results:
        print("\n=== NER Training Completed! ===")
        print("Results summary:")
        for model_name, metrics in results.items():
            print(f"{model_name}: Test F1 = {metrics['test_f1']:.4f}, "
                  f"Errors = {metrics.get('error_count', 'N/A')}")
    else:
        print("Training completed but no results available.")