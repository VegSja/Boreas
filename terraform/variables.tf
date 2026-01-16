variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "northeurope"
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "rg-boreas-prod"
}

variable "storage_account_name" {
  description = "Name of the storage account (must be globally unique, lowercase)"
  type        = string
  validation {
    condition     = can(regex("^[a-z0-9]{3,24}$", var.storage_account_name))
    error_message = "Storage account name must be 3-24 lowercase alphanumeric characters."
  }
}

variable "app_service_plan_name" {
  description = "Name of the App Service Plan"
  type        = string
  default     = "asp-boreas-prod"
}

variable "app_service_name" {
  description = "Name of the App Service"
  type        = string
  default     = "app-boreas-prod"
}

variable "app_service_sku" {
  description = "SKU for App Service (B1=Basic, S1=Standard)"
  type        = string
  default     = "B1"
  
  validation {
    condition     = contains(["B1", "B2", "B3", "S1", "S2", "S3"], var.app_service_sku)
    error_message = "App Service SKU must be B1, B2, B3, S1, S2, or S3."
  }
}

variable "github_org" {
  description = "GitHub organization name"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "Boreas"
}

variable "github_token" {
  description = "GitHub personal access token (set via environment variable TF_VAR_github_token)"
  type        = string
  sensitive   = true
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "Boreas"
    Environment = "prod"
    ManagedBy   = "Terraform"
  }
}
