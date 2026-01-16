terraform {
  required_version = ">= 1.5"
  
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.80"
    }
    github = {
      source  = "integrations/github"
      version = "~> 5.42"
    }
  }

  backend "local" {
    path = "terraform.tfstate"
  }
  
  # Uncomment for remote state in Azure Storage
  # backend "azurerm" {
  #   resource_group_name  = "rg-terraform-state"
  #   storage_account_name = "saterraformstate"
  #   container_name       = "tfstate"
  #   key                  = "boreas/terraform.tfstate"
  # }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
  }
}

provider "github" {
  owner = var.github_org
  token = var.github_token
}
