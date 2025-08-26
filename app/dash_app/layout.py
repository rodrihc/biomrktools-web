import dash_bootstrap_components as dbc
from dash_extensions.enrich import DashProxy
from dash import dcc, html, Input, Output, callback
import diskcache
from dash import DiskcacheManager

cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)


def serve_layout():
    return dbc.Container([
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="analysis-store"),  # store loaded data
        dbc.Row(dbc.Col(html.Div(id="config-panel", className="p-2 border rounded"), width=6)),
        dbc.Row(dbc.Col(html.Div(id="summary-panel", className="p-2 border rounded"), width=6)),
        dbc.Row(dbc.Col(html.Div(id="llm-response-panel", className="p-2 border rounded"), width=6)),
    ], fluid=True)
