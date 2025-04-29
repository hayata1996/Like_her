terraform {
  cloud {
    organization = "org_for_like_her"
    workspaces {
      name = "like-her"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
  credentials = var.google_credentials
}

# Artifact Registry repository defined as a resource (not data source)
resource "google_artifact_registry_repository" "like-her-repo" {
  location      = var.region
  repository_id = "like-her"
  description   = "Docker repository for Like Her application"
  format        = "DOCKER"
  
  # Add lifecycle configuration for extra protection
  lifecycle {
    ignore_changes = [
      description,
      format
    ]
    prevent_destroy = true
  }
}

# IAM - Grant push access to GitHub Actions
resource "google_artifact_registry_repository_iam_member" "github_push_access" {
  project    = var.project_id
  location   = google_artifact_registry_repository.like-her-repo.location
  repository = google_artifact_registry_repository.like-her-repo.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:admin-for-like-her@for-like-her.iam.gserviceaccount.com"
}

# Secret Manager for storing sensitive data
resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "gemini-api-key"
  
  replication {
    user_managed {
      replicas {
        location = "asia-northeast1"
      }
    }
  }

  lifecycle {
    ignore_changes = [
      replication,
    ]
    prevent_destroy = true
  }
}

# Create a secret version with the Gemini API key
resource "google_secret_manager_secret_version" "gemini_api_key_version" {
  secret      = google_secret_manager_secret.gemini_api_key.id
  secret_data = var.gemini_api_key

  lifecycle {
    prevent_destroy = false
  }
}

# Secret for allowed user email
resource "google_secret_manager_secret" "allowed_user_email" {
  secret_id = "allowed-user-email"
  
  replication {
    user_managed {
      replicas {
        location = "asia-northeast1"
      }
    }
  }

  lifecycle {
    ignore_changes = [
      replication,
    ]
    prevent_destroy = false
  }
}

# Create a secret version with the allowed user email
resource "google_secret_manager_secret_version" "allowed_user_email_version" {
  secret      = google_secret_manager_secret.allowed_user_email.id
  secret_data = var.allowed_user_email

  lifecycle {
    prevent_destroy = false
  }
}

# Local data source to read the email address safely
locals {
  allowed_user_email = var.allowed_user_email
}

# Allow Cloud Run service to access the secrets
resource "google_secret_manager_secret_iam_member" "api_gemini_access" {
  secret_id = google_secret_manager_secret.gemini_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:admin-for-like-her@for-like-her.iam.gserviceaccount.com"
}

resource "google_secret_manager_secret_iam_member" "api_email_access" {
  secret_id = google_secret_manager_secret.allowed_user_email.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:admin-for-like-her@for-like-her.iam.gserviceaccount.com"
}

# Cloud Run v2 service for API
resource "google_cloud_run_v2_service" "api" {
  name     = "like-her-api"
  location = var.region

  template {
    service_account = "admin-for-like-her@for-like-her.iam.gserviceaccount.com"
    
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/like-her/like-her-api:latest"
      
      resources {
        limits = {
          cpu    = "1000m"
          memory = "2Gi"
        }
      }
      
      env {
        name  = "MODEL_PATH"
        value = "/data/models"
      }
      
      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      
      env {
        name  = "LOCATION"
        value = "asia-northeast1"  # AI Builder's primary region
      }
      
      env {
        name  = "AGENT_ID"
        value = var.agent_id  # The ID of your AI Builder agent
      }
    }
  }
  
  # Add lifecycle block to prevent recreation issues
  lifecycle {
    create_before_destroy = true
  }
}

# IAM policy binding for API service - using v2 format
resource "google_cloud_run_v2_service_iam_policy" "api_noauth_policy" {
  name        = google_cloud_run_v2_service.api.name
  location    = google_cloud_run_v2_service.api.location
  project     = var.project_id
  
  policy_data = jsonencode({
    bindings = [
      {
        role = "roles/run.invoker"
        members = [
          "user:${local.allowed_user_email}",
        ]
      }
    ]
  })
}

