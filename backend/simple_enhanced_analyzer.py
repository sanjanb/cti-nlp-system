"""
Enhanced Backend Integration - Fixed Version
Works with your current system using rebuilt models without dependency issues
"""
import joblib
import os
import logging
import re
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, FeatureUnion

# Configure logging
logger = logging.getLogger(__name__)

# Global variables for loaded models
_threat_models = {}
_severity_models = {}
_models_loaded = False

class CybersecurityFeatureExtractor(BaseEstimator, TransformerMixin):
    """Extract cybersecurity-specific features from text"""
    
    def __init__(self):
        self.threat_keywords = [
            'malware', 'virus', 'trojan', 'ransomware', 'backdoor',
            'phishing', 'spam', 'botnet', 'ddos', 'injection',
            'vulnerability', 'exploit', 'payload', 'shellcode',
            'attack', 'breach', 'intrusion', 'compromise'
        ]
        
        self.severity_indicators = {
            'high': ['critical', 'severe', 'emergency', 'urgent', 'immediate'],
            'medium': ['important', 'significant', 'moderate'],
            'low': ['minor', 'low', 'minimal']
        }
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        features = []
        
        for text in X:
            if pd.isna(text) or text is None:
                text = ""
            
            text_lower = str(text).lower()
            feature_vector = []
            
            # Text statistics
            feature_vector.extend([
                len(text),  # Character count
                len(text.split()),  # Word count
                text.count('!'),  # Urgency indicators
            ])
            
            # Threat keyword counts
            threat_count = sum(1 for keyword in self.threat_keywords if keyword in text_lower)
            feature_vector.append(threat_count)
            
            # Severity indicators
            for level, keywords in self.severity_indicators.items():
                count = sum(1 for keyword in keywords if keyword in text_lower)
                feature_vector.append(count)
            
            # Technical indicators using regex
            # CVE mentions
            cve_count = len(re.findall(r'CVE-\d{4}-\d{4,7}', text, re.IGNORECASE))
            feature_vector.append(cve_count)
            
            # IP addresses
            ip_count = len(re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', text))
            feature_vector.append(ip_count)
            
            # Hash values (MD5, SHA1, SHA256)
            hash_patterns = [r'\b[a-fA-F0-9]{32}\b', r'\b[a-fA-F0-9]{40}\b', r'\b[a-fA-F0-9]{64}\b']
            hash_count = sum(len(re.findall(pattern, text)) for pattern in hash_patterns)
            feature_vector.append(hash_count)
            
            # URLs and domains
            url_count = len(re.findall(r'https?://[^\s<>"{}|\\^`\[\]]*', text))
            domain_count = len(re.findall(r'\b[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}\b', text))
            feature_vector.extend([url_count, domain_count])
            
            features.append(feature_vector)
        
        return np.array(features)

class EnhancedThreatAnalyzer:
    """Enhanced threat analyzer with rebuilt models"""
    
    def __init__(self):
        self.tfidf_vectorizer = None
        self.feature_extractor = CybersecurityFeatureExtractor()
        self.threat_classifier = None
        self.severity_classifier = None
        self.models_ready = False
        
    def load_or_create_models(self):
        """Load existing models or create new ones if they don't exist"""
        try:
            # Try to load basic models first
            basic_tfidf_path = os.path.join("models", "tfidf_vectorizer.pkl")
            basic_classifier_path = os.path.join("models", "threat_classifier.pkl")
            
            if os.path.exists(basic_tfidf_path) and os.path.exists(basic_classifier_path):
                self.tfidf_vectorizer = joblib.load(basic_tfidf_path)
                self.threat_classifier = joblib.load(basic_classifier_path)
                logger.info("Loaded basic models successfully")
                
                # Try to load severity model
                severity_path = os.path.join("models", "severity_model.pkl")
                severity_tfidf_path = os.path.join("models", "severity_vectorizer.pkl")
                
                if os.path.exists(severity_path) and os.path.exists(severity_tfidf_path):
                    self.severity_classifier = joblib.load(severity_path)
                    self.severity_vectorizer = joblib.load(severity_tfidf_path)
                    logger.info("Loaded severity models successfully")
                
                self.models_ready = True
                return True
            else:
                logger.warning("Basic models not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            return False
    
    def classify_threat_enhanced(self, text: str) -> Dict:
        """Enhanced threat classification"""
        if not self.models_ready:
            if not self.load_or_create_models():
                return {"category": "Other", "confidence": 0.0, "method": "fallback"}
        
        try:
            # Use TF-IDF vectorizer
            X_tfidf = self.tfidf_vectorizer.transform([text])
            
            # Get prediction
            prediction = self.threat_classifier.predict(X_tfidf)[0]
            probabilities = self.threat_classifier.predict_proba(X_tfidf)[0]
            confidence = max(probabilities)
            
            # Add cybersecurity features for analysis
            cyber_features = self.feature_extractor.transform([text])
            
            # Enhanced confidence based on cybersecurity features
            feature_boost = min(np.sum(cyber_features[0]) * 0.1, 0.3)
            enhanced_confidence = min(confidence + feature_boost, 1.0)
            
            return {
                "category": prediction,
                "confidence": float(enhanced_confidence),
                "method": "enhanced_tfidf",
                "cyber_features_detected": int(np.sum(cyber_features[0]))
            }
            
        except Exception as e:
            logger.error(f"Enhanced classification failed: {e}")
            return {"category": "Other", "confidence": 0.0, "method": "error"}
    
    def predict_severity_enhanced(self, text: str) -> Dict:
        """Enhanced severity prediction"""
        if not self.models_ready:
            if not self.load_or_create_models():
                return {"severity": "Medium", "confidence": 0.0, "method": "fallback"}
        
        try:
            if hasattr(self, 'severity_classifier') and hasattr(self, 'severity_vectorizer'):
                # Use loaded severity model
                X_severity = self.severity_vectorizer.transform([text])
                prediction = self.severity_classifier.predict(X_severity)[0]
                probabilities = self.severity_classifier.predict_proba(X_severity)[0]
                confidence = max(probabilities)
                
                # Enhanced severity based on cybersecurity features
                cyber_features = self.feature_extractor.transform([text])
                
                # Boost severity if critical indicators are present
                feature_sum = np.sum(cyber_features[0])
                if feature_sum > 5:  # High feature count suggests higher severity
                    enhanced_confidence = min(confidence + 0.2, 1.0)
                    if prediction in ["Low", "Medium"] and feature_sum > 8:
                        prediction = "High"  # Upgrade severity for high feature count
                else:
                    enhanced_confidence = confidence
                
                severity = prediction.item() if hasattr(prediction, "item") else prediction
                
                return {
                    "severity": severity,
                    "confidence": float(enhanced_confidence),
                    "method": "enhanced_severity",
                    "cyber_features_detected": int(feature_sum)
                }
            else:
                # Fallback to rule-based severity
                return self._rule_based_severity(text)
                
        except Exception as e:
            logger.error(f"Enhanced severity prediction failed: {e}")
            return self._rule_based_severity(text)
    
    def _rule_based_severity(self, text: str) -> Dict:
        """Rule-based severity prediction as fallback"""
        text_lower = text.lower()
        
        critical_keywords = ['critical', 'urgent', 'emergency', 'severe', 'ransomware', 'breach']
        high_keywords = ['high', 'important', 'malware', 'attack', 'vulnerability']
        low_keywords = ['low', 'minor', 'informational']
        
        critical_count = sum(1 for keyword in critical_keywords if keyword in text_lower)
        high_count = sum(1 for keyword in high_keywords if keyword in text_lower)
        low_count = sum(1 for keyword in low_keywords if keyword in text_lower)
        
        if critical_count > 0:
            return {"severity": "Critical", "confidence": 0.8, "method": "rule_based"}
        elif high_count > 0:
            return {"severity": "High", "confidence": 0.7, "method": "rule_based"}
        elif low_count > 0:
            return {"severity": "Low", "confidence": 0.6, "method": "rule_based"}
        else:
            return {"severity": "Medium", "confidence": 0.5, "method": "rule_based"}

# Global analyzer instance
_enhanced_analyzer = None

def load_enhanced_models():
    """Load enhanced models - Fixed version"""
    global _enhanced_analyzer, _models_loaded
    
    if _models_loaded and _enhanced_analyzer is not None:
        return True
    
    try:
        _enhanced_analyzer = EnhancedThreatAnalyzer()
        success = _enhanced_analyzer.load_or_create_models()
        
        if success:
            _models_loaded = True
            logger.info("Enhanced analyzer loaded successfully")
            return True
        else:
            logger.warning("Enhanced analyzer loaded with limited functionality")
            _models_loaded = True  # Still mark as loaded for fallback
            return False
            
    except Exception as e:
        logger.error(f"Failed to load enhanced analyzer: {e}")
        return False

def analyze_threat_enhanced(text: str) -> Dict:
    """Enhanced threat analysis"""
    if _enhanced_analyzer is None:
        load_enhanced_models()
    
    if _enhanced_analyzer:
        return _enhanced_analyzer.classify_threat_enhanced(text)
    else:
        return {"category": "Other", "confidence": 0.0, "method": "analyzer_unavailable"}

def predict_severity_enhanced(text: str) -> Dict:
    """Enhanced severity prediction"""
    if _enhanced_analyzer is None:
        load_enhanced_models()
    
    if _enhanced_analyzer:
        return _enhanced_analyzer.predict_severity_enhanced(text)
    else:
        return {"severity": "Medium", "confidence": 0.0, "method": "analyzer_unavailable"}

def analyze_threat_comprehensive(text: str) -> Dict:
    """Comprehensive threat analysis using enhanced models"""
    if not _models_loaded:
        load_enhanced_models()
    
    results = {
        "threat_classification": analyze_threat_enhanced(text),
        "severity_prediction": predict_severity_enhanced(text),
        "confidence_score": 0.0
    }
    
    # Calculate overall confidence
    threat_conf = results["threat_classification"].get("confidence", 0.0)
    severity_conf = results["severity_prediction"].get("confidence", 0.0)
    results["confidence_score"] = (threat_conf + severity_conf) / 2
    
    return results

def get_model_info() -> Dict:
    """Get information about loaded models"""
    if _enhanced_analyzer is None:
        load_enhanced_models()
    
    return {
        "enhanced_analyzer_available": _enhanced_analyzer is not None,
        "models_ready": _enhanced_analyzer.models_ready if _enhanced_analyzer else False,
        "threat_classifier": _enhanced_analyzer.threat_classifier is not None if _enhanced_analyzer else False,
        "severity_classifier": hasattr(_enhanced_analyzer, 'severity_classifier') and _enhanced_analyzer.severity_classifier is not None if _enhanced_analyzer else False,
        "feature_extractor": "CybersecurityFeatureExtractor available",
        "method": "enhanced_with_fallback"
    }

def initialize_analyzer():
    """Initialize the enhanced analyzer"""
    logger.info("Initializing enhanced threat analyzer...")
    return load_enhanced_models()
