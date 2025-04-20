variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
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