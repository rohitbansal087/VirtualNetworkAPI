from fastapi import FastAPI, HTTPException, Depends, status, Header
from pydantic import BaseModel, Field
from azure.identity import ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
import os
import requests

app = FastAPI()

# Load Azure credentials from environment variables
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP")

if not all([TENANT_ID, CLIENT_ID, CLIENT_SECRET, SUBSCRIPTION_ID, RESOURCE_GROUP]):
    raise RuntimeError("Missing Azure environment variables!")

# Azure Authentication using Client Credentials
credential = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
network_client = NetworkManagementClient(credential, SUBSCRIPTION_ID)


# Function to validate Bearer token
def validate_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid token")

    token = authorization.split("Bearer ")[1]
    return token  # In real case, validate token properly with Azure AD


# Request Models
class Subnet(BaseModel):
    name: str
    address_prefix: str = Field(default="10.0.1.0/24")


class VnetRequest(BaseModel):
    vnet_name: str
    location: str = Field(default="eastus2")
    address_space: list[str] = Field(default=["10.0.0.0/16"])
    subnets: list[Subnet] = Field(default=[{"name": "default-subnet", "address_prefix": "10.0.1.0/24"}])


# Create VNET (POST /vnet)
@app.post("/vnet")
async def create_vnet(vnet_data: VnetRequest, token: str = Depends(validate_token)):
    vnet_params = {
        "location": vnet_data.location,
        "address_space": {"address_prefixes": vnet_data.address_space},
        "subnets": [{"name": subnet.name, "address_prefix": subnet.address_prefix} for subnet in vnet_data.subnets]
    }

    try:
        vnet = network_client.virtual_networks.begin_create_or_update(
            RESOURCE_GROUP, vnet_data.vnet_name, vnet_params
        ).result()
        return {"message": "VNET created successfully", "vnet_id": vnet.id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Get VNET Details (GET /vnet/{vnet_name})
@app.get("/vnet/{vnet_name}")
async def get_vnet(vnet_name: str, token: str = Depends(validate_token)):
    try:
        vnet = network_client.virtual_networks.get(RESOURCE_GROUP, vnet_name)
        return {"vnet_name": vnet.name, "location": vnet.location, "address_space": vnet.address_space.address_prefixes}

    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
