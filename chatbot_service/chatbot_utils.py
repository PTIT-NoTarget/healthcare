import pickle
import re
from sklearn.metrics.pairwise import cosine_similarity
import sys
import os
import logging

logger = logging.getLogger(__name__)

# File path to the trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'healthcare_bot_model.pkl')

def load_model(model_path=MODEL_PATH):
    """Load the trained model from disk"""
    if not os.path.exists(model_path):
        logger.error(f"Error: Model file {model_path} not found.")
        return None
    
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        logger.info(f"Model loaded successfully with {len(model['questions'])} Q&A pairs.")
        return model
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None

def clean_text(text):
    """Clean and normalize text for processing"""
    if not isinstance(text, str):
        return ""
        
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    # Convert to lowercase for consistency
    text = text.lower()
    # Remove punctuation that might interfere with matching
    text = re.sub(r'[^\w\s]', ' ', text)
    return text.strip()

def get_answer(query, model):
    """Get answer for a user query"""
    # If model is not loaded, return error message
    if model is None:
        return "I'm sorry, but I'm not able to answer questions right now. Please try again later."
    
    # Clean and process the query
    processed_query = clean_text(query)
    
    # Get model components
    vectorizer = model['vectorizer']
    question_vectors = model['question_vectors']
    questions = model['questions']
    answers = model['answers']
    
    # Transform query to vector
    query_vector = vectorizer.transform([processed_query])
    
    # Calculate similarities
    similarities = cosine_similarity(query_vector, question_vectors)[0]
    
    # Get top most similar questions
    top_indices = similarities.argsort()[-3:][::-1]  # Get top 3 matches
    top_similarities = similarities[top_indices]
    
    # Return the best match based on confidence threshold
    if top_similarities[0] > 0.5:  # High confidence threshold
        return answers[top_indices[0]]
    elif top_similarities[0] > 0.2:  # Medium confidence threshold
        return answers[top_indices[0]]
    else:
        return "I don't have enough information to answer that question confidently."

# Global model instance - load once at module import time
try:
    model_instance = load_model()
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    model_instance = None 