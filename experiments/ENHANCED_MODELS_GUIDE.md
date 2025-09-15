# Enhanced Model Training - Complete Setup

## All Enhanced Models Created!

You now have three enhanced model training scripts in the `experiments/scripts/` folder:

### 1. **Enhanced Threat Classifier** (`enhanced_threat_classifier.py`)

- **Data Augmentation**: Text variations, minority class balancing
- **Class Imbalance**: SMOTE, Random Oversampling, Class Weights
- **Models**: Logistic Regression, Random Forest, SVM, XGBoost + Ensemble
- **Features**: TF-IDF + Domain-specific (threat keywords, CVEs, URLs)
- **Optimization**: Grid/Random Search with cross-validation

### 2. **Enhanced Severity Predictor** (`enhanced_severity_predictor.py`)

- **Severity-Aware Augmentation**: Context-specific text variations
- **Advanced Features**: Severity keywords, urgency indicators, impact scores
- **Models**: Random Forest, Gradient Boosting, XGBoost, SVM + Ensemble
- **Evaluation**: Severity-specific confusion matrix and feature importance
- **Error Analysis**: Shows misclassified examples with severity context

### 3. **Enhanced NER Trainer** (`enhanced_ner_trainer.py`)

- **Entity-Aware Augmentation**: Context prefixes, entity substitution
- **Multiple Transformers**: DistilBERT, BERT, RoBERTa, BERT-NER
- **Hyperparameter Optimization**: Learning rate, batch size, epochs
- **Entity-Level Analysis**: F1-score by entity type, error visualization
- **Advanced Evaluation**: Comprehensive error analysis with examples

## **Expected Improvements**

### Accuracy Increases:

- **Threat Classification**: 10-20% improvement (from ~0.27 to ~0.35-0.45)
- **Severity Prediction**: 15-25% improvement (from ~0.40 to ~0.50-0.65)
- **NER**: 5-15% improvement (from ~0.82 to ~0.85-0.95)

### F1-Score Improvements:

- **Better minority class performance** through SMOTE and class weights
- **More balanced precision/recall** through stratified cross-validation
- **Entity-level improvements** for rare entities in NER

## **Quick Start Guide**

### Run All Enhanced Models:

```bash
cd experiments

# 1. Enhanced Threat Classification
python scripts/enhanced_threat_classifier.py

# 2. Enhanced Severity Prediction
python scripts/enhanced_severity_predictor.py

# 3. Enhanced NER Training
python scripts/enhanced_ner_trainer.py
```

### Configuration Options:

Edit the main functions in each script to try different settings:

```python
# Threat Classifier
classifier.train_enhanced_model(
    use_augmentation=True,          # Enable data augmentation
    balance_method='smote',         # 'smote', 'random_oversample', 'class_weight'
    search_type='random',           # 'grid' or 'random' hyperparameter search
    cv_folds=5                      # Cross-validation folds
)

# Severity Predictor
predictor.train_enhanced_severity_model(
    use_augmentation=True,
    balance_method='smote',
    search_type='random',
    cv_folds=5
)

# NER Trainer
ner_trainer.train_enhanced_ner_ensemble(
    use_augmentation=True,
    optimization_type='random'      # 'grid' or 'random'
)
```

## **Output Structure**

After running, you'll have:

```
experiments/
├── models/                          # Enhanced trained models
│   ├── enhanced_threat_*_model.pkl
│   ├── enhanced_severity_*_model.pkl
│   ├── enhanced_ner_*/ (transformer models)
│   └── enhanced_*_ensemble_model.pkl
├── results/                         # Analysis and visualizations
│   ├── model_comparison_results.csv
│   ├── confusion_matrix.png
│   ├── severity_analysis.png
│   ├── ner_*_analysis.png
│   └── feature_importance.png
└── scripts/                         # Enhanced training scripts
```

## **Iteration Strategy**

1. **Start with Random Search** (faster) to get baseline improvements
2. **Switch to Grid Search** for final optimization if needed
3. **Compare results** with your original models
4. **Identify best techniques** for each model type
5. **Integrate successful methods** back into main project

## **Advanced Techniques Included**

### Data Augmentation:

- **Text variations** (synonym replacement, context addition)
- **Minority class balancing** (SMOTE, oversampling)
- **Entity-aware augmentation** (for NER)

### Feature Engineering:

- **Domain-specific features** (threat keywords, CVEs)
- **Contextual features** (URLs, IPs, emails)
- **Severity indicators** (urgency words, impact terms)

### Model Optimization:

- **Hyperparameter search** (Grid/Random with CV)
- **Ensemble methods** (Voting classifiers)
- **Class balancing** (weights, SMOTE, oversampling)

### Evaluation & Analysis:

- **Stratified cross-validation**
- **Confusion matrices with visualization**
- **Error analysis with examples**
- **Feature importance plots**
- **Entity-level performance metrics**

## **Ready to Run!**

All dependencies are installed and scripts are ready. Start with one model and compare results with your current performance!

**Expected runtime**: 10-30 minutes per model depending on data size and search type.
