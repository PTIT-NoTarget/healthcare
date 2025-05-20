import csv
import json
import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
import time
import codecs

# File paths
CSV_DATA_PATH = 'medquad.csv'
MODEL_SAVE_PATH = 'healthcare_bot_model.pkl'
SAMPLE_SIZE = 5000  # Process 5000 samples, or None for all data

# Set up logging
def log(message):
    """Simple logging function that includes timestamps"""
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

def clean_text(text):
    """Clean and normalize text"""
    if not isinstance(text, str):
        return ""
        
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    # Convert to lowercase for consistency
    text = text.lower()
    # Remove punctuation that might interfere with matching
    text = re.sub(r'[^\w\s]', ' ', text)
    return text.strip()

def truncate_text(text, max_length=1000):
    """Truncate very long answers to a reasonable length"""
    if len(text) <= max_length:
        return text
    
    # Try to find a period to break at
    cutoff = text[:max_length].rfind('.')
    if cutoff > max_length // 2:
        return text[:cutoff+1]
    
    return text[:max_length] + "..."

def validate_csv_file(filepath):
    """Check if the file exists and is readable"""
    if not os.path.exists(filepath):
        log(f"Error: File {filepath} does not exist")
        return False
    
    if not os.path.isfile(filepath):
        log(f"Error: {filepath} is not a file")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            sample = f.read(1024)
            if not sample:
                log(f"Error: File {filepath} is empty")
                return False
        return True
    except Exception as e:
        log(f"Error validating file: {e}")
        return False

def load_medquad_data(filepath, max_samples=None):
    """Load QA pairs from medquad.csv using pandas"""
    log(f"Loading data from {filepath} using pandas...")
    
    # Check if file exists
    if not os.path.exists(filepath):
        log(f"Error: File {filepath} does not exist")
        return [], []
    
    try:
        # Try to read the file with pandas - it can automatically detect delimiter in many cases
        log("Attempting to read CSV with pandas...")
        
        # First try with default settings
        try:
            df = pd.read_csv(filepath, encoding='utf-8', on_bad_lines='skip')
            log(f"Successfully read CSV with {len(df)} rows and {len(df.columns)} columns")
        except Exception as e:
            log(f"Standard read failed: {e}, trying with auto-delimiter detection...")
            
            # If that fails, try with specific delimiters
            for sep in [',', '\t', '|', ';']:
                try:
                    df = pd.read_csv(filepath, sep=sep, encoding='utf-8', on_bad_lines='skip')
                    if len(df.columns) >= 2:
                        log(f"Successfully read CSV with delimiter '{sep}', found {len(df)} rows and {len(df.columns)} columns")
                        break
                except Exception:
                    continue
            else:
                # If all attempts fail, try with the C engine which might be more forgiving
                log("Trying with the C engine and Python's csv module fallback...")
                df = pd.read_csv(filepath, engine='python', encoding='utf-8', on_bad_lines='skip')
                log(f"Read CSV using Python engine with {len(df)} rows and {len(df.columns)} columns")
        
        # Check if we have at least 2 columns
        if len(df.columns) < 2:
            log(f"Error: CSV file has fewer than 2 columns: {df.columns}")
            return [], []
        
        # Get the first two columns regardless of their names
        question_col = df.columns[0]
        answer_col = df.columns[1]
        
        log(f"Using columns: Question='{question_col}', Answer='{answer_col}'")
        
        # Extract questions and answers
        questions = []
        answers = []
        
        # Limit to max_samples if specified
        if max_samples:
            df = df.head(max_samples)
        
        # Process each row
        for index, row in df.iterrows():
            question = str(row[question_col]).strip()
            answer = str(row[answer_col]).strip()
            
            # Skip empty entries
            if not question or not answer or question == 'nan' or answer == 'nan':
                continue
                
            # Truncate very long answers
            answer = truncate_text(answer)
            
            questions.append(question)
            answers.append(answer)
            
            # Log progress for large datasets
            if (index + 1) % 1000 == 0:
                log(f"Processed {index + 1} rows...")
        
        log(f"Successfully loaded {len(questions)} Q&A pairs")
        return questions, answers
        
    except Exception as e:
        log(f"Error loading data with pandas: {e}")
        log("Falling back to manual file inspection")
        
        # Print file info as a last resort
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                sample = f.read(1000)
                log(f"File sample: {sample}")
        except Exception as e:
            log(f"Couldn't read file sample: {e}")
        
        return [], []