# Cloud Run v2 service for Frontend
resource "google_cloud_run_v2_service" "frontend" {
  name     = "like-her-frontend"
  location = var.region

  template {
    service_account = "admin-for-like-her@for-like-her.iam.gserviceaccount.com"
    
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/like-her/like-her-frontend:latest"
      
      resources {
        limits = {
          cpu    = "1000m"
          memory = "1Gi"
        }
      }
      
      env {
        name  = "API_URL"
        value = google_cloud_run_v2_service.api.uri
      }
    }
  }
  
  # Add lifecycle block to prevent recreation issues
  lifecycle {
    create_before_destroy = true
  }
}

# IAM policy binding for Frontend service - using v2 format
resource "google_cloud_run_v2_service_iam_policy" "frontend_noauth_policy" {
  name        = google_cloud_run_v2_service.frontend.name
  location    = google_cloud_run_v2_service.frontend.location
  project     = var.project_id
  
  policy_data = jsonencode({
    bindings = [
      {
        role = "roles/run.invoker"
        members = [
          "user:${local.allowed_user_email}",
        ]
      }
    ]
  })
}

# BigQuery dataset for data storage
resource "google_bigquery_dataset" "like_her_dataset" {
  dataset_id    = "like_her_dataset"
  friendly_name = "Like Her Dataset"
  location      = "asia-northeast1"

  lifecycle {
    prevent_destroy = false
  }
}

# BigQuery tables
resource "google_bigquery_table" "health_data" {
  dataset_id = google_bigquery_dataset.like_her_dataset.dataset_id
  table_id   = "health_data"

  schema = <<EOF
[
  {
    "name": "timestamp",
    "type": "TIMESTAMP",
    "mode": "REQUIRED"
  },
  {
    "name": "data_type",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "value",
    "type": "FLOAT",
    "mode": "REQUIRED"
  }
]
EOF

  deletion_protection = false

  lifecycle {
    prevent_destroy = false
  }
}

resource "google_bigquery_table" "news_data" {
  dataset_id = google_bigquery_dataset.like_her_dataset.dataset_id
  table_id   = "news_data"

  schema = <<EOF
[
  {
    "name": "timestamp",
    "type": "TIMESTAMP",
    "mode": "REQUIRED"
  },
  {
    "name": "title",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "content",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "source",
    "type": "STRING",
    "mode": "REQUIRED"
  }
]
EOF

  deletion_protection = false

  lifecycle {
    prevent_destroy = false
  }
}

# Cloud Scheduler for scheduled tasks
resource "google_cloud_scheduler_job" "daily_news_job" {
  name      = "daily-ai-news-job"
  schedule  = "0 3 * * *"  # Run at 3 AM daily
  time_zone = "Asia/Tokyo"
  region    = var.region

  http_target {
    uri         = "${google_cloud_run_v2_service.api.uri}/tasks/fetch-news"
    http_method = "POST"
    
    # Add this to ensure that authentication works
    oidc_token {
      service_account_email = "admin-for-like-her@for-like-her.iam.gserviceaccount.com"
      audience              = google_cloud_run_v2_service.api.uri
    }
  }

  depends_on = [google_cloud_run_v2_service.api]
}

resource "google_cloud_scheduler_job" "weekly_papers_job" {
  name      = "weekly-papers-job"
  schedule  = "0 20 * * 5"  # Run at 8 PM on Fridays
  time_zone = "Asia/Tokyo"
  region    = var.region

  http_target {
    uri         = "${google_cloud_run_v2_service.api.uri}/tasks/fetch-papers"
    http_method = "POST"
    
    # Add this to ensure that authentication works
    oidc_token {
      service_account_email = "admin-for-like-her@for-like-her.iam.gserviceaccount.com"
      audience              = google_cloud_run_v2_service.api.uri
    }
  }

  depends_on = [google_cloud_run_v2_service.api]
}