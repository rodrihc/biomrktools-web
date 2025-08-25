import io
import json
import os

from azure.storage.blob import ContainerClient
from dash import dash_table, html
from dotenv import load_dotenv
import pandas as pd 
from app.services.settings import Settings
from app.services import app_config


settings = Settings()

BIOMRKTOOLS_SA_TOKEN = settings.BIOMRKTOOLS_SA_TOKEN                # full SAS token string
BIOMRKTOOLS_ENV =  settings.BIOMRKTOOLS_ENV                         # full SAS token string

DELTA_PATH          = app_config.DATA_PATHS.get("adeg")             # e.g. "biomrk_master/adeg/analysis/log_adeg_summary"
STORAGE_ACCOUNT     = app_config.BASE_PATHS.get("storage_account")  # e.g. "https://biomrktools02sa.blob.core.windows.net"
SILVER_CONTAINER    = app_config.BASE_PATHS.get("silver_container")

#variables["config"]
def read_display_vars(element:dict):
    # Build HTML display of all config key-value pairs
    config_items = []
    for key, value in element.items():
        # Handle lists nicely
        if isinstance(value, list):
            display_value = ", ".join(map(str, value))
        else:
            display_value = str(value)
        config_items.append(
            
            html.Div([
                html.Strong(f"{key}: "), html.Span(display_value)
            ], style={"margin": "4px 0"})
               
        )

    return config_items

def serve_layout():
    # Build container client from SAS URL
    container_url = f"https://{STORAGE_ACCOUNT}.blob.core.windows.net/{SILVER_CONTAINER}?{BIOMRKTOOLS_SA_TOKEN}"
    container_client = ContainerClient.from_container_url(container_url)
    
    # List all parquet parts under the given Delta path
    part_names = [
        b.name for b in container_client.list_blobs(name_starts_with=DELTA_PATH)
        if b.name.endswith(".parquet")
    ]
    if not part_names:
        raise FileNotFoundError(f"No parquet files found under prefix: {DELTA_PATH}")

    # Download and load each part into a dataframe
    dfs = []
    for name in part_names:
        blob_client = container_client.get_blob_client(name)
        buf = io.BytesIO()
        blob_client.download_blob().readinto(buf)
        buf.seek(0)
        dfs.append(pd.read_parquet(buf))

    # Concatenate all parts into one dataframe
    df = pd.concat(dfs, ignore_index=True)


    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df[df["analysis_id"] == "adeg_brca_001"]
    df = df.sort_values("timestamp", ascending=False).iloc[0]

    variables = df.to_dict()

    for col in ["config", "dir_summary"]:
        if col in variables:
            variables[col] = json.loads(variables[col])

    # Example console prints (still there if you want them)

    config_items = read_display_vars(variables["config"])
    dir_summary = variables["dir_summary"]
    top_genes =  dir_summary["top_genes"] #read_display_vars(variables["dir_summary"]["top_genes"])
    summary = dir_summary["summary"] #read
    
    return html.Div([
        html.H2("biomrktools-web • Lakehouse Reader (Delta Preview)"),
        html.Hr(),
        html.H3("Configuration values"),
        html.Div(config_items, style={"padding": "10px", "border": "1px solid #ccc", "borderRadius": "6px"}),
        html.Hr(),
        html.H3("Dimensionality Reduction Summary"),
        html.Div(dir_summary, style={"padding": "10px", "border": "1px solid #ccc", "borderRadius": "6px"}),
        html.Hr(),
        
        html.Div([
            html.H3("Differentially Expressed Genes Analysis"),
            html.Pre(df["log_summary"])
                ], style={"padding": "10px", "border": "1px solid #ccc", "borderRadius": "6px"}),
 
        html.Hr(),
        html.H3("Top Genes"),
             
        dash_table.DataTable(
        columns=[{"name": k, "id": k} for k in top_genes[0].keys()],
        data=top_genes,
        page_size=15,
        style_table={"overflowX": "auto"},
        ),
    
        html.Hr(),
        html.H3("Summary"),
        html.Div([
        html.Strong("Summary: "),
        html.Pre(json.dumps(summary, indent=2))
        ], style={"margin": "4px 0"})
        
        
        ,
        html.Hr()
        
    ])

layout = serve_layout

