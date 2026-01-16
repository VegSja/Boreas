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
  default_to_oauth_authentication = false

  tags = var.tags
}

# Storage Container for DuckDB
resource "azurerm_storage_container" "duckdb" {
  name                  = "duckdb"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

# Key Vault for Secrets
resource "azurerm_key_vault" "main" {
  name                            = "kv-boreas-${substr(azurerm_resource_group.main.id, -8, -1)}"
  location                        = azurerm_resource_group.main.location
  resource_group_name             = azurerm_resource_group.main.name
  tenant_id                       = data.azurerm_client_config.current.tenant_id
  sku_name                        = "standard"
  soft_delete_retention_days      = 7
  enabled_for_disk_encryption     = false
  enabled_for_template_deployment = true
  purge_protection_enabled        = false

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    key_permissions = [
      "Get",
      "List",
      "Create",
      "Delete",
    ]

    secret_permissions = [
      "Get",
      "List",
      "Set",
      "Delete",
    ]
  }

  tags = var.tags
}

# Store Storage Account Key in Key Vault
resource "azurerm_key_vault_secret" "storage_key" {
  name         = "storage-account-key"
  value        = azurerm_storage_account.main.primary_access_key
  key_vault_id = azurerm_key_vault.main.id
}

# App Service Plan
resource "azurerm_service_plan" "main" {
  name                = var.app_service_plan_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  sku_name            = var.app_service_sku

  tags = var.tags
}

# App Service for Streamlit
resource "azurerm_linux_web_app" "main" {
  name                = var.app_service_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.main.id

  https_only = true

  app_settings = {
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = false
    DOCKER_REGISTRY_SERVER_URL          = "https://index.docker.io"
    WEBSITE_HEALTHCHECK_PATH            = "/"
  }

  site_config {
    minimum_tls_version       = "1.2"
    remote_debugging_enabled  = false
    
    app_command_line = "streamlit run dashboard/app.py --server.port 8000 --server.address 0.0.0.0"
    
    application_stack {
      docker_image_name   = "ghcr.io/${var.github_org}/boreas:latest"
      docker_registry_url = "https://ghcr.io"
    }
  }

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# Allow App Service to read from storage
resource "azurerm_role_assignment" "app_storage_read" {
  scope              = azurerm_storage_account.main.id
  role_definition_name = "Storage Blob Data Reader"
  principal_id       = azurerm_linux_web_app.main.identity[0].principal_id
}

# Data source for current Azure context
data "azurerm_client_config" "current" {}
