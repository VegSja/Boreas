# Boreas Azure Infrastructure as Code

Terraform configuration for deploying the Boreas data platform infrastructure to Azure:

- **Azure Storage Account** - Blob storage for DuckDB database
- **Azure Key Vault** - Secure storage for secrets and access keys
- **GitHub Actions OIDC** - Passwordless authentication for CI/CD pipelines
- **Service Principal** - For DuckDB Azure extension access

> **Note:** App Service deployment is currently commented out. The Streamlit dashboard can be deployed separately when needed.

## Files Overview

| File | Description |
|------|-------------|
| `main.tf` | Core infrastructure resources |
| `variables.tf` | Input variable definitions |
| `outputs.tf` | Output values (secrets for GitHub) |
| `versions.tf` | Provider version constraints |
| `terraform.tfvars.example` | Example variable values |
| `github-workflows-pipelines.yml` | Template for dlt/dbt CI/CD workflow |
| `github-workflows-streamlit.yml` | Template for Streamlit deployment workflow |

## Prerequisites

1. **Azure Account** - Active Azure subscription
2. **Terraform** - v1.5+
3. **Azure CLI** - Installed and authenticated (`az login`)
4. **GitHub Repository** - For OIDC federated credentials

## Setup Instructions

### 1. Azure CLI Authentication

```bash
az login
az account set --subscription "YOUR_SUBSCRIPTION_ID"
```

### 2. Configure Variables

Copy the example file and customize:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
environment          = "prod"
location             = "northeurope"
resource_group_name  = "rg-boreas-prod"
storage_account_name = "storageboreasXXXX"  # Must be globally unique, 3-24 lowercase alphanumeric
github_org           = "YOUR_GITHUB_ORG"
github_repo          = "Boreas"
```

### 3. Deploy Infrastructure

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### 4. Configure GitHub Actions Secrets

After deployment, add these secrets to your GitHub repository (Settings → Secrets and variables → Actions).

**For GitHub Actions OIDC Authentication:**
```
AZURE_CLIENT_ID         # terraform output github_actions_client_id
AZURE_TENANT_ID         # terraform output github_actions_tenant_id
AZURE_SUBSCRIPTION_ID   # terraform output github_actions_subscription_id
```

**For DuckDB Azure Extension (Service Principal):**
```
DUCKDB_AZURE_TENANT_ID      # terraform output duckdb_tenant_id
DUCKDB_AZURE_CLIENT_ID      # terraform output duckdb_client_id
DUCKDB_AZURE_CLIENT_SECRET  # terraform output -raw duckdb_client_secret
```

**For Storage Access:**
```
AZURE_STORAGE_ACCOUNT    # terraform output storage_account_name
AZURE_STORAGE_CONTAINER  # terraform output storage_container_name (= "duckdb")
```

Get all outputs:
```bash
terraform output
terraform output -raw duckdb_client_secret  # For sensitive values
```

### 5. Set Up GitHub Actions Workflows

Copy the workflow templates to your repository:

```bash
mkdir -p ../.github/workflows
cp github-workflows-pipelines.yml ../.github/workflows/pipelines.yml
cp github-workflows-streamlit.yml ../.github/workflows/deploy-streamlit.yml
```

Review and customize the workflows as needed.

## Resources Created

| Resource | Description |
|----------|-------------|
| `azurerm_resource_group` | Resource group for all Boreas resources |
| `azurerm_storage_account` | Storage account with LRS redundancy |
| `azurerm_storage_container` | Private container named "duckdb" |
| `azurerm_key_vault` | Key Vault for storing secrets |
| `azurerm_user_assigned_identity` | Managed identity for GitHub Actions OIDC |
| `azurerm_federated_identity_credential` | OIDC federation for passwordless CI/CD |
| `azuread_application` | Azure AD app for DuckDB service principal |
| `azuread_service_principal` | Service principal for DuckDB Azure extension |

## Useful Commands

### Check Storage Blob
```bash
az storage blob list \
  --account-name YOUR_STORAGE_ACCOUNT \
  --container-name duckdb \
  --auth-mode login
```

### View Key Vault Secrets
```bash
az keyvault secret list --vault-name YOUR_KEYVAULT_NAME
```

### Destroy All Resources
```bash
terraform destroy
```

## Security Notes

- **OIDC Authentication**: GitHub Actions uses federated identity credentials (no long-lived secrets)
- **Key Vault**: Storage keys and DuckDB client secret stored securely
- **Service Principal**: DuckDB access uses a dedicated service principal with 1-year credential rotation
- **Storage**: Private container access, HTTPS-only, TLS 1.2 minimum

## Troubleshooting

### GitHub Actions OIDC Fails
- Verify the `subject` in federated credential matches your branch (default: `refs/heads/main`)
- Check that the GitHub org/repo variables are correct
- Ensure `id-token: write` permission is set in workflow

### DuckDB Connection Issues
- Verify service principal credentials are correct
- Check storage account firewall rules allow access
- Ensure container "duckdb" exists

### Terraform State
- State is stored locally by default (`terraform.tfstate`)
- For team use, uncomment the remote backend in `versions.tf`


## Support

For issues, check:
1. Terraform state: `terraform state list`
2. Azure Portal resource status
3. GitHub Actions logs
4. Application logs: `az webapp log tail`
