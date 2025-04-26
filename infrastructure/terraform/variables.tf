variable "project_id" {
  description = "Google Cloud プロジェクトID"
  type        = string
  default     = "433235895318" # Your actual GCP project ID
}

variable "region" {
  description = "デプロイするリージョン"
  type        = string
  default     = "asia-northeast1" # 東京リージョン
}

variable "zone" {
  description = "デプロイするゾーン"
  type        = string
  default     = "asia-northeast1-a" # 東京リージョンのゾーン
}

variable "gemini_api_key" {
  description = "Gemini API Key - will be provided by GitHub Actions secrets"
  type        = string
  sensitive   = true
  # No default value as this will be provided by GitHub Actions
}