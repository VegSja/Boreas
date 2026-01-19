output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "storage_account_name" {
  description = "Name of the storage account"
  value       = azurerm_storage_account.main.name
}

output "storage_container_name" {
  description = "Name of the DuckDB blob container"
  value       = azurerm_storage_container.duckdb.name
}

# GitHub Actions OIDC Secrets
output "github_actions_client_id" {
  description = "AZURE_CLIENT_ID - Add as GitHub Actions secret"
  value       = azurerm_user_assigned_identity.github_actions.client_id
}

output "github_actions_tenant_id" {
  description = "AZURE_TENANT_ID - Add as GitHub Actions secret"
  value       = data.azurerm_client_config.current.tenant_id
}

output "github_actions_subscription_id" {
  description = "AZURE_SUBSCRIPTION_ID - Add as GitHub Actions secret"
  value       = data.azurerm_client_config.current.subscription_id
}

# Storage key for DuckDB Azure extension (if using key-based auth)
output "storage_account_key" {
  description = "Storage account primary key for DuckDB access"
  value       = azurerm_storage_account.main.primary_access_key
  sensitive   = true
}