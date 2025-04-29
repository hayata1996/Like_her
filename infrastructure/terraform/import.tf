// Import existing Artifact Registry repository
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# With Terraform Cloud, we'll manage imports through the UI or CLI
# rather than hardcoding them here

# Try to import Artifact Registry repository
# Command to run manually first:
# terraform import google_artifact_registry_repository.like-her-repo projects/{project_id}/locations/asia-northeast1/repositories/like-her