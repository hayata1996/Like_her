provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Secret Manager for storing sensitive data - just create the secret without initial value
resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "gemini-api-key"
  
  replication {
    user_managed {
      replicas {
        location = "us-central1"
      }
    }
  }
}

# Create a secret version with the Gemini API key
resource "google_secret_manager_secret_version" "gemini_api_key_version" {
  secret      = google_secret_manager_secret.gemini_api_key.id
  secret_data = var.gemini_api_key
}

# Allow Cloud Run service to access the secret
resource "google_secret_manager_secret_iam_member" "api_gemini_access" {
  secret_id = google_secret_manager_secret.gemini_api_key.id
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

        env {
          name = "GEMINI_API_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.gemini_api_key.secret_id
              key  = "latest"
            }
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
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

# Cloud Scheduler for scheduled tasks
resource "google_cloud_scheduler_job" "daily_news_job" {
  name      = "daily-ai-news-job"
  schedule  = "0 3 * * *"  # Run at 3 AM daily
  time_zone = "Asia/Tokyo"

  http_target {
    uri         = "${google_cloud_run_service.api.status[0].url}/tasks/fetch-news"
    http_method = "POST"
  }
}

resource "google_cloud_scheduler_job" "weekly_papers_job" {
  name      = "weekly-papers-job"
  schedule  = "0 20 * * 5"  # Run at 8 PM on Fridays
  time_zone = "Asia/Tokyo"

  http_target {
    uri         = "${google_cloud_run_service.api.status[0].url}/tasks/fetch-papers"
    http_method = "POST"
  }
}

# BigQuery dataset for data storage
resource "google_bigquery_dataset" "like_her_dataset" {
  dataset_id    = "like_her_dataset"
  friendly_name = "Like Her Dataset"
  location      = "asia-northeast1"
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
}