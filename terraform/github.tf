# GitHub OIDC Provider for federated authentication
resource "azurerm_federated_identity_credential" "github_actions" {
  name                = "github-actions-boreas"
  resource_group_name = azurerm_resource_group.main.name
  audience            = ["api://AzureADTokenExchange"]
  issuer              = "https://token.actions.githubusercontent.com"
  subject             = "repo:${var.github_org}/${var.github_repo}:ref:refs/heads/main"
  parent_id           = azurerm_user_assigned_identity.github_actions.id
}

# User Assigned Identity for GitHub Actions
resource "azurerm_user_assigned_identity" "github_actions" {
  name                = "id-github-actions-boreas"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = var.tags
}

# Grant GitHub Actions permissions to Storage
resource "azurerm_role_assignment" "github_storage" {
  scope              = azurerm_storage_account.main.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id       = azurerm_user_assigned_identity.github_actions.principal_id
}

# Grant GitHub Actions permissions to Key Vault
resource "azurerm_role_assignment" "github_keyvault" {
  scope              = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id       = azurerm_user_assigned_identity.github_actions.principal_id
}

# GitHub Repository Secret - Azure Credentials JSON
resource "github_actions_secret" "azure_credentials" {
  repository       = var.github_repo
  secret_name      = "AZURE_CREDENTIALS"
  plaintext_value = jsonencode({
    clientId       = azurerm_user_assigned_identity.github_actions.client_id
    subscriptionId = data.azurerm_client_config.current.subscription_id
    tenantId       = data.azurerm_client_config.current.tenant_id
    type           = "oidc"
  })
}

# GitHub Secrets for pipeline configuration
resource "github_actions_secret" "azure_subscription_id" {
  repository       = var.github_repo
  secret_name      = "AZURE_SUBSCRIPTION_ID"
  plaintext_value = data.azurerm_client_config.current.subscription_id
}

resource "github_actions_secret" "azure_tenant_id" {
  repository       = var.github_repo
  secret_name      = "AZURE_TENANT_ID"
  plaintext_value = data.azurerm_client_config.current.tenant_id
}

resource "github_actions_secret" "azure_client_id" {
  repository       = var.github_repo
  secret_name      = "AZURE_CLIENT_ID"
  plaintext_value = azurerm_user_assigned_identity.github_actions.client_id
}

resource "github_actions_secret" "azure_storage_account" {
  repository       = var.github_repo
  secret_name      = "AZURE_STORAGE_ACCOUNT"
  plaintext_value = azurerm_storage_account.main.name
}

resource "github_actions_secret" "azure_storage_container" {
  repository       = var.github_repo
  secret_name      = "AZURE_STORAGE_CONTAINER"
  plaintext_value = azurerm_storage_container.duckdb.name
}

resource "github_actions_secret" "azure_storage_key" {
  repository       = var.github_repo
  secret_name      = "AZURE_STORAGE_KEY"
  plaintext_value = azurerm_storage_account.main.primary_access_key
}
