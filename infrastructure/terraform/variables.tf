variable "project_id" {
  description = "Google Cloud プロジェクトID"
  type        = string
  default     = "like-her-project" # ここに実際のプロジェクトIDを入力してください
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