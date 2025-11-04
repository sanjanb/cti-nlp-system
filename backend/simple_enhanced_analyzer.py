"""
Simple Enhanced Backend Integration
Works with your current system - improved models without complex dependencies
"""
import joblib
import os
import sys
import re
import logging
from typing import Dict, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Global variables for loaded models
_threat_classifier = None
_severity_predictor = None
_entity_extractor = None
_models_loaded = False

class SimpleThreatAnalyzer:
    """Simple but enhanced threat analyzer"""
    
"""
Simple Enhanced Backend Integration
Works with your current system - using improved models from pickle files directly
"""
import joblib
import os
import logging
from typing import Dict, List, Optional
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

# Global variables for loaded models
_threat_models = {}
_severity_models = {}
_models_loaded = False

def load_enhanced_models():
    """Load enhanced models from pickle files"""
    global _threat_models, _severity_models, _models_loaded
    
    if _models_loaded:
        return True
    
    try:
        model_dir = "models"
        
        # Load threat classification models
        threat_files = [
            "improved_threat_classifier.pkl",
            "improved_tfidf_vectorizer.pkl",
            "enhanced_ensemble_model.pkl",
            "enhanced_tfidf_vectorizer.pkl"
        ]
        
        for filename in threat_files:
            filepath = os.path.join(model_dir, filename)
            if os.path.exists(filepath):
                try:
                    _threat_models[filename.replace('.pkl', '')] = joblib.load(filepath)
                    logger.info(f"Loaded {filename}")
                except Exception as e:
                    logger.warning(f"Failed to load {filename}: {e}")
        
        # Load severity prediction models
        severity_files = [
            "improved_severity_model.pkl",
            "improved_severity_tfidf.pkl",
            "improved_severity_features.pkl"
        ]
        
        for filename in severity_files:
            filepath = os.path.join(model_dir, filename)
            if os.path.exists(filepath):
                try:
                    _severity_models[filename.replace('.pkl', '')] = joblib.load(filepath)
                    logger.info(f"Loaded {filename}")
                except Exception as e:
                    logger.warning(f"Failed to load {filename}: {e}")
        
        _models_loaded = True
        logger.info("Enhanced models loaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to load enhanced models: {e}")
        return False

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

def analyze_threat_enhanced(text: str) -> Dict:
    """Enhanced threat classification"""
    try:
        if "improved_threat_classifier" in _threat_models and "improved_tfidf_vectorizer" in _threat_models:
            vectorizer = _threat_models["improved_tfidf_vectorizer"]
            classifier = _threat_models["improved_threat_classifier"]
            
            X = vectorizer.transform([text])
            prediction = classifier.predict(X)[0]
            probabilities = classifier.predict_proba(X)[0]
            confidence = max(probabilities)
            
            return {
                "category": prediction,
                "confidence": float(confidence),
                "model_type": "enhanced"
            }
        
        # Fallback to ensemble model
        elif "enhanced_ensemble_model" in _threat_models and "enhanced_tfidf_vectorizer" in _threat_models:
            vectorizer = _threat_models["enhanced_tfidf_vectorizer"]
            classifier = _threat_models["enhanced_ensemble_model"]
            
            X = vectorizer.transform([text])
            prediction = classifier.predict(X)[0]
            probabilities = classifier.predict_proba(X)[0]
            confidence = max(probabilities)
            
            return {
                "category": prediction,
                "confidence": float(confidence),
                "model_type": "ensemble"
            }
        
        else:
            return {
                "category": "Other",
                "confidence": 0.0,
                "model_type": "fallback",
                "error": "Enhanced models not available"
            }
            
    except Exception as e:
        logger.error(f"Enhanced threat analysis failed: {e}")
        return {
            "category": "Other",
            "confidence": 0.0,
            "model_type": "fallback",
            "error": str(e)
        }

