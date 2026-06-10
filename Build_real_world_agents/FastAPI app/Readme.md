# FastAPI RAG Service (Company Policy)

This folder now runs a FastAPI-based RAG service over `company_policy.md`.

## What Changed

- Converted the previous CLI script into a FastAPI app.
- Added startup ingestion of the policy file into ChromaDB.
- Added an AG-UI SSE endpoint for chat clients plus a JSON chat fallback endpoint.
- Switched the policy file path to a relative path so it works locally and in containers.

## Files Updated

- `maf-rag.py`
- `requirements.txt`
- `Readme.md` (this file)

## Requirements

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run Locally

From this folder:

```powershell
python maf-rag.py
```

Alternative:

```powershell
uvicorn --app-dir . maf-rag:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Health

- Method: `GET`
- URL: `/health`
- Response:

```json
{
  "status": "ok"
}
```

### Chat (AG-UI)

- Method: `POST`
- URL: `/chat`
- Protocol: Server-Sent Events for `AGUIChatClient`.

### Chat (JSON fallback)

- Method: `POST`
- URL: `/chat-json`
- Body:

```json
{
  "question": "How many annual leave days are employees entitled to?"
}
```

- Response:

```json
{
  "answer": "..."
}
```

## Environment

The app uses `FoundryChatClient` with `DefaultAzureCredential`.
Set the same Azure/Foundry environment variables you use today for local execution.

For the sample client in this folder, set `AGUI_SERVER_URL` to `http://127.0.0.1:8000/chat`.

## Container Notes

This FastAPI layout is container-ready.
This repo includes `Dockerfile`, `.dockerignore`, and `docker-compose.yml` so you can run:

```powershell
docker build -t maf-rag-fastapi .
docker run -p 8000:8000 maf-rag-fastapi
```

## Docker Files Created (3 Files)

1. `Dockerfile`
  Builds the FastAPI image using Python 3.11-slim, installs dependencies from `requirements.txt`, copies app code, and starts Uvicorn on port 8000.

2. `.dockerignore`
  Excludes local-only and sensitive files from image build context (for example `.venv`, `.env`, logs, and git metadata) to keep images smaller and safer.

3. `docker-compose.yml`
  Defines one service (`api`) that builds from the local `Dockerfile`, loads env vars from `.env`, and maps port `8000:8000` for local container runs.

## Run As A Docker Container

Build and run:

```powershell
docker build -t maf-rag-fastapi .
docker run --env-file .env -p 8000:8000 maf-rag-fastapi
```

Test:

```powershell
curl http://127.0.0.1:8000/health
```

Optional with Docker Compose:

```powershell
docker compose up --build
```

## Deploy To Azure Container Apps

For a dedicated, production-friendly, step-by-step deployment runbook, see:

`DEPLOY_CONTAINER_APP.md`

Prerequisites:

- Azure CLI logged in (`az login`)
- Docker installed
- Resource group and Container Apps environment in your subscription

Example end-to-end commands:

```powershell
# 1) Variables
$RESOURCE_GROUP = "rg-maf-rag"
$LOCATION = "canadacentral"
$ACR_NAME = "mafragacr"
$ACA_ENV = "mafrag-env"
$APP_NAME = "maf-rag-api"
$IMAGE = "$ACR_NAME.azurecr.io/maf-rag-fastapi:latest"

# 2) Create infra (one-time)
az group create --name $RESOURCE_GROUP --location $LOCATION
az acr create --name $ACR_NAME --resource-group $RESOURCE_GROUP --sku Basic
az containerapp env create --name $ACA_ENV --resource-group $RESOURCE_GROUP --location $LOCATION

# 3) Build image in ACR
az acr build --registry $ACR_NAME --image maf-rag-fastapi:latest .

# 4) Deploy Container App
az containerapp create `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --environment $ACA_ENV `
  --image $IMAGE `
  --target-port 8000 `
  --ingress external `
  --registry-server "$ACR_NAME.azurecr.io" `
  --query properties.configuration.ingress.fqdn
```

Set runtime environment variables (replace values appropriately):

```powershell
az containerapp update `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --set-env-vars `
    FOUNDRY_MODEL="grok-4.3" `
    FOUNDRY_PROJECT_ENDPOINT="https://obs-test-resource-resource.services.ai.azure.com/api/projects/obs-test-resource" `
    AZURE_TENANT_ID="<tenant-id>" `
    AZURE_CLIENT_ID="<app-client-id>" `
    AZURE_CLIENT_SECRET="<app-client-secret>"
```

## Managed Identity (Recommended For Azure)

Instead of storing `AZURE_CLIENT_SECRET`, use a system-assigned managed identity on the Container App.

1. Enable managed identity on your app:

```powershell
az containerapp identity assign `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --system-assigned
```

2. Grant that identity permission to call your Foundry/AI resource (least privilege role for model inference in your environment).

3. Remove secret-based auth vars from your app settings:

```powershell
az containerapp update `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --remove-env-vars AZURE_CLIENT_SECRET
```

4. Keep only non-secret runtime vars:

```powershell
az containerapp update `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --set-env-vars `
    FOUNDRY_MODEL="grok-4.3" `
    FOUNDRY_PROJECT_ENDPOINT="https://obs-test-resource-resource.services.ai.azure.com/api/projects/obs-test-resource"
```

Because this app uses `DefaultAzureCredential`, it will automatically use the managed identity inside Azure Container Apps.

Then get the app URL:

```powershell
az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv
```

For AG-UI clients, set `AGUI_SERVER_URL` to:

`https://<your-container-app-fqdn>/chat`
