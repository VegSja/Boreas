output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "storage_account_name" {
  description = "Name of the storage account"
  value       = azurerm_storage_account.main.name
}

output "storage_account_id" {
  description = "ID of the storage account"
  value       = azurerm_storage_account.main.id
}

output "storage_container_name" {
  description = "Name of the DuckDB blob container"
  value       = azurerm_storage_container.duckdb.name
}

output "app_service_name" {
  description = "Name of the App Service"
  value       = azurerm_linux_web_app.main.name
}

output "app_service_url" {
  description = "URL of the Streamlit application"
  value       = "https://${azurerm_linux_web_app.main.default_hostname}"
}

output "app_service_default_hostname" {
  description = "Default hostname of the App Service"
  value       = azurerm_linux_web_app.main.default_hostname
}

output "key_vault_id" {
  description = "ID of the Key Vault"
  value       = azurerm_key_vault.main.id
}

output "key_vault_name" {
  description = "Name of the Key Vault"
  value       = azurerm_key_vault.main.name
}

output "github_actions_client_id" {
  description = "Client ID for GitHub Actions OIDC"
  value       = azurerm_user_assigned_identity.github_actions.client_id
}

output "github_actions_setup_complete" {
  description = "GitHub Actions secrets have been configured"
  value       = "Check your GitHub repository secrets for AZURE_* variables"
}

output "next_steps" {
  description = "Instructions for next steps"
  value = <<-EOT
    1. Retrieve terraform outputs: terraform output -json
    2. Check GitHub repository for new Action secrets
    3. Build and push Docker image to GitHub Container Registry:
       docker build -t ghcr.io/${var.github_org}/boreas:latest .
       docker push ghcr.io/${var.github_org}/boreas:latest
    4. Create GitHub workflow files:
       - .github/workflows/deploy-streamlit.yml
       - .github/workflows/run-pipelines.yml
    5. Access Streamlit: ${azurerm_linux_web_app.main.default_hostname}
  EOT
}
