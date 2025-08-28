from dash import Input, Output, callback, dcc, html
from dash import DiskcacheManager
import dash_bootstrap_components as dbc
from dash_extensions.enrich import DashProxy
import diskcache

cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)


def serve_layout():
    return dbc.Container([
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="analysis-store"),  # store loaded data
        dbc.Row(dbc.Col(html.Div(id="config-panel", className="p-2 border rounded"), width=6)),
        dbc.Row(dbc.Col(html.Div(id="summary-panel", className="p-2 border rounded"), width=6)),
        dbc.Row(dbc.Col(
            dcc.Graph(id="pca-3d-plot", className="p-2 border rounded"),
            width=6
        )),
        dbc.Row(dbc.Col(html.Div(id="heatmap-container", className="p-2 border rounded"), width=6)),
        dbc.Row(dbc.Col(
            dcc.Graph(id="limma-logfc-plot", className="p-2 border rounded"),
                width=6)),
        dbc.Row(dbc.Col(
            dcc.Graph(id="limma-voom-volcano-plot", className="p-2 border rounded"),
                width=6)),
        dbc.Row(dbc.Col(
            dcc.Graph(id="pc-box-scatter-plot", className="p-2 border rounded"),
                width=6)),
        dbc.Row(dbc.Col(html.Div(id="llm-response-panel", className="p-2 border rounded"), width=6)),
    ], fluid=True)
