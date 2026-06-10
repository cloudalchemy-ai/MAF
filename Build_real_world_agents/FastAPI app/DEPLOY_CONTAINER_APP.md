# Deploy FastAPI RAG to Azure Container Apps

This guide is a clean, end-to-end deployment path for this project.
It is written so a new user can deploy without guessing.

## What this deploys

- One Azure Container Registry (ACR)
- One Azure Container Apps Environment
- One Azure Container App running this API
- Foundry runtime configuration via environment variables
- Required RBAC so FoundryChatClient can call the model

## Prerequisites

- Azure CLI installed
- Docker installed (only needed for local container testing)
- Access to an Azure subscription
- A Foundry/AI Services resource with a deployed model
- You are in this folder before running commands

PowerShell:

```powershell
Set-Location "D:\Kshitij\MAF\V1\Build_real_world_agents\FastAPI app"
az login
```

## 1) Set deployment variables

Update only values in quotes.

```powershell
$SUBSCRIPTION_ID = "<your-subscription-id>"
$RESOURCE_GROUP = "rg-maf-rag"
$LOCATION = "canadacentral"

$ACR_NAME = "mafragacr"
$ACA_ENV = "mafrag-env"
$APP_NAME = "maf-rag-api"
$IMAGE_NAME = "maf-rag-fastapi"
$IMAGE_TAG = "v1"
$IMAGE = "$ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG"

$FOUNDRY_PROJECT_ENDPOINT = "https://obs-test-resource-resource.services.ai.azure.com/api/projects/obs-test-resource"
$FOUNDRY_MODEL = "grok-4.3"

# Scope where RBAC is applied (AI Services account scope)
$FOUNDRY_SCOPE = "/subscriptions/<your-subscription-id>/resourceGroups/Obs-resource-group/providers/Microsoft.CognitiveServices/accounts/obs-test-resource-resource"

az account set --subscription $SUBSCRIPTION_ID
```

## 2) Create infrastructure (one time)

```powershell
az group create --name $RESOURCE_GROUP --location $LOCATION
az acr create --name $ACR_NAME --resource-group $RESOURCE_GROUP --sku Basic
az containerapp env create --name $ACA_ENV --resource-group $RESOURCE_GROUP --location $LOCATION
```

## 3) Build and push image with ACR build

Run from the project folder.

```powershell
az acr build --registry $ACR_NAME --image "$IMAGE_NAME:$IMAGE_TAG" .
```

## 4) Create the Container App

```powershell
az containerapp create `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --environment $ACA_ENV `
  --image $IMAGE `
  --target-port 8000 `
  --ingress external `
  --registry-server "$ACR_NAME.azurecr.io"
```

## 5) Configure app settings for Foundry

### Option A (recommended): Managed Identity

1. Enable system-assigned identity:

```powershell
az containerapp identity assign --name $APP_NAME --resource-group $RESOURCE_GROUP --system-assigned
```

2. Get principal id:

```powershell
$PRINCIPAL_ID = az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query identity.principalId -o tsv
$PRINCIPAL_ID
```

3. Grant role(s) at the AI Services scope:

```powershell
az role assignment create --assignee-object-id $PRINCIPAL_ID --assignee-principal-type ServicePrincipal --role "Cognitive Services OpenAI User" --scope $FOUNDRY_SCOPE
```

If you still see 403 after propagation, add one fallback role:

```powershell
az role assignment create --assignee-object-id $PRINCIPAL_ID --assignee-principal-type ServicePrincipal --role "Azure AI Developer" --scope $FOUNDRY_SCOPE
```

4. Set non-secret env vars only:

```powershell
az containerapp update `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --set-env-vars `
    FOUNDRY_MODEL="$FOUNDRY_MODEL" `
    FOUNDRY_PROJECT_ENDPOINT="$FOUNDRY_PROJECT_ENDPOINT"
```

### Option B: Service Principal in env vars

Use this only if managed identity is not possible.

```powershell
$AZURE_TENANT_ID = "<tenant-id>"
$AZURE_CLIENT_ID = "<client-id>"
$AZURE_CLIENT_SECRET = "<client-secret>"

az containerapp update `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --set-env-vars `
    FOUNDRY_MODEL="$FOUNDRY_MODEL" `
    FOUNDRY_PROJECT_ENDPOINT="$FOUNDRY_PROJECT_ENDPOINT" `
    AZURE_TENANT_ID="$AZURE_TENANT_ID" `
    AZURE_CLIENT_ID="$AZURE_CLIENT_ID" `
    AZURE_CLIENT_SECRET="$AZURE_CLIENT_SECRET"
```

Then assign RBAC to that service principal object id on the same scope.

## 6) Get URL and verify health

```powershell
$FQDN = az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv
$BASE_URL = "https://$FQDN"
$BASE_URL

Invoke-RestMethod "$BASE_URL/health"
```

Expected response:

```json
{
  "status": "ok"
}
```

## 7) Verify chat endpoint

```powershell
$body = @{ question = 'How many annual leave days are employees entitled to?' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$BASE_URL/chat-json" -ContentType 'application/json' -Body $body | ConvertTo-Json -Depth 5
```

If successful, you should receive an answer field.

## 8) Configure local client to call deployed API

In .env:

```dotenv
AGUI_SERVER_URL="https://<your-fqdn>/chat"
```

Then run:

```powershell
python client.py
```

## 9) 403 troubleshooting playbook (important)

If logs show PermissionDeniedError 403 from FoundryChatClient:

1. Confirm the app identity actually used by DefaultAzureCredential.
- If AZURE_CLIENT_ID and AZURE_CLIENT_SECRET are set, service principal is used first.
- If not set, managed identity is used inside Container Apps.

2. Confirm role assignment scope is correct.
- Use the AI Services account scope that backs your Foundry project.

3. Confirm model deployment exists and name matches exactly.

```powershell
az cognitiveservices account deployment list --name obs-test-resource-resource --resource-group Obs-resource-group -o table
```

4. Wait 5 to 15 minutes for RBAC propagation, then retry.

5. If model-specific access is blocked, test with another deployed model to isolate entitlement issues.

## 10) Useful operations

View app logs:

```powershell
az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP --tail 100
```

Update to a new image tag:

```powershell
$IMAGE_TAG = "v2"
$IMAGE = "$ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG"
az acr build --registry $ACR_NAME --image "$IMAGE_NAME:$IMAGE_TAG" .
az containerapp update --name $APP_NAME --resource-group $RESOURCE_GROUP --image $IMAGE
```

## Final checklist

- Container app is externally reachable
- Health endpoint returns status ok
- Chat-json endpoint returns answer
- Foundry model and project endpoint are set
- Correct identity has RBAC on AI Services scope
- AGUI_SERVER_URL points to /chat on deployed app
