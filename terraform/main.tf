# Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

# Storage Account for DuckDB
resource "azurerm_storage_account" "main" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  
  https_traffic_only_enabled       = true
  min_tls_version                  = "TLS1_2"
  shared_access_key_enabled        = true
  default_to_oauth_authentication  = false

  tags = var.tags
}

# Storage Container for DuckDB
resource "azurerm_storage_container" "duckdb" {
  name                  = "duckdb"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

# Data source for current Azure context
data "azurerm_client_config" "current" {}

# ============================================
# GitHub Actions OIDC Authentication
# ============================================

# User Assigned Identity for GitHub Actions
resource "azurerm_user_assigned_identity" "github_actions" {
  name                = "id-github-actions-boreas"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = var.tags
}

# Federated credential for GitHub Actions OIDC
resource "azurerm_federated_identity_credential" "github_actions" {
  name                = "github-actions-boreas"
  resource_group_name = azurerm_resource_group.main.name
  audience            = ["api://AzureADTokenExchange"]
  issuer              = "https://token.actions.githubusercontent.com"
  subject             = "repo:${var.github_org}/${var.github_repo}:ref:refs/heads/master"
  parent_id           = azurerm_user_assigned_identity.github_actions.id
}

# Grant GitHub Actions permissions to Storage Account
resource "azurerm_role_assignment" "github_storage" {
  scope                = azurerm_storage_account.main.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_user_assigned_identity.github_actions.principal_id
}