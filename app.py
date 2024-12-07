import os
import logging
import json
import base64
from typing import List, Tuple, Dict, Optional

import numpy as np
import tensorflow as tf
import firebase_admin
from flask import Flask, request, jsonify
from google.cloud import pubsub_v1, storage
from firebase_admin import firestore

# Initialize Firebase Admin at the top of your file
firebase_admin.initialize_app()

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ml_service.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Initialize Google Cloud Storage client
storage_client = storage.Client()

# Download model and tokenizer from Cloud Storage
def download_from_gcs(bucket_name: str, source_blob_name: str, destination_file_name: str):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    logger.info(f"Downloaded {source_blob_name} to {destination_file_name}")

# Download required files
download_from_gcs('deploy-ml-1', 'model_nextStep.h5', 'model_nextStep.h5')
download_from_gcs('deploy-ml-1', 'tokenizer_and_labels.json', 'tokenizer_and_labels.json')

# Load the model
model = tf.keras.models.load_model('model_nextStep.h5')

# Load tokenizer and job labels from JSON
with open('tokenizer_and_labels.json', 'r') as f:
    tokenizer_data = json.load(f)

# Convert tokenizer dictionary to JSON string
tokenizer_json = json.dumps(tokenizer_data)

# Load tokenizer from JSON string
tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(tokenizer_json)

# Load job labels
y_titles = tokenizer_data.get('job_titles', {})
index_to_job_title = {index: title for title, index in y_titles.items()}

class MLPredictionService:
    def __init__(self):
        self.publisher = pubsub_v1.PublisherClient()
        self.project_id = 'test-1-7ccf2'
        self.topic_name = 'ml-prediction-result'
        self.topic_path = self.publisher.topic_path(self.project_id, self.topic_name)
        self.db = firestore.client()

    def get_roadmap_ids(self, job_titles: List[str]) -> List[Dict[str, str]]:
        matched_jobs = []
        
        # Query Firestore for each job title
        for job_title in job_titles:
            # Query the roadmaps collection where title matches the job title
            query = self.db.collection('roadmaps').where('career', '==', job_title).limit(1)
            docs = query.stream()
            
            # Get the first matching document
            for doc in docs:
                doc_data = doc.to_dict()
                matched_jobs.append({
                    'title': job_title,
                    'roadmapId': doc_data.get('id')
                })
                break 
            
            # If no roadmap found, include the job title without an ID
            if not any(job['title'] == job_title for job in matched_jobs):
                matched_jobs.append({
                    'title': job_title,
                    'roadmapId': None
                })
        
        return matched_jobs

    def publish_prediction_result(self, data: dict):
        try:
            message_data = json.dumps(data).encode('utf-8')
            future = self.publisher.publish(self.topic_path, data=message_data)
            message_id = future.result()
            logger.info(f"Published message {message_id} to {self.topic_path}")
        except Exception as e:
            logger.error(f"Error publishing message: {e}")
            raise

def predict_top_jobs(skills: List[str], label_map: Dict[int, str], top_n: int = 3) -> List[Tuple[str, float]]:
    # Convert skills to one-hot representation using tokenizer
    skills_encoded = tokenizer.texts_to_matrix([' '.join(skills)], mode='binary')

    # Make predictions
    predictions = model.predict(skills_encoded)

    # Get indices and probabilities of top predictions
    top_indices = np.argsort(predictions[0])[::-1][:top_n]
    top_jobs = [label_map[idx] for idx in top_indices]

    return top_jobs

def create_app() -> Flask:
    """Create and configure Flask application."""
    app = Flask(__name__)
    ml_service = MLPredictionService()

    @app.route('/', methods=['GET'])
    def home():
        return jsonify({'status': 'ML Service is running'}), 200

    @app.route('/predict', methods=['POST'])
    def predict():
        try:
            # Validate Pub/Sub message structure
            envelope = request.get_json()
            if not envelope or "message" not in envelope:
                return jsonify({'error': 'Invalid Pub/Sub message'}), 400

            pubsub_message = envelope["message"]
            message_data = base64.b64decode(pubsub_message.get("data", "")).decode("utf-8")
            decoded_message = json.loads(message_data)

            request_id = decoded_message.get("request_id")
            skills = decoded_message.get("input_data", [])

            # Validate input
            if not skills or not isinstance(skills, list):
                raise ValueError("Invalid input: skills must be a non-empty list")

            # Predict top jobs
            top_jobs = predict_top_jobs(skills, index_to_job_title, top_n=3)
            matched_jobs = ml_service.get_roadmap_ids(top_jobs)

            predicted_data = {
                'request_id': request_id,
                'predicted_jobs': matched_jobs,
                'skills': skills,
            }

            # Publish results
            ml_service.publish_prediction_result(predicted_data)

            return jsonify(predicted_data), 200

        except ValueError as ve:
            logger.warning(f"Validation error: {ve}")
            return jsonify({'error': str(ve)}), 200
        except Exception as e:
            logger.error(f"Prediction endpoint error: {e}")
            return jsonify({'error': 'Internal server error'}), 200

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)