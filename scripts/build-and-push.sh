#!/bin/bash
set -e

# Configuration
PROJECT_ID=${PROJECT_ID:-"your-project-id"}
REGISTRY_LOCATION=${REGISTRY_LOCATION:-"us-central1"}
IMAGE_NAME=${IMAGE_NAME:-"iris-api"}
COMMIT_SHA=${GITHUB_SHA:-$(git rev-parse HEAD)}

echo "Building and pushing Docker image..."
echo "Project ID: $PROJECT_ID"
echo "Registry: $REGISTRY_LOCATION-docker.pkg.dev"
echo "Image: $IMAGE_NAME"
echo "Commit SHA: $COMMIT_SHA"

# Build image
cd app
docker build -t "$REGISTRY_LOCATION-docker.pkg.dev/$PROJECT_ID/my-repo/$IMAGE_NAME:$COMMIT_SHA" .
docker tag "$REGISTRY_LOCATION-docker.pkg.dev/$PROJECT_ID/my-repo/$IMAGE_NAME:$COMMIT_SHA" \
           "$REGISTRY_LOCATION-docker.pkg.dev/$PROJECT_ID/my-repo/$IMAGE_NAME:latest"

# Push image
docker push "$REGISTRY_LOCATION-docker.pkg.dev/$PROJECT_ID/my-repo/$IMAGE_NAME:$COMMIT_SHA"
docker push "$REGISTRY_LOCATION-docker.pkg.dev/$PROJECT_ID/my-repo/$IMAGE_NAME:latest"

echo "Image pushed successfully!"
