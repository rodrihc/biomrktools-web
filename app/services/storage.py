import json
import os
from typing import Any, List
import fsspec
from azure.identity import DefaultAzureCredential
from deltalake import DeltaTable
import pandas as pd
from .settings import settings
from app.services import app_config
# Then read into pandas
import pyarrow.compute as pc
import pyarrow.dataset as ds

_account = app_config.BASE_PATHS.get("storage_account") 
_container = app_config.BASE_PATHS.get("silver_container") 
_table_path = app_config.DATA_PATHS.get("adeg") 

token = settings.BIOMRKTOOLS_SA_TOKEN

# Use managed identity / dev creds automatically (works locally with Azure CLI login,
# and in Azure Container Apps with system-assigned identity).
_cred = DefaultAzureCredential(exclude_interactive_browser_credential=False)

def _fs():
    return fsspec.filesystem(
        "abfs",
        account_name=_account,
        credential=_cred
    )

def read_delta_head(path: str = _table_path, limit: int = 20) -> List[dict]:
    # Acquire a bearer token for Delta-RS object store:
    #token = _cred.get_token("https://storage.azure.com/.default").token
    
    uri = f"abfss://{_container}@{_account}.dfs.core.windows.net/{path}"

    df = DeltaTable(
        table_uri=uri,
        storage_options={
            "azure_storage_account_name": _account,
            "azure_storage_sas_token": token
        }
    ).to_pyarrow_table(
        partitions=[("cancer_code", "=", "BRCA")],  # <- specify partition key + value
        columns=None  # or a list of specific columns
    ).to_pandas()

    
    df['log_summary'] = df['log_summary'].astype(str)
    df['llm_summary'] = df['llm_summary'].astype(str)
    df['config'] = df['config'].astype(str)

    print(df)
    print(df["config"])


    # Ensure all entries in top_genes (ARRAY<STRING>) are plain lists
    df['top_genes'] = df['top_genes'].apply(lambda x: list(x) if isinstance(x, (list, tuple)) else [])

    return df.to_dict(orient="records")[0] 
