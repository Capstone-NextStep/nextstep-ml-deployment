docker build -t ml-model-generate .
docker tag ml-model-generate gcr.io/next-step-442801/ml-model-generate
docker push gcr.io/next-step-442801/ml-model-generate
gcloud run deploy ml-model-generate --image gcr.io/next-step-442801/ml-model-generate --platform managed --memory 1Gi --region asia-southeast2 --allow-unauthenticated