def train_retrieval_model(questions, answers):
    """Create and train a retrieval-based model using TF-IDF"""
    log("Processing questions for TF-IDF vectorization...")
    
    # Clean questions for better matching
    cleaned_questions = [clean_text(q) for q in questions]
    
    # Create TF-IDF vectorizer
    log("Creating TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        stop_words='english',
        max_features=10000,  # Limit features to improve performance
        min_df=2  # Ignore terms that appear in less than 2 documents
    )
    
    # Fit and transform questions to TF-IDF vectors
    log("Fitting vectorizer to questions...")
    question_vectors = vectorizer.fit_transform(cleaned_questions)
    log(f"Created {question_vectors.shape[1]} features for {question_vectors.shape[0]} questions")
    
    # Create model dictionary
    model = {
        'vectorizer': vectorizer,
        'question_vectors': question_vectors,
        'questions': questions,
        'cleaned_questions': cleaned_questions,
        'answers': answers
    }
    
    return model

def save_model(model, filepath):
    """Save model to disk"""
    log(f"Saving model to {filepath}...")
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)
    log("Model saved successfully")

def test_model(model, test_questions=None):
    """Test the model with a few predefined questions"""
    if test_questions is None:
        test_questions = [
            "What is glaucoma?",
            "How can I prevent high blood pressure?",
            "What are the symptoms of urinary tract infections?",
        ]
    
    log("\n--- Testing Model with Sample Questions ---")
    for question in test_questions:
        answer, confidence, matched_question = get_answer(question, model)
        print(f"\nQ: {question}")
        print(f"A: {answer[:150]}..." if len(answer) > 150 else f"A: {answer}")
        print(f"[Confidence: {confidence:.2f}, Match: '{matched_question}']\n")
        print("-" * 50)

def get_answer(query, model, top_k=3):
    """Get answer for a query using the retrieval model"""
    # Clean and process the query
    processed_query = clean_text(query)
    
    # Get model components
    vectorizer = model['vectorizer']
    question_vectors = model['question_vectors']
    questions = model['questions']
    cleaned_questions = model['cleaned_questions']  
    answers = model['answers']
    
    # Transform query to vector
    query_vector = vectorizer.transform([processed_query])
    
    # Calculate similarities
    similarities = cosine_similarity(query_vector, question_vectors)[0]
    
    # Get top-k most similar questions
    top_indices = similarities.argsort()[-top_k:][::-1]
    top_similarities = similarities[top_indices]
    
    # If the most similar question has high similarity, return its answer directly
    if top_similarities[0] > 0.5:  # Threshold for "high confidence"
        return answers[top_indices[0]], top_similarities[0], questions[top_indices[0]]
    
    # Otherwise, check if we have any reasonable matches
    if top_similarities[0] > 0.2:  # Threshold for "some confidence"
        return answers[top_indices[0]], top_similarities[0], questions[top_indices[0]]
    
    # Fall back to a generic answer with the most similar question
    return "I don't have enough information to answer that question confidently.", top_similarities[0], questions[top_indices[0]]

def inspect_file_content(filepath):
    """Read and print the first few lines of the file to help diagnose issues"""
    try:
        log(f"Inspecting file: {filepath}")
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [f.readline().strip() for _ in range(3)]
        
        log(f"File preview (first 3 lines):")
        for i, line in enumerate(lines):
            log(f"Line {i+1}: {line[:100]}...")
            
        # Try to guess the delimiter by looking for common patterns
        for delimiter in [',', '\t', '|', ';']:
            parts = [len(line.split(delimiter)) for line in lines]
            if min(parts) > 1 and max(parts) == min(parts):
                log(f"Possible delimiter: '{delimiter}' (splits lines into {parts[0]} parts)")
    except Exception as e:
        log(f"Error inspecting file: {e}")

if __name__ == "__main__":
    log("Starting healthcare chatbot training...")
    
    # Inspect the file to help diagnose issues
    inspect_file_content(CSV_DATA_PATH)
    
    # Load data from CSV using pandas
    questions, answers = load_medquad_data(CSV_DATA_PATH, SAMPLE_SIZE)
    
    if not questions:
        log("Error: No data loaded. Exiting.")
        exit(1)
    
    # Train the model
    log("Training model...")
    model = train_retrieval_model(questions, answers)
    
    # Save the model
    save_model(model, MODEL_SAVE_PATH)
    
    # Test the model with a few sample questions
    test_model(model)
    
    log("Training complete!") 