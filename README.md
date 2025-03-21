# Azure VNET API with Authentication

This FastAPI application allows you to create and retrieve Azure Virtual Networks (VNETs) securely using Azure AD authentication.

## Prerequisites
- Azure Subscription
- Azure AD App Registration (Client ID, Tenant ID, Client Secret)
- Azure Resource Group
- Python 3.10 or later
- FastAPI and Azure SDK for Python installed

## Setup Instructions
### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Add Environment Variables
Create a `.env` file and add the following details:
```
AZURE_TENANT_ID=<your-tenant-id>
AZURE_CLIENT_ID=<your-client-id>
AZURE_CLIENT_SECRET=<your-client-secret>
AZURE_SUBSCRIPTION_ID=<your-subscription-id>
AZURE_RESOURCE_GROUP=<your-resource-group>
```

### 4. Run the Application Locally
```bash
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. Generate Access Token (Required for API Calls)
Use the following command to generate an authentication token:
```bash
curl -X POST -H "Content-Type: application/x-www-form-urlencoded" \
-d 'client_id=<your-client-id>&scope=api://<your-api-id>/.default&client_secret=<your-client-secret>&grant_type=client_credentials' \
https://login.microsoftonline.com/<your-tenant-id>/oauth2/v2.0/token
```
Copy the generated `access_token` for use in API requests.

### 6. Deploy to Azure Web App using GitHub Actions
1. Create an Azure Web App.
2. In the Azure Portal, go to **Deployment Center**.
3. Select **GitHub** as your source.
4. Follow the steps to connect your repository and set the branch.
5. Add the environment variables in your Web App's **Environment variables**.
6. Configure the **Startup Command** in **Configuration** settings.
```bash
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py && pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 8000
```

### 7. API Endpoints
#### Create VNET
**POST** `/vnet/`
**Body:**
```bash
curl -L -X POST "https://<your-webapp-name>.azurewebsites.net/vnet/" \
-H "Authorization: Bearer <Access_Token>" \
-H "Content-Type: application/json" \
-d '{
    "vnet_name": "TestVNET",
    "location": "eastus2",
    "address_space": ["10.4.0.0/16"],
    "subnets": [
        {"name": "subnet1", "address_prefix": "10.4.1.0/24"},
        {"name": "subnet2", "address_prefix": "10.4.2.0/24"}
    ]
}'
```

#### Get VNET
**GET** `/vnet/{vnet_name}`
**Body:**
```bash
curl -X GET "https://<your-webapp-name>.azurewebsites.net/vnet/TestVNET" \
-H "Authorization: Bearer <Access_Token>"
```
For additional support, feel free to raise an issue in the repository.

