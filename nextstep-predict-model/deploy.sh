docker build -t ml-model-predict .
docker tag ml-model-predict gcr.io/next-step-442801/ml-model-predict
docker push gcr.io/next-step-442801/ml-model-predict
gcloud run deploy ml-model-predict --image gcr.io/next-step-442801/ml-model-predict --platform managed --memory 1Gi --region asia-southeast2 --allow-unauthenticated