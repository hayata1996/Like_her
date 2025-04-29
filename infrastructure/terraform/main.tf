terraform {
  cloud {
    organization = "org_for_like_her"  # Updated to match what's likely your organization name
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
    prevent_destroy = false
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

# After the secret has been created, we can reference it in a data source
# This data source will be used to access the email address
# if the latest is destoroied, build will fail
data "google_secret_manager_secret_version" "email_version" {
  secret  = google_secret_manager_secret.allowed_user_email.id
  version = "latest"
  
  depends_on = [
    google_secret_manager_secret_version.allowed_user_email_version
  ]
}

# Allow Cloud Run service to access the secrets
resource "google_secret_manager_secret_iam_member" "api_gemini_access" {
  secret_id = google_secret_manager_secret.gemini_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  # Use the admin-for-like-her service account
  member    = "serviceAccount:admin-for-like-her@for-like-her.iam.gserviceaccount.com"
}

resource "google_secret_manager_secret_iam_member" "api_email_access" {
  secret_id = google_secret_manager_secret.allowed_user_email.id
  role      = "roles/secretmanager.secretAccessor"
  # Use the admin-for-like-her service account
  member    = "serviceAccount:admin-for-like-her@for-like-her.iam.gserviceaccount.com"
}

# Cloud Run service for API
resource "google_cloud_run_service" "api" {
  name     = "like-her-api"
  location = var.region

  template {
    spec {
      service_account_name = "admin-for-like-her@for-like-her.iam.gserviceaccount.com"
      containers {
        image = "gcr.io/${var.project_id}/like-her-api:latest"
        
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
        
        # Add AI Builder environment variables instead of Gemini
        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }
        
        env {
          name  = "LOCATION"
          value = "us-central1"  # AI Builder's primary region
        }
        
        env {
          name  = "AGENT_ID"
          value = var.agent_id  # The ID of your AI Builder agent
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# IAM policy binding for API service - restrict to user only
resource "google_cloud_run_service_iam_binding" "api_no_public_access" {
  location = google_cloud_run_service.api.location
  service  = google_cloud_run_service.api.name
  role     = "roles/run.invoker"
  members  = [
    "user:${data.google_secret_manager_secret_version.email_version.secret_data}"
  ]

  depends_on = [
    data.google_secret_manager_secret_version.email_version
  ]
}

# Cloud Run service for Frontend
resource "google_cloud_run_service" "frontend" {
  name     = "like-her-frontend"
  location = var.region

  template {
    spec {
      service_account_name = "admin-for-like-her@for-like-her.iam.gserviceaccount.com"
      containers {
        image = "gcr.io/${var.project_id}/like-her-frontend:latest"
        
        resources {
          limits = {
            cpu    = "1000m"
            memory = "1Gi"
          }
        }
        
        env {
          name  = "API_URL"
          value = google_cloud_run_service.api.status[0].url
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# IAM policy binding for Frontend service - restrict to user only
resource "google_cloud_run_service_iam_binding" "frontend_no_public_access" {
  location = google_cloud_run_service.frontend.location
  service  = google_cloud_run_service.frontend.name
  role     = "roles/run.invoker"
  members  = [
    "user:${data.google_secret_manager_secret_version.email_version.secret_data}"
  ]

  depends_on = [
    data.google_secret_manager_secret_version.email_version
  ]
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
    uri         = "${google_cloud_run_service.api.status[0].url}/tasks/fetch-news"
    http_method = "POST"
  }

  depends_on = [google_cloud_run_service.api]
}

resource "google_cloud_scheduler_job" "weekly_papers_job" {
  name      = "weekly-papers-job"
  schedule  = "0 20 * * 5"  # Run at 8 PM on Fridays
  time_zone = "Asia/Tokyo"
  region    = var.region

  http_target {
    uri         = "${google_cloud_run_service.api.status[0].url}/tasks/fetch-papers"
    http_method = "POST"
  }

  depends_on = [google_cloud_run_service.api]
}