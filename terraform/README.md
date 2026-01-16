# Boreas Azure Infrastructure as Code

Professional Terraform configuration for deploying the Boreas application to Azure with:
- DuckDB database in Azure Blob Storage
- Streamlit dashboard on Azure App Service
- dlt and dbt pipelines running in GitHub Actions CI/CD

## Prerequisites

1. **Azure Account** - Active Azure subscription
2. **Terraform** - v1.5+
3. **Azure CLI** - Installed and authenticated (`az login`)
4. **GitHub Repository** - With secrets configured (see GitHub Actions Setup)

## Setup Instructions

### 1. Azure CLI Authentication

```bash
az login
az account set --subscription "YOUR_SUBSCRIPTION_ID"
```

### 2. Terraform Variables

Create `terraform.tfvars` in this directory:

```hcl
# terraform.tfvars
environment              = "prod"
location                 = "northeurope"
resource_group_name      = "rg-boreas-prod"
storage_account_name     = "storageboreasXXXX"  # Must be globally unique, lowercase
app_service_plan_name    = "asp-boreas-prod"
app_service_name         = "app-boreas-prod"
github_org               = "YOUR_GITHUB_ORG"
github_repo              = "Boreas"
```

### 3. Deploy Infrastructure

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### 4. Configure GitHub Actions Secrets

After Terraform deployment completes, add these secrets to your GitHub repository (Settings > Secrets and variables > Actions):

```
AZURE_SUBSCRIPTION_ID    # From Azure Portal
AZURE_TENANT_ID          # From Azure Portal
AZURE_CLIENT_ID          # Created by Terraform
AZURE_CLIENT_SECRET      # Created by Terraform
AZURE_STORAGE_ACCOUNT    # From Terraform output
AZURE_STORAGE_CONTAINER  # From Terraform output
AZURE_STORAGE_KEY        # From Terraform output
```

Get these values from Terraform outputs:
```bash
terraform output -json
```

### 5. Configure Streamlit App

The Streamlit app needs to be deployed to App Service. Create a deployment workflow in `.github/workflows/deploy-streamlit.yml`:

```yaml
name: Deploy Streamlit to Azure

on:
  push:
    branches: [main]
    paths:
      - 'dashboard/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Deploy to App Service
        uses: azure/webapps-deploy@v2
        with:
          app-name: app-boreas-prod
          package: dashboard
          publish-profile: ${{ secrets.AZURE_PUBLISH_PROFILE }}
```

### 6. GitHub Actions for dlt & dbt

Create `.github/workflows/run-pipelines.yml`:

```yaml
name: Run dlt and dbt Pipelines

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:

jobs:
  run-pipelines:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          pip install -r dlt/requirements.txt
          pip install dbt-duckdb
      
      - name: Configure dlt
        env:
          AZURE_STORAGE_ACCOUNT: ${{ secrets.AZURE_STORAGE_ACCOUNT }}
          AZURE_STORAGE_KEY: ${{ secrets.AZURE_STORAGE_KEY }}
          AZURE_STORAGE_CONTAINER: ${{ secrets.AZURE_STORAGE_CONTAINER }}
        run: |
          mkdir -p ~/.dlt
          cat > ~/.dlt/config.toml << EOF
          [runtime]
          log_level = "INFO"
          [destinations.duckdb]
          database = "/tmp/boreas.duckdb"
          [sources]
          # ... your dlt config
          EOF
      
      - name: Run dlt Pipelines
        run: cd dlt && python run_dlt_pipelines.py
      
      - name: Upload DuckDB to Blob Storage
        run: |
          az storage blob upload \
            --account-name ${{ secrets.AZURE_STORAGE_ACCOUNT }} \
            --account-key ${{ secrets.AZURE_STORAGE_KEY }} \
            --container-name ${{ secrets.AZURE_STORAGE_CONTAINER }} \
            --name boreas.duckdb \
            --file /tmp/boreas.duckdb \
            --overwrite
      
      - name: Run dbt
        run: cd dbt_boreas && dbt run
```

### 7. Update Application Config

Update your DuckDB connection string in the Streamlit app to use Blob Storage:

```python
# dashboard/app.py
import os
import duckdb

@st.cache_resource
def get_db_connection():
    # Download DuckDB from Blob Storage
    storage_account = os.getenv('AZURE_STORAGE_ACCOUNT')
    container = os.getenv('AZURE_STORAGE_CONTAINER')
    storage_key = os.getenv('AZURE_STORAGE_KEY')
    
    # Use DuckDB's S3/Azure extension if needed
    # Or cache the DB locally and sync periodically
    conn_string = f"./boreas.duckdb"
    return duckdb.connect(conn_string, read_only=True)
```

## Terraform Files Overview

- **main.tf** - Core Azure resources (Storage, App Service, Key Vault)
- **variables.tf** - Input variables with defaults
- **outputs.tf** - Output values for GitHub Actions setup
- **github.tf** - GitHub Actions OIDC configuration

## Monitoring & Debugging

### View App Service Logs
```bash
az webapp log tail --name app-boreas-prod --resource-group rg-boreas-prod
```

### Check Storage Blob
```bash
az storage blob list \
  --account-name storageboreasXXXX \
  --container-name duckdb \
  --account-key YOUR_KEY
```

### Destroy All Resources
```bash
terraform destroy
```

## Cost Optimization

- **Storage**: LRS redundancy (lowest cost)
- **App Service**: B1 tier (lowest tier, suitable for dashboards)
- **Schedule dlt/dbt**: Run once daily instead of continuous
- **Cleanup old blobs**: Set blob retention policy

## Security Best Practices

1. ✅ Managed Identity for GitHub Actions (no service principal secrets)
2. ✅ Key Vault for sensitive data
3. ✅ Private Storage Account access (recommended)
4. ✅ Network Security Groups for App Service
5. ✅ Encryption at rest for all storage

## Troubleshooting

### DuckDB Connection Issues
- Ensure DuckDB is in correct blob location
- Check storage account firewall rules
- Verify SAS token hasn't expired

### GitHub Actions Fails
- Check Azure credentials in secrets
- Verify OIDC federation is configured
- Review App Service deployment slots

### Performance Issues
- Increase App Service tier (B2, B3)
- Enable caching in Streamlit
- Consider cosmosdb for faster queries

## Support

For issues, check:
1. Terraform state: `terraform state list`
2. Azure Portal resource status
3. GitHub Actions logs
4. Application logs: `az webapp log tail`
