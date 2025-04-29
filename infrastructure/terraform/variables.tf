variable "project_id" {
  description = "Google Cloud プロジェクトID"
  type        = string
  default     = " " # Your actual GCP project ID
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
  default     = "placeholder-key" # Temporary placeholder until you get the real key
}

variable "agent_id" {
  description = "AI Builder Agent ID"
  type        = string
  default     = "placeholder-agent-id" # Temporary placeholder until you create an agent
}

variable "google_credentials" {
  description = "Google Cloud credentials JSON"
  type        = string
  sensitive   = true
}

variable "allowed_user_email" {
  description = "アクセスを許可するGoogleアカウントのメールアドレス"
  type        = string
  default     = "template@gmail.com" # あなたのGoogleアカウントのメールアドレスに変更してください
}