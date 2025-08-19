import io
import os

from azure.storage.blob import BlobClient
from azure.storage.blob import BlobServiceClient, ContainerClient
from dotenv import load_dotenv
import pandas as pd
from dash import html, dash_table

load_dotenv()

AZURE_CONTAINER = os.getenv("AZURE_CONTAINER")
API_BASE = os.getenv("API_BASE")          # should be https://biomrktools02sa.blob.core.windows.net
DELTA_PATH = os.getenv("DELTA_PATH")      # e.g. biomrk_master/adeg/v_adeg_tcga_brca_001_limma_voom
SAS_TOKEN = os.getenv("SAS_TOKEN")

def serve_layout():
    # pick one parquet blob (first one we listed earlier)
    blob_name = f"{DELTA_PATH}/part-00000-0eff1f98-cd33-463d-9030-f8b304a37997-c000.snappy.parquet"
    blob_url = f"{API_BASE}/{AZURE_CONTAINER}/{blob_name}?{SAS_TOKEN}"

    print("Downloading:", blob_url)
    blob_client = BlobClient.from_blob_url(blob_url)
    stream = io.BytesIO()
    blob_client.download_blob().readinto(stream)
    stream.seek(0)

    df = pd.read_parquet(stream)
    print(df.head(10))

    delta_rows = df.head(10).to_dict(orient="records")
    delta_cols = [{"name": c, "id": c} for c in df.columns]

    return html.Div([
        html.H2("biomrktools-web • Lakehouse Reader (Delta Preview)"),
        html.H3("Delta preview (first 10 rows)"),
        dash_table.DataTable(columns=delta_cols, data=delta_rows, page_size=10),
        html.Hr(),
        html.Div("This page directly fetches a Parquet file from Blob Storage.")
    ])

layout = serve_layout
