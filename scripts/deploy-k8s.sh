#!/bin/bash
set -e

# Configuration
PROJECT_ID=${PROJECT_ID:-"your-project-id"}
GKE_CLUSTER=${GKE_CLUSTER:-"iris-cluster"}
GKE_ZONE=${GKE_ZONE:-"us-central1-a"}
DEPLOYMENT_NAME=${DEPLOYMENT_NAME:-"iris-api-deployment"}
COMMIT_SHA=${GITHUB_SHA:-$(git rev-parse HEAD)}

echo "Deploying to Kubernetes..."
echo "Cluster: $GKE_CLUSTER"
echo "Zone: $GKE_ZONE"
echo "Deployment: $DEPLOYMENT_NAME"

# Get cluster credentials
gcloud container clusters get-credentials "$GKE_CLUSTER" --zone "$GKE_ZONE"

# Update deployment with new image
sed -i "s|PROJECT_ID|$PROJECT_ID|g" k8s/deployment.yaml
kubectl apply -f k8s/deployment.yaml

# Update image
kubectl set image deployment/$DEPLOYMENT_NAME \
    iris-api=us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/iris-api:$COMMIT_SHA

# Wait for rollout
kubectl rollout status deployment/$DEPLOYMENT_NAME

# Get service info
echo "Deployment completed! Service info:"
kubectl get services iris-api-service -o wide
