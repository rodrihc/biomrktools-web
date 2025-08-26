# app/api/delta_api.py
from fastapi import APIRouter
from deltalake import DeltaTable
import pandas as pd
import os
from app.services import settings
from app.services import app_config
from dotenv import load_dotenv

import json
import os
from typing import Any, List
import fsspec
from azure.identity import DefaultAzureCredential
from deltalake import DeltaTable
import pandas as pd
from app.services.settings import settings
from app.services import app_config



# Explicitly load .env first
load_dotenv(".env", override=False)  # override=False means host vars take priority


router = APIRouter()

_account = app_config.BASE_PATHS.get("storage_account") 
_container = app_config.BASE_PATHS.get("silver_container") 
token = settings.BIOMRKTOOLS_SA_TOKEN

DELTA_PATH = f"abfss://{_container}@{_account}.dfs.core.windows.net/biomrk_master/adeg/analysis/log_adeg_summary"


print(DELTA_PATH)

def read_delta():
    
    dt = DeltaTable(
        table_uri=DELTA_PATH,
        storage_options={
            "azure_storage_account_name": _account,
            "azure_storage_sas_token": token
        }
    )

    pd = dt.to_pandas()


    print(pd)

    return pd

@router.get("/config")
def get_config():
    df = read_delta()
    latest = df[df.analysis_id=="adeg_brca_001"].sort_values("timestamp", ascending=False).iloc[0]
    config = latest["config"]
    import json
    return json.loads(config)


@router.get("/dir_summary")
def get_dir_summary():
    df = read_delta()
    latest = df[df.analysis_id=="adeg_brca_001"].sort_values("timestamp", ascending=False).iloc[0]
    dir_summary = latest["dir_summary"]
    import json
    return json.loads(dir_summary)

@router.get("/top_genes")
def get_top_genes():
    dir_summary = get_dir_summary()
    return dir_summary.get("top_genes", [])

@router.get("/summary")
def get_summary():
    dir_summary = get_dir_summary()
    return dir_summary.get("summary", {})
