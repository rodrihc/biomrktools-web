import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table, Input, Output, callback
import plotly.express as px
import pandas as pd
import numpy as np


# 30 named genes
genes = [
    "MMP9", "COL1A1", "CDH1", "TP53INP1", "ACTB",
    "BRCA1", "EGFR", "MYC", "VEGFA", "KRAS",
    "BCL2", "PTEN", "AKT1", "TP53", "GATA3",
    "FOXA1", "ERBB2", "CCND1", "CDK4", "SMAD4",
    "PIK3CA", "RB1", "CTNNB1", "NRAS", "NOTCH1",
    "MTOR", "MAPK1", "FGFR1", "JUN", "STAT3"
]

df_deg = pd.DataFrame([
    ("MMP9", 3.2, 0.0000012, 0.0000012, True),
    ("COL1A1", 2.9, 0.00015, 0.0002, True),
    ("CDH1", -2.3, 0.0008, 0.001, True),
    ("TP53INP1", -1.8, 0.002, 0.0025, True),
    ("ACTB", 0.4, 0.3, 0.35, False),
    ("BRCA1", 2.5, 0.00005, 0.00006, True),
    ("EGFR", -1.7, 0.01, 0.015, True),
    ("MYC", 3.0, 0.0001, 0.00012, True),
    ("VEGFA", 1.5, 0.04, 0.045, True),
    ("KRAS", -0.6, 0.5, 0.6, False),
    ("BCL2", -2.1, 0.005, 0.006, True),
    ("PTEN", 2.0, 0.0003, 0.00035, True),
    ("AKT1", 1.8, 0.02, 0.025, True),
    ("TP53", -3.1, 0.00002, 0.000025, True),
    ("GATA3", -0.3, 0.3, 0.35, False),
    ("FOXA1", 1.2, 0.06, 0.07, False),
    ("ERBB2", 2.7, 0.0002, 0.00025, True),
    ("CCND1", 1.0, 0.03, 0.035, True),
    ("CDK4", -1.5, 0.008, 0.01, True),
    ("SMAD4", 0.7, 0.09, 0.1, False),
    ("PIK3CA", 2.6, 0.0001, 0.00012, True),
    ("RB1", -1.9, 0.006, 0.007, True),
    ("CTNNB1", -0.4, 0.25, 0.3, False),
    ("NRAS", 1.4, 0.04, 0.045, True),
    ("NOTCH1", -2.2, 0.003, 0.0035, True),
    ("MTOR", 2.1, 0.0005, 0.0006, True),
    ("MAPK1", -0.2, 0.15, 0.2, False),
    ("FGFR1", 1.6, 0.035, 0.04, True),
    ("JUN", -2.5, 0.002, 0.0022, True),
    ("STAT3", 0.5, 0.2, 0.25, False)
], columns=["Gene", "log2FC", "p-value", "adj. p-value", "Significant"])


df_heatmap = pd.DataFrame([
    [2.1, 2.3, 2.0, 2.2, 2.4],
    [1.5, 1.7, 1.4, 1.6, 1.9],
    [-1.3, -1.1, -1.2, -1.4, -1.5],
    [-2.0, -1.9, -2.1, -2.2, -2.0],
    [0.5, 0.7, 0.6, 0.4, 0.3],
    [2.2, 2.4, 2.3, 2.5, 2.6],
    [-1.8, -2.0, -1.7, -1.6, -1.5],
    [3.1, 3.3, 3.0, 3.2, 3.4],
    [1.4, 1.6, 1.5, 1.3, 1.2],
    [-0.5, -0.6, -0.4, -0.7, -0.8],
    [-2.3, -2.1, -2.4, -2.2, -2.0],
    [2.0, 2.1, 1.9, 2.2, 2.3],
    [1.9, 1.8, 1.7, 1.6, 1.5],
    [-3.0, -3.1, -3.2, -3.3, -3.4],
    [0.2, 0.1, 0.3, 0.4, 0.5],
    [1.1, 1.0, 0.9, 1.2, 1.3],
    [2.5, 2.7, 2.6, 2.8, 2.9],
    [1.0, 0.8, 1.1, 1.2, 1.3],
    [-1.4, -1.6, -1.5, -1.3, -1.2],
    [0.6, 0.7, 0.8, 0.9, 1.0],
    [2.4, 2.3, 2.2, 2.1, 2.0],
    [-1.7, -1.8, -1.6, -1.9, -2.0],
    [-0.3, -0.2, -0.4, -0.5, -0.1],
    [1.3, 1.2, 1.4, 1.5, 1.6],
    [-2.1, -2.3, -2.2, -2.0, -2.4],
    [2.0, 2.2, 2.1, 2.3, 2.4],
    [-0.1, -0.3, -0.2, -0.4, -0.5],
    [1.7, 1.8, 1.6, 1.5, 1.4],
    [-2.4, -2.6, -2.5, -2.3, -2.2],
    [0.4, 0.3, 0.5, 0.6, 0.7]
], index=df_deg["Gene"], columns=[f"S{i+1}" for i in range(5)])


layout = html.Div([
    dbc.NavbarSimple(brand="BiomkTools · DEG Explorer", color="primary", dark=True),

    dbc.Container([
        dbc.Row([
            dbc.Col(dcc.Graph(id="volcano-plot"), md=6),
            dbc.Col(dcc.Graph(id="heatmap"), md=6),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dash_table.DataTable(
                id="deg-table",
                columns=[{"name": i, "id": i} for i in df_deg.columns],
                data=df_deg.to_dict("records"),
                sort_action="native",
                filter_action="native",
                page_size=5,
                style_table={'overflowX': 'auto'},
                style_cell={'padding': '5px', 'textAlign': 'left'},
                style_header={'backgroundColor': '#222', 'color': 'white', 'fontWeight': 'bold'},
                style_data={'backgroundColor': '#333', 'color': 'white'},
            ))
        ])
    ], fluid=True)
], style={
    "maxWidth": "1240px",       # 1140px standard website width
    "margin": "0 auto",         # center horizontally
    "padding": "20px"           # optional inner spacing
})

@callback(
    Output("volcano-plot", "figure"),
    Input("deg-table", "data")
)
def update_volcano(_):
    fig = px.scatter(
        df_deg, x="log2FC", y=-np.log10(df_deg["adj. p-value"]),
        color="Significant",
        hover_data=["Gene"],
        title="Volcano Plot",
        color_discrete_map={True: "crimson", False: "gray"},
    )
    fig.update_layout(template="plotly_dark", height=400)
    return fig

@callback(
    Output("heatmap", "figure"),
    Input("deg-table", "data")
)
def update_heatmap(_):
    fig = px.imshow(
        df_heatmap,
        labels=dict(x="Sample", y="Gene", color="Expression (Z-score)"),
        color_continuous_scale="RdBu_r",
        title="Heatmap of Selected DEGs"
    )
    fig.update_layout(
        template="plotly_dark",
        height=800,          # increase vertical space for 30 genes
        #width=1000,          # widen to show all sample labels
        margin=dict(t=100, l=20, r=20, b=50),  # more space for gene labels
        coloraxis_colorbar=dict(
            thickness=20,    # make color bar thinner
            len=0.75,        # shorten it vertically
            y=0.5,           # center it vertically
        ),
    )
     # ⬅ Stretch the plot grid to use more of the space
    fig.update_layout(
        xaxis=dict(domain=[0.05, 0.95]),  # stretch X plot area
        yaxis=dict(domain=[0.05, 0.95]),  # stretch Y plot area
    )
    fig.update_xaxes(tickangle=0)  # horizontal sample labels for readability
    return fig