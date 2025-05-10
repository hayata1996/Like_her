# Like Her - AI Personal Assistant

A personal AI assistant inspired by the movie "Her" (2013), designed for the Google Cloud Japan AI Hackathon Vol.2.

**Last updated: April 26, 2025**

## Project Overview

This project creates a human-like voice assistant that:
- Provides conversational AI with voice input/output
- Delivers personalized insights based on health data
- Offers AI industry news and stock updates
- Uses a terminal-like interface for a unique aesthetic

## Architecture

The application consists of three main components:
- **Frontend**: Streamlit-based UI with voice interaction capabilities
- **API**: Backend service that integrates with local LLM and external APIs
- **Scheduler**: Handles regular tasks like news fetching and health data analysis

## Tech Stack

- **ML Model**: Local Swallow1.5 model by sakana.ai
- **Frontend**: Streamlit with terminal-like UI
- **Backend**: FastAPI
- **Infrastructure**: Google Cloud (deployed via Terraform)
- **Data Storage**: BigQuery
- **Containerization**: Docker
- **Health Data**: Huawei Health Kit API

## Local Development

### Prerequisites
- Docker and Docker Compose
- Google Cloud CLI (for deployment)
- Terraform (for infrastructure management)

### Getting Started

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/like-her.git
   cd like-her
   ```

2. Run the application locally:
   ```
   docker-compose up
   ```

3. Access the application:
   - Frontend: http://localhost:8501
   - API: http://localhost:8080

## Deployment

### Setting up Google Cloud

1. Create a new Google Cloud project
2. Enable required APIs:
   - Cloud Run
   - Cloud Scheduler
   - BigQuery
   - Artifact Registry

### Deploying with Terraform

1. Navigate to the infrastructure directory:
   ```
   cd infrastructure/terraform
   ```

2. Initialize Terraform:
   ```
   terraform init
   ```

3. Create a `terraform.tfvars` file with your project information:
   ```
   project_id = "your-gcp-project-id"
   ```

4. Apply the Terraform configuration:
   ```
   terraform apply
   ```

## Project Structure

```
.
├── app
│   ├── api              # Backend API service
│   ├── frontend         # Streamlit UI
│   └── scheduler        # Scheduled jobs
├── data                 # Data storage (local development)
├── docs                 # Documentation
├── infrastructure       # IaC with Terraform
│   └── terraform
└── docker-compose.yml   # Local development orchestration
```

## Hackathon Link
[Google Cloud Japan AI Hackathon Vol.2](https://zenn.dev/hackathons/google-cloud-japan-ai-hackathon-vol2)