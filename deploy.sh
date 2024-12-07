cd test-deploy
docker build -t ml-model-test .
docker tag ml-model-test gcr.io/test-1-7ccf2/ml-model-test
docker push gcr.io/test-1-7ccf2/ml-model-test
gcloud run deploy ml-model-test --image gcr.io/test-1-7ccf2/ml-model-test --platform managed --memory 1Gi --region asia-southeast2 --allow-unauthenticated