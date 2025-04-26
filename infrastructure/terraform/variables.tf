variable "project_id" {
  description = "Google Cloud プロジェクトID"
  type        = string
  default     = "like-her-project" # Please replace with your actual GCP project ID before deployment
}

variable "region" {
  description = "Google Cloud region"
  type        = string
  default     = "asia-northeast1"  # Tokyo region
}

variable "zone" {
  description = "Google Cloud zone"
  type        = string
  default     = "asia-northeast1-a"
}