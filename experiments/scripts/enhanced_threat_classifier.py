"""
Enhanced Threat Classifier with Multiple Improvements
- Data Augmentation (back-translation, paraphrasing)
- Class Imbalance Handling (SMOTE, class weights)
- Advanced Model Ensembling
- Feature Engineering (domain-specific features)
- Hyperparameter Optimization (Grid/Random Search)
- Stratified Cross-Validation
- Error Analysis
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV, RandomizedSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import SMOTE, RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler
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

class EnhancedThreatClassifier:
    def __init__(self, data_path="../data/Cybersecurity_Dataset.csv"):
        self.data_path = data_path
        self.models = {}
        self.vectorizers = {}
        self.label_encoder = None
        self.threat_keywords = [
            'malware', 'virus', 'trojan', 'ransomware', 'phishing', 'ddos', 'botnet',
            'exploit', 'vulnerability', 'breach', 'attack', 'hack', 'intrusion',
            'backdoor', 'worm', 'spyware', 'adware', 'rootkit', 'keylogger',
            'cve', 'zero-day', 'apt', 'c2', 'command', 'control'
        ]
        
    def load_and_prepare_data(self):
        """Load and prepare the dataset with enhanced preprocessing"""
        print("Loading and preparing data...")
        
        # Load data
        df = pd.read_csv(self.data_path)
        df = df.rename(columns=lambda x: x.strip())
        
        text_col = "Cleaned Threat Description"
        label_col = "Threat Category"
        
        # Drop missing values
        df = df.dropna(subset=[text_col, label_col])
        
        print(f"Dataset shape: {df.shape}")
        print(f"Class distribution:\n{df[label_col].value_counts()}")
        
        return df[text_col], df[label_col]
    
    def augment_data(self, X, y, augment_factor=2):
        """Data augmentation using simple techniques"""
        print("Performing data augmentation...")
        
        # Find minority classes
        class_counts = Counter(y)
        min_count = min(class_counts.values())
        max_count = max(class_counts.values())
        
        X_augmented = list(X)
        y_augmented = list(y)
        
        # Simple augmentation: synonym replacement and paraphrasing
        for label in class_counts:
            if class_counts[label] < max_count * 0.7:  # Augment minority classes
                class_samples = [x for x, l in zip(X, y) if l == label]
                
                # Simple text variations
                for sample in class_samples[:min(len(class_samples), augment_factor)]:
                    # Add variations
                    variations = self._create_text_variations(sample)
                    X_augmented.extend(variations)
                    y_augmented.extend([label] * len(variations))
        
        print(f"Original samples: {len(X)}")
        print(f"Augmented samples: {len(X_augmented)}")
        
        return np.array(X_augmented), np.array(y_augmented)
    
    def _create_text_variations(self, text):
        """Create simple text variations"""
        variations = []
        
        # Case variations
        variations.append(text.lower())
        variations.append(text.upper())
        
        # Synonym replacement (simple)
        synonyms = {
            'attack': 'assault',
            'malware': 'malicious software',
            'virus': 'malicious program',
            'hack': 'breach',
            'exploit': 'abuse'
        }
        
        varied_text = text.lower()
        for word, synonym in synonyms.items():
            if word in varied_text:
                variations.append(varied_text.replace(word, synonym))
        
        return variations[:2]  # Limit variations
    
    def extract_domain_features(self, texts):
        """Extract domain-specific features"""
        print("Extracting domain-specific features...")
        
        features = []
        for text in texts:
            text_lower = text.lower()
            feature_dict = {}
            
            # Threat keyword counts
            for keyword in self.threat_keywords:
                feature_dict[f'keyword_{keyword}'] = text_lower.count(keyword)
            
            # CVE mentions
            cve_pattern = r'cve-\d{4}-\d{4,7}'
            feature_dict['cve_count'] = len(re.findall(cve_pattern, text_lower))
            
            # Text statistics
            feature_dict['text_length'] = len(text)
            feature_dict['word_count'] = len(text.split())
            feature_dict['exclamation_count'] = text.count('!')
            feature_dict['question_count'] = text.count('?')
            feature_dict['uppercase_ratio'] = sum(1 for c in text if c.isupper()) / len(text) if text else 0
            
            # Threat indicators
            feature_dict['has_ip'] = 1 if re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', text) else 0
            feature_dict['has_url'] = 1 if re.search(r'https?://', text_lower) else 0
            feature_dict['has_email'] = 1 if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text) else 0
            
            features.append(feature_dict)
        
        return pd.DataFrame(features).fillna(0)
    
    def handle_class_imbalance(self, X, y, method='smote'):
        """Handle class imbalance using various techniques"""
        print(f"Handling class imbalance using {method}...")
        
        if method == 'smote':
            sampler = SMOTE(random_state=42)
        elif method == 'random_oversample':
            sampler = RandomOverSampler(random_state=42)
        elif method == 'smote_tomek':
            sampler = SMOTETomek(random_state=42)
        else:
            return X, y
        
        X_resampled, y_resampled = sampler.fit_resample(X, y)
        
        print(f"Original shape: {X.shape}")
        print(f"Resampled shape: {X_resampled.shape}")
        print(f"New class distribution: {Counter(y_resampled)}")
        
        return X_resampled, y_resampled
    
    def create_ensemble_models(self):
        """Create ensemble of different models"""
        print("Creating ensemble models...")
        
        models = {
            'logistic': LogisticRegression(max_iter=1000, random_state=42),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'svm': SVC(probability=True, random_state=42),
            'xgboost': XGBClassifier(random_state=42, eval_metric='logloss')
        }
        
        return models
    
    def hyperparameter_optimization(self, model, X, y, search_type='grid'):
        """Perform hyperparameter optimization"""
        print(f"Performing {search_type} search for hyperparameter optimization...")
        
        param_grids = {
            'logistic': {
                'C': [0.1, 1, 10, 100],
                'solver': ['liblinear', 'lbfgs'],
                'penalty': ['l1', 'l2']
            },
            'random_forest': {
                'n_estimators': [50, 100, 200],
                'max_depth': [None, 10, 20],
                'min_samples_split': [2, 5, 10]
            },
            'svm': {
                'C': [0.1, 1, 10],
                'kernel': ['linear', 'rbf'],
                'gamma': ['scale', 'auto']
            },
            'xgboost': {
                'n_estimators': [50, 100, 200],
                'max_depth': [3, 6, 9],
                'learning_rate': [0.1, 0.2, 0.3]
            }
        }
        
        model_name = type(model).__name__.lower()
        if 'logistic' in str(model):
            model_name = 'logistic'
        elif 'forest' in str(model):
            model_name = 'random_forest'
        elif 'svc' in str(model):
            model_name = 'svm'
        elif 'xgb' in str(model):
            model_name = 'xgboost'
        
        param_grid = param_grids.get(model_name, {})
        
        if search_type == 'grid':
            search = GridSearchCV(
                model, param_grid, cv=3, scoring='f1_weighted',
                n_jobs=-1, verbose=1
            )
        else:  # random search
            search = RandomizedSearchCV(
                model, param_grid, cv=3, scoring='f1_weighted',
                n_jobs=-1, verbose=1, n_iter=20, random_state=42
            )
        
        search.fit(X, y)
        
        print(f"Best parameters: {search.best_params_}")
        print(f"Best cross-validation score: {search.best_score_:.4f}")
        
        return search.best_estimator_
    
    def stratified_cross_validation(self, model, X, y, cv_folds=5):
        """Perform stratified cross-validation"""
        print(f"Performing {cv_folds}-fold stratified cross-validation...")
        
        skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
        cv_scores = []
        
        for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
            X_train_fold, X_val_fold = X[train_idx], X[val_idx]
            y_train_fold, y_val_fold = y[train_idx], y[val_idx]
            
            model.fit(X_train_fold, y_train_fold)
            y_pred_fold = model.predict(X_val_fold)
            
            f1 = f1_score(y_val_fold, y_pred_fold, average='weighted')
            cv_scores.append(f1)
            
            print(f"Fold {fold + 1}: F1 = {f1:.4f}")
        
        mean_f1 = np.mean(cv_scores)
        std_f1 = np.std(cv_scores)
        
        print(f"Cross-validation F1: {mean_f1:.4f} ± {std_f1:.4f}")
        
        return cv_scores
    
    def error_analysis(self, model, X_test, y_test, class_names):
        """Perform detailed error analysis"""
        print("Performing error analysis...")
        
        y_pred = model.predict(X_test)
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=class_names, yticklabels=class_names)
        plt.title('Confusion Matrix')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.tight_layout()
        plt.savefig('../results/confusion_matrix.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Classification report
        report = classification_report(y_test, y_pred, target_names=class_names, output_dict=True)
        
        # Identify most confused classes
        misclassified_indices = np.where(y_test != y_pred)[0]
        
        print(f"Total misclassified samples: {len(misclassified_indices)}")
        
        # Show some misclassified examples
        if hasattr(X_test, 'iloc'):
            for i in misclassified_indices[:5]:
                print(f"\nMisclassified example {i}:")
                print(f"Text: {X_test.iloc[i][:100]}...")
                print(f"True label: {y_test.iloc[i]}")
                print(f"Predicted label: {y_pred[i]}")
        
        return report
    
    def train_enhanced_model(self, use_augmentation=True, balance_method='smote', 
                           search_type='grid', cv_folds=5):
        """Train the enhanced model with all improvements"""
        print("Starting enhanced model training...")
        
        # Create results directory
        os.makedirs('../results', exist_ok=True)
        
        # Load data
        X, y = self.load_and_prepare_data()
        
        # Data augmentation
        if use_augmentation:
            X, y = self.augment_data(X, y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Feature extraction
        # 1. TF-IDF features
        tfidf_vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
        X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
        X_test_tfidf = tfidf_vectorizer.transform(X_test)
        
        # 2. Domain-specific features
        domain_features_train = self.extract_domain_features(X_train)
        domain_features_test = self.extract_domain_features(X_test)
        
        # Combine features
        from scipy.sparse import hstack
        X_train_combined = hstack([X_train_tfidf, domain_features_train.values])
        X_test_combined = hstack([X_test_tfidf, domain_features_test.values])
        
        # Handle class imbalance
        if balance_method != 'none':
            X_train_balanced, y_train_balanced = self.handle_class_imbalance(
                X_train_combined, y_train, balance_method
            )
        else:
            X_train_balanced, y_train_balanced = X_train_combined, y_train
        
        # Create models
        models = self.create_ensemble_models()
        
        # Calculate class weights for models that support it
        class_weights = compute_class_weight(
            'balanced', classes=np.unique(y_train), y=y_train
        )
        class_weight_dict = dict(zip(np.unique(y_train), class_weights))
        
        # Train and optimize models
        best_models = {}
        results = {}
        
        for name, model in models.items():
            print(f"\nTraining {name}...")
            
            # Set class weights if supported
            if hasattr(model, 'class_weight') and balance_method == 'class_weight':
                model.set_params(class_weight='balanced')
            
            # Hyperparameter optimization
            try:
                optimized_model = self.hyperparameter_optimization(
                    model, X_train_balanced, y_train_balanced, search_type
                )
                best_models[name] = optimized_model
            except Exception as e:
                print(f"Hyperparameter optimization failed for {name}: {e}")
                model.fit(X_train_balanced, y_train_balanced)
                best_models[name] = model
            
            # Cross-validation
            cv_scores = self.stratified_cross_validation(
                best_models[name], X_train_balanced, y_train_balanced, cv_folds
            )
            
            # Test evaluation
            y_pred = best_models[name].predict(X_test_combined)
            test_f1 = f1_score(y_test, y_pred, average='weighted')
            
            results[name] = {
                'cv_mean': np.mean(cv_scores),
                'cv_std': np.std(cv_scores),
                'test_f1': test_f1
            }
            
            print(f"{name} - Test F1: {test_f1:.4f}")
        
        # Create ensemble
        print("\nCreating ensemble model...")
        ensemble_models = [(name, model) for name, model in best_models.items()]
        ensemble = VotingClassifier(estimators=ensemble_models, voting='soft')
        ensemble.fit(X_train_balanced, y_train_balanced)
        
        # Evaluate ensemble
        y_pred_ensemble = ensemble.predict(X_test_combined)
        ensemble_f1 = f1_score(y_test, y_pred_ensemble, average='weighted')
        
        print(f"Ensemble Test F1: {ensemble_f1:.4f}")
        
        # Error analysis
        class_names = np.unique(y)
        best_model_name = max(results, key=lambda x: results[x]['test_f1'])
        print(f"\nPerforming error analysis on best model: {best_model_name}")
        
        error_report = self.error_analysis(
            best_models[best_model_name], X_test_combined, y_test, class_names
        )
        
        # Save models and results
        self.save_models(best_models, ensemble, tfidf_vectorizer, results)
        
        return best_models, ensemble, results
    
    def save_models(self, models, ensemble, vectorizer, results):
        """Save all models and results"""
        print("Saving models and results...")
        
        os.makedirs('../models', exist_ok=True)
        
        # Save individual models
        for name, model in models.items():
            joblib.dump(model, f'../models/enhanced_{name}_model.pkl')
        
        # Save ensemble
        joblib.dump(ensemble, '../models/enhanced_ensemble_model.pkl')
        
        # Save vectorizer
        joblib.dump(vectorizer, '../models/enhanced_tfidf_vectorizer.pkl')
        
        # Save results
        results_df = pd.DataFrame(results).T
        results_df.to_csv('../results/model_comparison_results.csv')
        
        print("All models and results saved successfully!")

if __name__ == "__main__":
    # Initialize the enhanced classifier
    classifier = EnhancedThreatClassifier()
    
    # Train with all enhancements
    best_models, ensemble, results = classifier.train_enhanced_model(
        use_augmentation=True,
        balance_method='smote',  # Options: 'smote', 'random_oversample', 'class_weight', 'none'
        search_type='random',   # Options: 'grid', 'random'
        cv_folds=5
    )
    
    print("\nTraining completed!")
    print("Results summary:")
    for model_name, metrics in results.items():
        print(f"{model_name}: CV F1 = {metrics['cv_mean']:.4f} ± {metrics['cv_std']:.4f}, "
              f"Test F1 = {metrics['test_f1']:.4f}")