def predict_severity_enhanced(text: str) -> Dict:
    """Enhanced severity prediction"""
    try:
        if "improved_severity_model" in _severity_models and "improved_severity_tfidf" in _severity_models:
            vectorizer = _severity_models["improved_severity_tfidf"]
            classifier = _severity_models["improved_severity_model"]
            
            X = vectorizer.transform([text])
            prediction = classifier.predict(X)[0]
            probabilities = classifier.predict_proba(X)[0]
            confidence = max(probabilities)
            
            return {
                "severity": prediction,
                "confidence": float(confidence),
                "model_type": "enhanced"
            }
        else:
            return {
                "severity": "Medium",
                "confidence": 0.0,
                "model_type": "fallback",
                "error": "Enhanced severity models not available"
            }
            
    except Exception as e:
        logger.error(f"Enhanced severity prediction failed: {e}")
        return {
            "severity": "Medium",
            "confidence": 0.0,
            "model_type": "fallback",
            "error": str(e)
        }

def get_model_info() -> Dict:
    """Get information about loaded models"""
    return {
        "models_loaded": _models_loaded,
        "threat_models": list(_threat_models.keys()),
        "severity_models": list(_severity_models.keys()),
        "total_models": len(_threat_models) + len(_severity_models)
    }

def initialize_analyzer():
    """Initialize the analyzer by loading models"""
    return load_enhanced_models()

