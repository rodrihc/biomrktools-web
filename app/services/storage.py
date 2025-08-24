import json
import os
from typing import Any, List
import fsspec
from azure.identity import DefaultAzureCredential
from deltalake import DeltaTable
import pandas as pd
from .settings import settings

_account = settings.AZURE_STORAGE_ACCOUNT
_container = settings.AZURE_CONTAINER

# Use managed identity / dev creds automatically (works locally with Azure CLI login,
# and in Azure Container Apps with system-assigned identity).
_cred = DefaultAzureCredential(exclude_interactive_browser_credential=False)

def _fs():
    return fsspec.filesystem(
        "abfs",
        account_name=_account,
        credential=_cred
    )

def read_delta_head(path: str, limit: int = 20) -> List[dict]:
    # Acquire a bearer token for Delta-RS object store:
    token = _cred.get_token("https://storage.azure.com/.default").token
    uri = f"abfss://{_container}@{_account}.dfs.core.windows.net/{path}"

    dt = DeltaTable(
        uri,
        storage_options={
            "azure_storage_account_name": _account,
            "azure_storage_token": token,  # bearer token
        },
    )
    df: pd.DataFrame = dt.to_pandas()[:limit]
    return df.to_dict(orient="records")
