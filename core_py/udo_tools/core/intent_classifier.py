"""
Intent Classifier for uDOS
Classifies user queries to determine the best model to use
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
import joblib


class IntentClassifier:
    """Classifies user intent for model routing"""
    
    def __init__(self, model_path: Path = None):
        if model_path is None:
            model_path = Path.home() / ".udos" / "intent_classifier.joblib"
        self.model_path = model_path
        self.model = self._load_or_train_model()
        self.labels = [
            "code_gen", "debug", "refactor", "code_complete",
            "code_analysis", "general", "creative", "math"
        ]
    
    def _load_or_train_model(self) -> Pipeline:
        """Load trained model or train a new one"""
        if self.model_path.exists():
            try:
                return joblib.load(self.model_path)
            except Exception as e:
                print(f"Error loading model: {e}")
        
        # Train a new model if not found
        print("Training new intent classifier...")
        return self._train_model()
    
    def _train_model(self) -> Pipeline:
        """Train intent classifier on sample data"""
        # Sample training data
        X_train = [
            "write a function to sort a list",
            "create a python class",
            "generate code for API call",
            "make a rust implementation",
            "code a binary search",
            "Fix this TypeError",
            "Debug this segmentation fault",
            "Why is this code crashing?",
            "Error: module not found",
            "Refactor this function",
            "Optimize this loop",
            "Improve this algorithm",
            "Make this more efficient",
            "Complete this function",
            "Fill in this code",
            "Finish this implementation",
            "Explain this code",
            "What does this do?",
            "Analyze this algorithm",
            "Document this function",
            "What's the weather today?",
            "Tell me about Python",
            "Explain quantum computing",
            "Write a poem about code",
            "Create a story",
            "Generate a joke",
            "Solve this equation",
            "Calculate the integral",
            "Math problem help"
        ]
        
        y_train = [
            "code_gen", "code_gen", "code_gen", "code_gen", "code_gen",
            "debug", "debug", "debug", "debug",
            "refactor", "refactor", "refactor", "refactor",
            "code_complete", "code_complete", "code_complete",
            "code_analysis", "code_analysis", "code_analysis", "code_analysis",
            "general", "general", "general",
            "creative", "creative", "creative",
            "math", "math", "math"
        ]
        
        # Create pipeline
        model = Pipeline([
            ('tfidf', TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                max_features=500
            )),
            ('clf', RandomForestClassifier(
                n_estimators=100,
                random_state=42
            ))
        ])
        
        model.fit(X_train, y_train)
        
        # Save model
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, self.model_path)
        
        return model
    
    def classify(self, query: str) -> Tuple[str, float]:
        """Classify query intent with confidence score"""
        try:
            probas = self.model.predict_proba([query])[0]
            max_idx = np.argmax(probas)
            intent = self.labels[max_idx]
            confidence = probas[max_idx]
            return intent, float(confidence)
        except Exception as e:
            print(f"Classification error: {e}")
            return "general", 0.5  # Default to general with medium confidence
    
    def retrain(self, new_data: Dict[str, str]):
        """Retrain model with additional data"""
        # In a real implementation, this would load existing data
        # and append new data before retraining
        print("Retraining model with new data...")
        self.model = self._train_model()
    
    def get_intents(self) -> list:
        """Get list of supported intents"""
        return self.labels


# Global intent classifier instance
intent_classifier = IntentClassifier()