# Simplified class for backward compatibility
class SimpleThreatAnalyzer:
    """Simple but enhanced threat analyzer"""
    
    def __init__(self, model_dir="models"):
        self.model_dir = model_dir
        self.models_loaded = load_enhanced_models()
        self.severity_predictor = None
        self.entity_extractor = None
        
        # Fallback models
        self.fallback_classifier = None
        self.fallback_tfidf = None
        self.fallback_severity = None
        self.fallback_severity_tfidf = None
        
        self.load_models()
    
    def load_models(self):
        """Load improved models with fallback to original models"""
        print("Loading threat analysis models...")
        
        # Try to load improved models
        if ImprovedThreatClassifier:
            try:
                self.classifier = ImprovedThreatClassifier()
                if not self.classifier.load_model(self.model_dir):
                    self.classifier = None
            except:
                self.classifier = None
        
        if ImprovedSeverityPredictor:
            try:
                self.severity_predictor = ImprovedSeverityPredictor()
                if not self.severity_predictor.load_model(self.model_dir):
                    self.severity_predictor = None
            except:
                self.severity_predictor = None
        
        if SimpleEntityExtractor:
            try:
                self.entity_extractor = SimpleEntityExtractor()
            except:
                self.entity_extractor = None
        
        # Load fallback models
        self._load_fallback_models()
        
        print("✅ Threat analysis models loaded")
    
    def _load_fallback_models(self):
        """Load original models as fallback"""
        try:
            # Original TF-IDF classifier
            vectorizer_path = os.path.join(self.model_dir, "tfidf_vectorizer.pkl")
            classifier_path = os.path.join(self.model_dir, "threat_classifier.pkl")
            
            if os.path.exists(vectorizer_path) and os.path.exists(classifier_path):
                self.fallback_tfidf = joblib.load(vectorizer_path)
                self.fallback_classifier = joblib.load(classifier_path)
            
            # Original severity model
            severity_model_path = os.path.join(self.model_dir, "severity_model.pkl")
            severity_vectorizer_path = os.path.join(self.model_dir, "severity_vectorizer.pkl")
            
            if os.path.exists(severity_model_path) and os.path.exists(severity_vectorizer_path):
                self.fallback_severity_tfidf = joblib.load(severity_vectorizer_path)
                self.fallback_severity = joblib.load(severity_model_path)
                
        except Exception as e:
            print(f"Warning: Failed to load some fallback models: {e}")
    
    def classify_threat(self, text: str) -> Dict:
        """Classify threat using best available model"""
        try:
            # Try improved model first
            if self.classifier:
                result = self.classifier.predict(text, return_details=True)
                return {
                    'prediction': result['prediction'],
                    'confidence': result['confidence'],
                    'probabilities': result['probabilities'],
                    'model_type': 'improved_ensemble',
                    'individual_predictions': result['individual_predictions'],
                    'success': True
                }
            
            # Fallback to original model
            elif self.fallback_classifier and self.fallback_tfidf:
                X = self.fallback_tfidf.transform([text])
                prediction = self.fallback_classifier.predict(X)[0]
                confidence = max(self.fallback_classifier.predict_proba(X)[0])
                
                return {
                    'prediction': prediction,
                    'confidence': confidence,
                    'model_type': 'original_tfidf',
                    'success': True
                }
            
            else:
                return {
                    'prediction': 'unknown',
                    'confidence': 0.0,
                    'model_type': 'none',
                    'error': 'No classifier available',
                    'success': False
                }
                
        except Exception as e:
            return {
                'prediction': 'error',
                'confidence': 0.0,
                'model_type': 'error',
                'error': str(e),
                'success': False
            }
    
    def predict_severity(self, text: str) -> Dict:
        """Predict severity using best available model"""
        try:
            # Try improved model first
            if self.severity_predictor:
                result = self.severity_predictor.predict(text, return_details=True)
                return {
                    'severity': result['severity'],
                    'confidence': result['confidence'],
                    'probabilities': result['probabilities'],
                    'threat_indicators': result['threat_indicators'],
                    'cve_count': result['cve_count'],
                    'ip_count': result['ip_count'],
                    'hash_count': result['hash_count'],
                    'model_type': 'improved_random_forest',
                    'success': True
                }
            
            # Fallback to original model
            elif self.fallback_severity and self.fallback_severity_tfidf:
                X = self.fallback_severity_tfidf.transform([text])
                prediction = self.fallback_severity.predict(X)[0]
                confidence = max(self.fallback_severity.predict_proba(X)[0])
                
                return {
                    'severity': prediction,
                    'confidence': confidence,
                    'model_type': 'original_random_forest',
                    'success': True
                }
            
            else:
                return {
                    'severity': 'unknown',
                    'confidence': 0.0,
                    'model_type': 'none',
                    'error': 'No severity predictor available',
                    'success': False
                }
                
        except Exception as e:
            return {
                'severity': 'error',
                'confidence': 0.0,
                'model_type': 'error',
                'error': str(e),
                'success': False
            }
    
    def extract_entities(self, text: str) -> Dict:
        """Extract entities using enhanced extractor"""
        try:
            if self.entity_extractor:
                entities = self.entity_extractor.extract_entities(text)
                risk_score = self.entity_extractor.calculate_risk_score(entities)
                
                return {
                    'entities': entities,
                    'risk_score': risk_score,
                    'model_type': 'enhanced_regex',
                    'success': True
                }
            
            else:
                # Simple fallback extraction
                entities = self._simple_entity_extraction(text)
                
                return {
                    'entities': entities,
                    'model_type': 'simple_regex',
                    'success': True
                }
                
        except Exception as e:
            return {
                'entities': {},
                'model_type': 'error',
                'error': str(e),
                'success': False
            }
    
    def _simple_entity_extraction(self, text):
        """Simple entity extraction fallback"""
        entities = {}
        
        # IP addresses
        ips = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', text)
        if ips:
            entities['IP'] = list(set(ips))
        
        # CVEs
        cves = re.findall(r'CVE-\d{4}-\d{4,7}', text, re.IGNORECASE)
        if cves:
            entities['CVE'] = list(set(cves))
        
        # Hashes (MD5, SHA1, SHA256)
        hashes = []
        for pattern in [r'\b[a-fA-F0-9]{32}\b', r'\b[a-fA-F0-9]{40}\b', r'\b[a-fA-F0-9]{64}\b']:
            hashes.extend(re.findall(pattern, text))
        if hashes:
            entities['HASH'] = list(set(hashes))
        
        return entities
    
    def comprehensive_analysis(self, text: str) -> Dict:
        """Perform comprehensive threat analysis"""
        # Get individual analyses
        classification = self.classify_threat(text)
        severity = self.predict_severity(text)
        entities = self.extract_entities(text)
        
        # Calculate overall risk score
        risk_components = []
        
        if classification['success'] and classification['confidence'] > 0.5:
            risk_components.append(classification['confidence'] * 30)
        
        if severity['success']:
            severity_weights = {'Critical': 40, 'High': 30, 'Medium': 20, 'Low': 10}
            risk_components.append(severity_weights.get(severity['severity'], 0))
        
        if entities['success'] and 'risk_score' in entities:
            risk_components.append(min(entities['risk_score'], 30))
        
        overall_risk = min(100, sum(risk_components)) if risk_components else 0
        
        # Generate recommendations
        recommendations = []
        
        if overall_risk >= 70:
            recommendations.extend([
                "CRITICAL: Immediate security response required",
                "Escalate to incident response team",
                "Consider system isolation"
            ])
        elif overall_risk >= 40:
            recommendations.extend([
                "HIGH: Priority security assessment needed",
                "Monitor for related indicators",
                "Update security controls"
            ])
        elif overall_risk >= 20:
            recommendations.append("MEDIUM: Include in security review")
        else:
            recommendations.append("LOW: Log for future reference")
        
        # Add specific recommendations based on entities
        if entities['success'] and entities['entities']:
            if 'IP_ADDRESS' in entities['entities'] or 'IP' in entities['entities']:
                recommendations.append("Block identified IP addresses")
            if 'CVE' in entities['entities']:
                recommendations.append("Apply patches for identified CVEs")
            if any(hash_type in entities['entities'] for hash_type in ['MD5', 'SHA1', 'SHA256', 'HASH']):
                recommendations.append("Update antivirus signatures")
        
        return {
            'text': text,
            'overall_risk_score': overall_risk,
            'classification': classification,
            'severity': severity,
            'entities': entities,
            'recommendations': recommendations,
            'summary': {
                'threat_detected': classification.get('prediction', 'unknown') != 'unknown',
                'severity_level': severity.get('severity', 'unknown'),
                'entities_found': bool(entities.get('entities', {})),
                'models_used': {
                    'classification': classification.get('model_type', 'none'),
                    'severity': severity.get('model_type', 'none'),
                    'entities': entities.get('model_type', 'none')
                }
            }
        }
    
    def get_model_status(self) -> Dict:
        """Get status of all models"""
        return {
            'improved_classifier': self.classifier is not None,
            'improved_severity': self.severity_predictor is not None,
            'entity_extractor': self.entity_extractor is not None,
            'fallback_classifier': self.fallback_classifier is not None,
            'fallback_severity': self.fallback_severity is not None,
            'model_directory': self.model_dir
        }

