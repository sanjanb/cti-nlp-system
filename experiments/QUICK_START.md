# Enhanced Threat Classifier - Quick Start Guide

## Setup

1. Navigate to the experiments folder:

   ```bash
   cd experiments
   ```

2. Install requirements:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the enhanced classifier:
   ```bash
   python scripts/enhanced_threat_classifier.py
   ```

## What This Script Does

### 1. Data Augmentation

- Creates text variations using synonym replacement
- Augments minority classes to balance the dataset
- Generates 2-3 variations per minority class sample

### 2. Class Imbalance Handling

- **SMOTE**: Synthetic Minority Oversampling Technique
- **Random Oversampling**: Duplicate minority samples
- **Class Weights**: Weight classes inversely to their frequency
- **SMOTETomek**: SMOTE + Tomek link removal

### 3. Advanced Feature Engineering

- **TF-IDF**: Traditional text features with bi-grams
- **Domain Features**: Threat keywords, CVE mentions, text statistics
- **Contextual Features**: IP addresses, URLs, email patterns
- **Combined Features**: Stacks all feature types together

### 4. Model Ensemble

- **Logistic Regression**: Fast, interpretable baseline
- **Random Forest**: Handles feature interactions
- **SVM**: Good for high-dimensional data
- **XGBoost**: Gradient boosting for complex patterns
- **Voting Ensemble**: Combines all models

### 5. Hyperparameter Optimization

- **Grid Search**: Exhaustive search over parameter grid
- **Random Search**: Faster, samples random combinations
- Cross-validation scoring using F1-weighted

### 6. Evaluation

- **Stratified K-Fold**: Maintains class distribution in folds
- **Confusion Matrix**: Visual error analysis
- **Classification Report**: Per-class metrics
- **Error Analysis**: Shows misclassified examples

## Expected Improvements

- **Accuracy**: Should increase by 10-20%
- **F1-Score**: Better balance of precision/recall
- **Minority Classes**: Much better performance on rare threats
- **Generalization**: More robust to new data

## Output Files

- `../models/enhanced_*_model.pkl`: Individual optimized models
- `../models/enhanced_ensemble_model.pkl`: Final ensemble
- `../models/enhanced_tfidf_vectorizer.pkl`: Feature extractor
- `../results/model_comparison_results.csv`: Performance comparison
- `../results/confusion_matrix.png`: Visual error analysis

## Configuration Options

Edit the main function to try different settings:

```python
classifier.train_enhanced_model(
    use_augmentation=True,          # Enable/disable data augmentation
    balance_method='smote',         # 'smote', 'random_oversample', 'class_weight'
    search_type='random',           # 'grid' or 'random' search
    cv_folds=5                      # Number of cross-validation folds
)
```

## Next Steps

1. Run the script and compare results to your original model
2. Try different `balance_method` options
3. Experiment with `search_type='grid'` for more thorough optimization
4. Analyze the error analysis output to identify remaining issues
5. If results are good, integrate best practices back into main project
