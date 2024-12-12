# ML Model Deployment with Flask on Cloud Run
This repository contains the deployment setup for a machine-learning model. It uses Flask to create RESTful API endpoints and is deployed on Google Cloud Run for scalable, serverless hosting.

## Prerequisites
Before starting, ensure you have the following installed:
- Python 3.8 or later
- Google Cloud SDK
- Docker

## Flask Application
Flask Application
The Flask app serves as the API for the machine learning model. Below are the key features of app.py:

**Endpoints:**
- /predict: Accepts input data of "skills" (JSON) and return careers predictions.
- /generate: Generate About section for the CV Template Based on user provided career