# Global instance
analyzer = None

def initialize_analyzer(model_dir="models"):
    """Initialize the global analyzer"""
    global analyzer
    analyzer = SimpleThreatAnalyzer(model_dir)
    return analyzer

def get_analyzer():
    """Get the analyzer instance"""
    global analyzer
    if analyzer is None:
        analyzer = initialize_analyzer()
    return analyzer

# Backwards compatible functions
def classify_threat(text: str) -> str:
    """Backwards compatible classification"""
    result = get_analyzer().classify_threat(text)
    return result.get('prediction', 'unknown')

def predict_severity(text: str) -> str:
    """Backwards compatible severity prediction"""
    result = get_analyzer().predict_severity(text)
    return result.get('severity', 'unknown')

def extract_threat_entities(text: str) -> Dict:
    """Backwards compatible entity extraction"""
    result = get_analyzer().extract_entities(text)
    return result.get('entities', {})

# New enhanced functions
def analyze_threat_comprehensive(text: str) -> Dict:
    """New comprehensive analysis function"""
    return get_analyzer().comprehensive_analysis(text)

def get_model_info() -> Dict:
    """Get model information"""
    return get_analyzer().get_model_status()

if __name__ == "__main__":
    # Test the analyzer
    print("Testing Simple Enhanced Analyzer...")
    
    test_text = """
    Critical malware attack detected! Ransomware with hash d41d8cd98f00b204e9800998ecf8427e 
    is exploiting CVE-2021-34527 vulnerability. Attacker IP 192.168.1.100 has established 
    connection to command server evil-domain.com. Immediate action required!
    """
    
    analyzer = initialize_analyzer()
    result = analyzer.comprehensive_analysis(test_text)
    
    print("="*60)
    print("COMPREHENSIVE THREAT ANALYSIS")
    print("="*60)
    print(f"Overall Risk Score: {result['overall_risk_score']}/100")
    print(f"Classification: {result['classification']['prediction']} (confidence: {result['classification'].get('confidence', 0):.3f})")
    print(f"Severity: {result['severity']['severity']} (confidence: {result['severity'].get('confidence', 0):.3f})")
    print(f"Entities: {result['entities']['entities']}")
    print(f"\nRecommendations:")
    for rec in result['recommendations']:
        print(f"  - {rec}")
    
    print(f"\nModel Status:")
    status = analyzer.get_model_status()
    for model, loaded in status.items():
        print(f"  {model}: {'✅' if loaded else '❌'}")
