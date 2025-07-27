

# Iris ML API with Continuous Deployment on GKE

This project demonstrates a complete Continuous Deployment (CD) pipeline for a machine learning application. The pipeline automatically builds, tests, and deploys a simple Iris flower classification API to a Google Kubernetes Engine (GKE) cluster whenever changes are pushed to the main branch.

The core of the automation is managed by **GitHub Actions** for orchestration, **Docker** for containerization, **CML (Continuous Machine Learning)** for reporting, and **Google Cloud Platform (GCP)** for hosting.

## 🚀 Pipeline Workflow

The CD pipeline is designed to be fully automated:

1.  **Code Push:** A developer pushes code changes to the `main` branch of the GitHub repository.
2.  **Trigger Workflow:** The push event automatically triggers the GitHub Actions workflow defined in `.github/workflows/cd.yml`.
3.  **Authentication:** The workflow authenticates with Google Cloud using a Service Account.
4.  **Build & Push Image:** It builds a Docker image of the FastAPI application and pushes it to Google Artifact Registry with a unique tag based on the commit SHA.
5.  **Deploy to GKE:** The workflow updates the Kubernetes deployment manifest with the new image tag and applies it to the GKE cluster, triggering a rolling update.
6.  **Test & Report:** A CML-driven Python script (`.cml/cd-pipeline.py`) runs to:
    *   Verify the deployment was successful.
    *   Test the live API endpoint with a sample prediction request.
    *   Generate a `report.md` file summarizing the deployment status and test results.
7.  **Create Comment:** CML posts the contents of `report.md` as a comment on the triggering commit, providing immediate feedback directly in GitHub.

## 🛠️ Technology Stack

*   **Machine Learning:** Scikit-learn, Pandas
*   **API Framework:** FastAPI
*   **CI/CD:** GitHub Actions, CML (Continuous Machine Learning)
*   **Containerization:** Docker
*   **Cloud & Orchestration:** Google Kubernetes Engine (GKE), Google Artifact Registry

## 📂 File & Directory Structure

Here is a breakdown of the key files and their objectives in this project.

| File / Directory                | Objective                                                                                                                                                                             |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`app/`**                      | This directory contains all the source code for the Python-based API.                                                                                                                 |
| └── `main.py`                   | The entry point of our application. It uses **FastAPI** to define the API endpoints, specifically the `/predict` endpoint that accepts feature data and returns an Iris species prediction. |
| └── `model.py`                  | A helper module responsible for loading the pre-trained `iris_model.pkl` from disk and providing a function to make predictions on new data.                                            |
| **`model/`**                    | This directory stores the trained machine learning model artifacts.                                                                                                                   |
| └── `iris_model.pkl`            | The serialized, pre-trained scikit-learn model file. This model is loaded by the API at startup to serve predictions.                                                                   |
| **`.github/workflows/`**        | Contains the GitHub Actions workflow definitions.                                                                                                                                     |
| └── `cd.yml`                    | The brain of the automation. This YAML file defines the entire Continuous Deployment pipeline, including jobs, steps, environment variables, and triggers.                                |
| **`.cml/`**                     | This directory holds scripts and configurations related to CML.                                                                                                                       |
| └── `cd-pipeline.py`            | A Python script executed by the CD workflow. Its job is to check the deployment status, retrieve the external IP of the service, run a live test against the API, and generate `report.md`. |
| └── `requirements.txt`          | Lists the Python packages needed specifically for the `.cml/cd-pipeline.py` script (e.g., `requests`). This is separate from the main application's requirements.                            |
| **`kubernetes/`**               | This directory contains the Kubernetes manifest files, which are templates for our application's resources in GKE.                                                                    |
| └── `deployment.yaml`           | A Kubernetes manifest that defines the **Deployment**. It specifies the Docker image to use, the number of replicas (pods), and the container port. The image tag is updated dynamically by the pipeline. |
| └── `service.yaml`              | A Kubernetes manifest that defines the **Service**. It exposes the application to the internet by creating a Network Load Balancer with a public IP address, routing traffic to the pods managed by the Deployment. |
| **`Dockerfile`**                | A set of instructions for building the Docker image for our FastAPI application. It handles installing dependencies from `requirements.txt`, copying the application code, and defining the command to run the server. |
| **`requirements.txt`**          | The main list of Python dependencies required for the FastAPI application itself (e.g., `fastapi`, `uvicorn`, `scikit-learn`, `pandas`).                                                |
| **`README.md`**                 | This file. It provides the documentation and overview for the project.                                                                                                                |

## ⚙️ Setup & Configuration

To run this pipeline, you need to configure the following prerequisites:

1.  **Google Cloud Project:**
    *   A GKE cluster.
    *   An Artifact Registry repository.
    *   A Service Account with permissions for GKE and Artifact Registry.
    *   The JSON key for the Service Account.

2.  **GitHub Repository Secrets:**
    *   `GCP_PROJECT_ID`: Your Google Cloud project ID.
    *   `GCP_SA_KEY`: The base64-encoded JSON key of your Google Cloud Service Account.
    *   The `cd.yml` workflow should also have `permissions: contents: write` to allow CML to post comments.
