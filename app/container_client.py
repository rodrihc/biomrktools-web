from azure.storage.blob import ContainerClient, BlobServiceClient
import os
from dotenv import load_dotenv

load_dotenv()

AZURE_CONTAINER = os.getenv("AZURE_CONTAINER")
API_BASE = os.getenv("API_BASE")          # should be https://biomrktools02sa.blob.core.windows.net
DELTA_PATH = os.getenv("DELTA_PATH")      # e.g. biomrk_master/adeg/v_adeg_tcga_brca_001_limma_voom
SAS_TOKEN = os.getenv("SAS_TOKEN")

print(AZURE_CONTAINER)
print(API_BASE)
print(DELTA_PATH)
print(SAS_TOKEN)

# ✅ OPTION 1: ContainerClient directly
container_url = f"{API_BASE}/{AZURE_CONTAINER}?{SAS_TOKEN}"
container_client = ContainerClient.from_container_url(container_url)

print("Listing blobs via ContainerClient:")
for blob in container_client.list_blobs(name_starts_with=DELTA_PATH):
    print(" ->", blob.name)

# ✅ OPTION 2: BlobServiceClient with account_url
service_client = BlobServiceClient(account_url=API_BASE, credential=SAS_TOKEN)
container_client = service_client.get_container_client(AZURE_CONTAINER)

print("Listing blobs via BlobServiceClient:")
for blob in container_client.list_blobs(name_starts_with=DELTA_PATH):
    print(" ->", blob.name)
