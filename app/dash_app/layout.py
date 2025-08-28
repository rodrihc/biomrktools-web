from dash import Input, Output, callback, dcc, html
from dash import DiskcacheManager
import dash_bootstrap_components as dbc
from dash_extensions.enrich import DashProxy
import diskcache

cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)



def serve_layout():
    return dbc.Container([


       # Captures pathname + query string
        dcc.Location(id="url", refresh=False),

        dcc.Store(id="params-store"),
        
        dcc.Store(id="config-store"),
        dcc.Store(id="summary-store"),
        dcc.Store(id="top-genes-store"),
        dcc.Store(id="llm-summary-store"),
        dcc.Store(id="results-store"),
        dcc.Store(id="pc-avg-exprs-store"),

            
        
        dcc.Store(id="analysis-store"),  # store loaded data
        



                    # Sub-container-1
            dbc.Row(
                id="sub-container-1",
                children=[
                    dbc.Col(
                        html.Div(id="config-panel", className="p-2 border rounded"),
                        width=12
                    )
                ]
            ),

            # Sub-container-2
            dbc.Row(
                id="sub-container-2",
                children=[
                    dbc.Col(
                        html.Div(id="summary-panel", className="p-2 border rounded"),
                        width=12
                    )
                ]
            ),

            # Sub-container-3 (split 40/60: text | graphics)
            dbc.Row(
                id="sub-container-3",
                children=[
                    dbc.Col(
                        html.Div("placeholder", id="sub3-text", className="p-2 border rounded"),
                        width=5
                    ),
                    dbc.Col(
                        dcc.Graph(id="pca-3d-plot", className="p-2 border rounded"),
                        width=7
                    ),
                ]
            ),

            # Sub-container-4 (again 40/60 split)
            dbc.Row(
                id="sub-container-4",
                children=[
                    dbc.Col(
                        html.Div(id="heatmap-container", className="p-2 border rounded"),
                        width=5
                    ),
                    dbc.Col(
                        dcc.Graph(id="limma-logfc-plot", className="p-2 border rounded"),
                        width=7
                    )
                ]
            ),

            # Sub-container-5 (40/60 split)
            dbc.Row(
                id="sub-container-5",
                children=[
                    dbc.Col(
                        dcc.Graph(id="limma-voom-volcano-plot", className="p-2 border rounded"),
                        width=5
                    ),
                    dbc.Col(
                        dcc.Graph(id="pc-box-scatter-plot", className="p-2 border rounded"),
                        width=7
                    )
                ]
            ),

            # Sub-container-6 (single 100%)
            dbc.Row(
                id="sub-container-6",
                children=[
                    dbc.Col(
                        html.Div(id="llm-response-panel", className="p-2 border rounded"),
                        width=12
                    )
                ]
            ),





    ], fluid=True)
