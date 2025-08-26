# app/dash_app/controllers.py

import io
import json
import pandas as pd
from azure.storage.blob import ContainerClient
from app.services.settings import Settings
from app.services import app_config

settings = Settings()

BIOMRKTOOLS_SA_TOKEN = settings.BIOMRKTOOLS_SA_TOKEN
DELTA_PATH = app_config.DATA_PATHS.get("adeg")
STORAGE_ACCOUNT = app_config.BASE_PATHS.get("storage_account")
SILVER_CONTAINER = app_config.BASE_PATHS.get("silver_container")


#TODO deprecate this function. Leave it as an example. Reading blob wise is for config files but not for delta tables. 
def load_latest_analysis(analysis_id: str = "adeg_brca_001") -> dict:
    """Fetch latest parquet data for a given analysis_id and return parsed variables dict."""
    container_url = f"https://{STORAGE_ACCOUNT}.blob.core.windows.net/{SILVER_CONTAINER}?{BIOMRKTOOLS_SA_TOKEN}"
    container_client = ContainerClient.from_container_url(container_url)

    part_names = [
        b.name for b in container_client.list_blobs(name_starts_with=DELTA_PATH)
        if b.name.endswith(".parquet")
    ]
    if not part_names:
        raise FileNotFoundError(f"No parquet files found under prefix: {DELTA_PATH}")

    dfs = []
    for name in part_names:
        blob_client = container_client.get_blob_client(name)
        buf = io.BytesIO()
        blob_client.download_blob().readinto(buf)
        buf.seek(0)
        dfs.append(pd.read_parquet(buf))

    df = pd.concat(dfs, ignore_index=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # get latest run for given analysis
    df = df[df["analysis_id"] == analysis_id].sort_values("timestamp", ascending=False).iloc[0]

    variables = df.to_dict()
    for col in ["config", "dir_summary"]:
        if col in variables:
            variables[col] = json.loads(variables[col])
    return variables
