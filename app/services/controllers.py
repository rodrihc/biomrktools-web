# app/dash_app/controllers.py

import io
import json
import json
import json
import os
from sys import version
from typing import Any, List
from typing import Any, Dict

from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContainerClient
from deltalake import DeltaTable
import fsspec
import pandas as pd
from pyarrow import null
import pyarrow.compute as pc
import pyarrow.dataset as ds

from app.services import app_config
from app.services import app_config
from app.services.settings import Settings
from app.services.settings import settings

# Use managed identity / dev creds automatically (works locally with Azure CLI login,
# and in Azure Container Apps with system-assigned identity).
_cred = DefaultAzureCredential(exclude_interactive_browser_credential=False)

settings = Settings()

BIOMRKTOOLS_SA_TOKEN = settings.BIOMRKTOOLS_SA_TOKEN
DELTA_PATH = app_config.DATA_PATHS.get("adeg")
STORAGE_ACCOUNT = app_config.BASE_PATHS.get("storage_account")
SILVER_CONTAINER = app_config.BASE_PATHS.get("silver_container")

def _fs():
    return fsspec.filesystem(
        "abfs",
        account_name=STORAGE_ACCOUNT,
        credential=_cred
    )


def load_analysis_blob(analysis_id: str = "adeg_brca_001") -> dict:
    """
        Fetch latest parquet data for a given analysis_id and return parsed variables dict.
        Uses blog direct download. 
        
        TODO: This fuction should be deprecated and blob and container classes be used only for accesing config files  
    
    """
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
    for col in ["config", "dir_summary", "llm_summary"], :
        if col in variables:
            variables[col] = json.loads(variables[col])
    return variables

def load_analysis_delta_table(path: str = DELTA_PATH, cancer_code: str = 'OV', limit: int = 1) -> Dict[str, Any]:
    """
    Read first row from a Delta table as a structured Python dict.
    JSON fields are deserialized safely, while array/struct fields are preserved.
    """

    if not BIOMRKTOOLS_SA_TOKEN:
        raise ValueError("No SAS Token provided")

    uri = f"abfss://{SILVER_CONTAINER}@{STORAGE_ACCOUNT}.dfs.core.windows.net/{path}"


    dt = DeltaTable(
            table_uri=uri,
            storage_options={
                "azure_storage_account_name": STORAGE_ACCOUNT,
                "azure_storage_sas_token": BIOMRKTOOLS_SA_TOKEN,
            },
        )
        
    partitions = dt.partitions(partition_filters=[("cancer_code", "=", cancer_code)])  # typically a list of dicts
    partition_timestamps = []
    for part in partitions:
        partition_timestamps.append(int(part["log_timestamp"]))

    partition_timestamps.sort()
    latest_ts = partition_timestamps[0]


    df = dt.to_pyarrow_table(
            partitions=[("cancer_code", "=", cancer_code), ("log_timestamp", "=", latest_ts)],  # adjust as needed
        ).to_pandas()


 
    record_dict = map_structures_to_json(df) 
    record_dict = build_pc_avg_exprs_pivot(record_dict)

    return record_dict

def map_structures_to_json(df: pd.DataFrame) -> dict: 
    
    if df.empty:
        return {}

    # Ensure top_genes is always a list
    if "top_genes" in df.columns:
        df["top_genes"] = df["top_genes"].apply(
            lambda x: list(x) if isinstance(x, (list, tuple)) else []
        )

    # Take first row as dict
    record_dict = df.iloc[0].to_dict()

    # Safely decode JSON string columns if necessary
    for col in ["dir_summary", "config", "llm_summary", "results", "pc_avg_exprs"]:
        if col in record_dict and isinstance(record_dict[col], str):
            try:
                record_dict[col] = json.loads(record_dict[col])
            except json.JSONDecodeError:
                # keep original string if it's not valid JSON
                pass

    return record_dict        

def build_pc_avg_exprs_pivot(record_dict) -> pd.DataFrame:

    pc_avg_exprs_pivot = {}

    for pc_entry in record_dict["pc_avg_exprs"]:
        pc_name = pc_entry["pc_name"]

        # flatten details into rows
        rows = []
        for gene in pc_entry["details"]:
            ensembl = gene["ensembl"]
            for g in gene["groups"]:
                rows.append({
                    "ensembl": ensembl,
                    "subgroup": g["subgroup"],
                    "value": g["value"]
                })

        df = pd.DataFrame(rows)

        if not df.empty:
            pc_pivot = df.pivot(index="ensembl", columns="subgroup", values="value")
            # reset index so ensembl becomes a column again
            # convert to list-of-dicts so it's JSON-serializable
            pc_avg_exprs_pivot[pc_name] = pc_pivot.reset_index().to_dict(orient="records")
        else:
            pc_avg_exprs_pivot[pc_name] = []

    record_dict["pc_avg_exprs_pivot"] = pc_avg_exprs_pivot

    return record_dict

