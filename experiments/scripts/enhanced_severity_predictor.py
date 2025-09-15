"""
Enhanced Severity Prediction Model with All Improvements
- Data Augmentation and Class Balancing
- Advanced Feature Engineering (domain-specific, contextual)
- Multiple Models with Hyperparameter Optimization
- Ensemble Methods and Cross-Validation
- Comprehensive Error Analysis
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV, RandomizedSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, confusion_matrix, f1_score, accuracy_score
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import SMOTE, RandomOverSampler
from imblearn.combine import SMOTETomek
import joblib
import os
import re
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from sentence_transformers import SentenceTransformer
import warnings
warnings.filterwarnings('ignore')

class EnhancedSeverityPredictor:
    def __init__(self, data_path="../data/Cybersecurity_Dataset.csv"):
        self.data_path = data_path
        self.models = {}
        self.vectorizers = {}
        self.severity_keywords = {
            'critical': ['critical', 'severe', 'urgent', 'immediate', 'emergency'],
            'high': ['high', 'dangerous', 'major', 'significant', 'serious'],
            'medium': ['medium', 'moderate', 'notable', 'important'],
            'low': ['low', 'minor', 'minimal', 'negligible']
        }
        self.threat_indicators = [
            'exploit', 'vulnerability', 'zero-day', 'backdoor', 'ransomware',
            'ddos', 'breach', 'compromise', 'malicious', 'attack'
        ]
        
    def load_and_prepare_data(self):
        """Load and prepare severity data with enhanced preprocessing"""
        print("Loading and preparing severity data...")
        
        df = pd.read_csv(self.data_path)
        df = df.rename(columns=lambda x: x.strip())
        
        text_col = "Cleaned Threat Description"
        severity_col = "Severity Score"
        
        # Drop missing values
        df = df.dropna(subset=[text_col, severity_col])
        
        # Map numeric severity to labels with more granular mapping
        def map_severity_enhanced(score):
            score = int(score)
            if score <= 1:
                return "Very Low"
            elif score == 2:
                return "Low"
            elif score == 3:
                return "Medium"
            elif score == 4:
                return "High"
            else:
                return "Critical"
        
        df["Severity_Label"] = df[severity_col].astype(int).apply(map_severity_enhanced)
        
        print(f"Dataset shape: {df.shape}")
        print(f"Severity distribution:\n{df['Severity_Label'].value_counts()}")
        
        return df[text_col], df["Severity_Label"], df[severity_col]
    
    def augment_severity_data(self, X, y, augment_factor=3):
        """Data augmentation specifically for severity prediction"""
        print("Performing severity-focused data augmentation...")
        
        class_counts = Counter(y)
        max_count = max(class_counts.values())
        
        X_augmented = list(X)
        y_augmented = list(y)
        
        # Augment underrepresented severity classes
        for severity_label in class_counts:
            if class_counts[severity_label] < max_count * 0.6:
                class_samples = [x for x, l in zip(X, y) if l == severity_label]
                
                for sample in class_samples[:min(len(class_samples), augment_factor)]:
                    variations = self._create_severity_variations(sample, severity_label)
                    X_augmented.extend(variations)
                    y_augmented.extend([severity_label] * len(variations))
        
        print(f"Original samples: {len(X)}")
        print(f"Augmented samples: {len(X_augmented)}")
        
        return np.array(X_augmented), np.array(y_augmented)
    
    def _create_severity_variations(self, text, severity_label):
        """Create severity-aware text variations"""
        variations = []
        
        # Add severity-specific keywords based on label
        severity_keywords = self.severity_keywords.get(severity_label.lower(), [])
        
        for keyword in severity_keywords[:2]:  # Limit to 2 keywords
            if keyword not in text.lower():
                variations.append(f"{text} This is a {keyword} threat.")
        
        # Intensity modifiers based on severity
        if severity_label in ['High', 'Critical']:
            variations.append(f"URGENT: {text}")
            variations.append(f"{text} Immediate action required.")
        elif severity_label in ['Very Low', 'Low']:
            variations.append(f"Minor issue: {text}")
            variations.append(f"{text} Low priority.")
        
        return variations[:2]  # Limit variations
    
    def extract_severity_features(self, texts, severity_scores=None):
        """Extract features specifically relevant to severity prediction"""
        print("Extracting severity-specific features...")
        
        features = []
        for i, text in enumerate(texts):
            text_lower = text.lower()
            feature_dict = {}
            
            # Severity keyword counts by category
            for severity, keywords in self.severity_keywords.items():
                feature_dict[f'severity_{severity}_count'] = sum(
                    text_lower.count(keyword) for keyword in keywords
                )
            
            # Threat indicator counts
            for indicator in self.threat_indicators:
                feature_dict[f'threat_{indicator}'] = text_lower.count(indicator)
            
            # Urgency indicators
            urgency_words = ['urgent', 'immediate', 'emergency', 'critical', 'asap']
            feature_dict['urgency_score'] = sum(text_lower.count(word) for word in urgency_words)
            
            # Impact indicators
            impact_words = ['damage', 'loss', 'compromise', 'breach', 'steal', 'destroy']
            feature_dict['impact_score'] = sum(text_lower.count(word) for word in impact_words)
            
            # Technical severity indicators
            tech_indicators = ['zero-day', 'rce', 'privilege escalation', 'root access']
            feature_dict['technical_severity'] = sum(text_lower.count(term) for term in tech_indicators)
            
            # Text intensity features
            feature_dict['exclamation_count'] = text.count('!')
            feature_dict['uppercase_ratio'] = sum(1 for c in text if c.isupper()) / len(text) if text else 0
            feature_dict['caps_words'] = len([w for w in text.split() if w.isupper() and len(w) > 2])
            
            # CVSS-like features
            feature_dict['has_exploit_code'] = 1 if 'exploit' in text_lower else 0
            feature_dict['affects_multiple'] = 1 if any(word in text_lower for word in ['multiple', 'widespread', 'global']) else 0
            feature_dict['requires_interaction'] = 1 if 'click' in text_lower or 'user' in text_lower else 0
            
            # Network indicators (higher severity often involves network)
            feature_dict['network_related'] = 1 if any(word in text_lower for word in ['network', 'remote', 'internet']) else 0
            
            # Add actual severity score if available (for training)
            if severity_scores is not None and i < len(severity_scores):
                feature_dict['original_severity_score'] = severity_scores[i]
            
            features.append(feature_dict)
        
        return pd.DataFrame(features).fillna(0)
    
    def create_severity_models(self):
        """Create models optimized for severity prediction"""
        print("Creating severity prediction models...")
        
        models = {
            'random_forest': RandomForestClassifier(n_estimators=200, random_state=42),
            'gradient_boosting': GradientBoostingClassifier(random_state=42),
            'xgboost': XGBClassifier(random_state=42, eval_metric='mlogloss'),
            'svm': SVC(probability=True, random_state=42),
            'logistic': LogisticRegression(max_iter=1000, random_state=42)
        }
        
        return models
    
    def severity_hyperparameter_optimization(self, model, X, y, search_type='random'):
        """Hyperparameter optimization for severity models"""
        print(f"Optimizing {type(model).__name__} with {search_type} search...")
        
        param_grids = {
            'random_forest': {
                'n_estimators': [100, 200, 300],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4],
                'bootstrap': [True, False]
            },
            'gradient_boosting': {
                'n_estimators': [100, 200],
                'learning_rate': [0.05, 0.1, 0.15],
                'max_depth': [3, 5, 7],
                'subsample': [0.8, 0.9, 1.0]
            },
            'xgboost': {
                'n_estimators': [100, 200, 300],
                'max_depth': [3, 5, 7],
                'learning_rate': [0.05, 0.1, 0.2],
                'subsample': [0.8, 0.9, 1.0],
                'colsample_bytree': [0.8, 0.9, 1.0]
            },
            'svm': {
                'C': [0.1, 1, 10, 100],
                'kernel': ['rbf', 'linear'],
                'gamma': ['scale', 'auto', 0.001, 0.01]
            },
            'logistic': {
                'C': [0.01, 0.1, 1, 10],
                'penalty': ['l1', 'l2'],
                'solver': ['liblinear', 'lbfgs']
            }
        }
        
        model_name = type(model).__name__.lower()
        if 'forest' in str(model):
            model_name = 'random_forest'
        elif 'gradient' in str(model):
            model_name = 'gradient_boosting'
        elif 'xgb' in str(model):
            model_name = 'xgboost'
        elif 'svc' in str(model):
            model_name = 'svm'
        elif 'logistic' in str(model):
            model_name = 'logistic'
        
        param_grid = param_grids.get(model_name, {})
        
        if search_type == 'grid':
            search = GridSearchCV(
                model, param_grid, cv=3, scoring='f1_weighted',
                n_jobs=-1, verbose=1
            )
        else:
            search = RandomizedSearchCV(
                model, param_grid, cv=3, scoring='f1_weighted',
                n_jobs=-1, verbose=1, n_iter=15, random_state=42
            )
        
        search.fit(X, y)
        
        print(f"Best parameters: {search.best_params_}")
        print(f"Best CV score: {search.best_score_:.4f}")
        
        return search.best_estimator_
    
    def severity_error_analysis(self, model, X_test, y_test, severity_scores_test, class_names):
        """Detailed error analysis for severity prediction"""
        print("Performing severity prediction error analysis...")
        
        y_pred = model.predict(X_test)
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred, labels=class_names)
        
        plt.figure(figsize=(12, 10))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Reds',
                   xticklabels=class_names, yticklabels=class_names)
        plt.title('Severity Prediction Confusion Matrix')
        plt.xlabel('Predicted Severity')
        plt.ylabel('Actual Severity')
        plt.tight_layout()
        plt.savefig('../results/severity_confusion_matrix.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Severity distribution analysis
        plt.figure(figsize=(15, 5))
        
        plt.subplot(1, 3, 1)
        pd.Series(y_test).value_counts().plot(kind='bar')
        plt.title('Actual Severity Distribution')
        plt.xticks(rotation=45)
        
        plt.subplot(1, 3, 2)
        pd.Series(y_pred).value_counts().plot(kind='bar')
        plt.title('Predicted Severity Distribution')
        plt.xticks(rotation=45)
        
        plt.subplot(1, 3, 3)
        accuracy_by_class = {}
        for class_name in class_names:
            mask = np.array(y_test) == class_name
            if mask.sum() > 0:
                accuracy_by_class[class_name] = accuracy_score(
                    np.array(y_test)[mask], np.array(y_pred)[mask]
                )
        
        plt.bar(accuracy_by_class.keys(), accuracy_by_class.values())
        plt.title('Accuracy by Severity Class')
        plt.xticks(rotation=45)
        plt.ylabel('Accuracy')
        
        plt.tight_layout()
        plt.savefig('../results/severity_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Feature importance (if available)
        if hasattr(model, 'feature_importances_'):
            feature_names = [f'feature_{i}' for i in range(len(model.feature_importances_))]
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            plt.figure(figsize=(12, 8))
            top_features = importance_df.head(20)
            plt.barh(top_features['feature'], top_features['importance'])
            plt.title('Top 20 Feature Importances for Severity Prediction')
            plt.xlabel('Importance')
            plt.tight_layout()
            plt.savefig('../results/severity_feature_importance.png', dpi=300, bbox_inches='tight')
            plt.show()
        
        # Classification report
        report = classification_report(y_test, y_pred, target_names=class_names, output_dict=True)
        
        # Show misclassified examples with severity context
        misclassified_indices = np.where(np.array(y_test) != np.array(y_pred))[0]
        
        print(f"Total misclassified samples: {len(misclassified_indices)}")
        print("\nSeverity Prediction Errors:")
        
        for i in misclassified_indices[:10]:
            if hasattr(X_test, 'iloc'):
                text_sample = X_test.iloc[i][:150] + "..."
            else:
                text_sample = str(X_test[i])[:150] + "..."
            
            actual_score = severity_scores_test.iloc[i] if hasattr(severity_scores_test, 'iloc') else severity_scores_test[i]
            
            print(f"\nExample {i}:")
            print(f"Text: {text_sample}")
            print(f"Original Score: {actual_score}")
            print(f"True Label: {y_test.iloc[i] if hasattr(y_test, 'iloc') else y_test[i]}")
            print(f"Predicted: {y_pred[i]}")
            print("-" * 80)
        
        return report
    
    def train_enhanced_severity_model(self, use_augmentation=True, balance_method='smote',
                                    search_type='random', cv_folds=5):
        """Train enhanced severity prediction model"""
        print("Starting enhanced severity model training...")
        
        # Create results directory
        os.makedirs('../results', exist_ok=True)
        
        # Load data
        X, y, severity_scores = self.load_and_prepare_data()
        
        # Data augmentation
        if use_augmentation:
            X, y = self.augment_severity_data(X, y)
            # Note: severity_scores might not align after augmentation
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # For error analysis, we need the original severity scores
        # Split them the same way (only for non-augmented data)
        if not use_augmentation:
            _, severity_scores_test = train_test_split(
                severity_scores, test_size=0.2, random_state=42, stratify=y
            )
        else:
            severity_scores_test = pd.Series([3] * len(y_test))  # Default for augmented data
        
        # Feature extraction
        # 1. TF-IDF features
        tfidf_vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
        X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
        X_test_tfidf = tfidf_vectorizer.transform(X_test)
        
        # 2. Severity-specific features
        severity_features_train = self.extract_severity_features(X_train)
        severity_features_test = self.extract_severity_features(X_test)
        
        # Combine features
        from scipy.sparse import hstack
        X_train_combined = hstack([X_train_tfidf, severity_features_train.values])
        X_test_combined = hstack([X_test_tfidf, severity_features_test.values])
        
        # Handle class imbalance
        if balance_method != 'none':
            if balance_method == 'smote':
                sampler = SMOTE(random_state=42)
            elif balance_method == 'random_oversample':
                sampler = RandomOverSampler(random_state=42)
            elif balance_method == 'smote_tomek':
                sampler = SMOTETomek(random_state=42)
            
            if balance_method != 'class_weight':
                X_train_balanced, y_train_balanced = sampler.fit_resample(X_train_combined, y_train)
            else:
                X_train_balanced, y_train_balanced = X_train_combined, y_train
        else:
            X_train_balanced, y_train_balanced = X_train_combined, y_train
        
        # Create and train models
        models = self.create_severity_models()
        
        best_models = {}
        results = {}
        
        for name, model in models.items():
            print(f"\nTraining {name} for severity prediction...")
            
            # Set class weights if needed
            if hasattr(model, 'class_weight') and balance_method == 'class_weight':
                model.set_params(class_weight='balanced')
            
            # Hyperparameter optimization
            try:
                optimized_model = self.severity_hyperparameter_optimization(
                    model, X_train_balanced, y_train_balanced, search_type
                )
                best_models[name] = optimized_model
            except Exception as e:
                print(f"Hyperparameter optimization failed for {name}: {e}")
                model.fit(X_train_balanced, y_train_balanced)
                best_models[name] = model
            
            # Cross-validation
            skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
            cv_scores = []
            
            for fold, (train_idx, val_idx) in enumerate(skf.split(X_train_balanced, y_train_balanced)):
                X_train_fold = X_train_balanced[train_idx]
                X_val_fold = X_train_balanced[val_idx]
                y_train_fold = np.array(y_train_balanced)[train_idx]
                y_val_fold = np.array(y_train_balanced)[val_idx]
                
                best_models[name].fit(X_train_fold, y_train_fold)
                y_pred_fold = best_models[name].predict(X_val_fold)
                
                f1 = f1_score(y_val_fold, y_pred_fold, average='weighted')
                cv_scores.append(f1)
            
            # Test evaluation
            y_pred = best_models[name].predict(X_test_combined)
            test_f1 = f1_score(y_test, y_pred, average='weighted')
            test_accuracy = accuracy_score(y_test, y_pred)
            
            results[name] = {
                'cv_mean': np.mean(cv_scores),
                'cv_std': np.std(cv_scores),
                'test_f1': test_f1,
                'test_accuracy': test_accuracy
            }
            
            print(f"{name} - Test F1: {test_f1:.4f}, Accuracy: {test_accuracy:.4f}")
        
        # Create ensemble
        print("\nCreating severity prediction ensemble...")
        ensemble_models = [(name, model) for name, model in best_models.items()]
        ensemble = VotingClassifier(estimators=ensemble_models, voting='soft')
        ensemble.fit(X_train_balanced, y_train_balanced)
        
        # Evaluate ensemble
        y_pred_ensemble = ensemble.predict(X_test_combined)
        ensemble_f1 = f1_score(y_test, y_pred_ensemble, average='weighted')
        ensemble_accuracy = accuracy_score(y_test, y_pred_ensemble)
        
        print(f"Ensemble - Test F1: {ensemble_f1:.4f}, Accuracy: {ensemble_accuracy:.4f}")
        
        # Error analysis
        class_names = sorted(np.unique(y))
        best_model_name = max(results, key=lambda x: results[x]['test_f1'])
        print(f"\nPerforming error analysis on best model: {best_model_name}")
        
        error_report = self.severity_error_analysis(
            best_models[best_model_name], X_test, y_test, severity_scores_test, class_names
        )
        
        # Save models and results
        self.save_severity_models(best_models, ensemble, tfidf_vectorizer, results)
        
        return best_models, ensemble, results
    
    def save_severity_models(self, models, ensemble, vectorizer, results):
        """Save all severity models and results"""
        print("Saving severity models and results...")
        
        os.makedirs('../models', exist_ok=True)
        
        # Save individual models
        for name, model in models.items():
            joblib.dump(model, f'../models/enhanced_severity_{name}_model.pkl')
        
        # Save ensemble
        joblib.dump(ensemble, '../models/enhanced_severity_ensemble_model.pkl')
        
        # Save vectorizer
        joblib.dump(vectorizer, '../models/enhanced_severity_tfidf_vectorizer.pkl')
        
        # Save results
        results_df = pd.DataFrame(results).T
        results_df.to_csv('../results/severity_model_comparison_results.csv')
        
        print("All severity models and results saved successfully!")

if __name__ == "__main__":
    # Initialize the enhanced severity predictor
    predictor = EnhancedSeverityPredictor()
    
    # Train with all enhancements
    best_models, ensemble, results = predictor.train_enhanced_severity_model(
        use_augmentation=True,
        balance_method='smote',      # Options: 'smote', 'random_oversample', 'class_weight', 'none'
        search_type='random',       # Options: 'grid', 'random'
        cv_folds=5
    )
    
    print("\nSeverity model training completed!")
    print("Results summary:")
    for model_name, metrics in results.items():
        print(f"{model_name}: CV F1 = {metrics['cv_mean']:.4f} ± {metrics['cv_std']:.4f}, "
              f"Test F1 = {metrics['test_f1']:.4f}, Accuracy = {metrics['test_accuracy']:.4f}")