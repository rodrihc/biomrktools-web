from dash import html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd
import numpy as np
import networkx as nx
import plotly.graph_objects as go

# Sample gene expression data
gene_expr_df = pd.DataFrame({
    "gene_id": ["AXL", "PTEN", "AXL", "PTEN"],
    "cell_line_id": ["CL001", "CL001", "CL002", "CL002"],
    "expression_value": [18.7, 3.2, 6.1, 5.8]
})

# Sample drug response data
drug_response_df = pd.DataFrame({
    "cell_line_id": ["CL001", "CL002"],
    "drug_name": ["Vemurafenib", "Vemurafenib"],
    "IC50": [6.8, 0.4]
})

# Sample correlation results
correlation_df = pd.DataFrame({
    "gene_id": ["AXL", "PTEN"],
    "drug_name": ["Vemurafenib"] * 2,
    "correlation": [0.79, -0.72],
    "p_value": [0.0011, 0.0042]
})

# Mock STRING interaction network
graph = nx.Graph()
graph.add_edge("AXL", "ZEB1", weight=0.91)
graph.add_edge("ZEB1", "TWIST1", weight=0.88)
pos = nx.spring_layout(graph, seed=42)

# STRING network to Plotly
edge_x, edge_y, node_x, node_y, node_text = [], [], [], [], []
for edge in graph.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]

for node in graph.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_text.append(node)

string_fig = go.Figure(
    data=[
        go.Scatter(x=edge_x, y=edge_y, mode='lines', line=dict(width=1, color='gray'), showlegend=False),
        go.Scatter(x=node_x, y=node_y, mode='markers+text', text=node_text,
                   textposition="top center",
                   marker=dict(size=20, color='skyblue'), showlegend=False)
    ],
    layout=go.Layout(title='STRING Interaction Network', height=400, margin=dict(t=40))
)

# Pathway enrichment mock data
pathway_df = pd.DataFrame({
    "pathway_name": ["EMT signaling"],
    "FDR": [0.0008],
    "upregulated_genes": ["AXL, ZEB1"]
})

pathway_df["neg_log10_fdr"] = -np.log10(pathway_df["FDR"])


# Create Dash layout
corr_cols = ["gene_id", "drug_name", "correlation"]
layout = html.Div([
    html.H3("Drug Resistance Pathway Discovery"),

    html.Div([
        html.H5("Correlation Heatmap (Gene vs Drug IC50)"),
        dcc.Graph(figure=px.imshow(
            correlation_df.pivot(index="gene_id", columns="drug_name", values="correlation"),
            color_continuous_scale='RdBu_r',
            title="Correlation Heatmap"
        )),
        html.Div("Interpretation: AXL is strongly positively correlated with resistance (high IC50), while PTEN shows an inverse pattern."),
    ], style={"marginBottom": "30px"}),

    html.Div([
        html.H5("Expression vs Drug Response"),
        dcc.Graph(figure=px.box(
            pd.merge(gene_expr_df, drug_response_df, on="cell_line_id"),
            x="gene_id", y="IC50", points="all", color="gene_id",
            title="Boxplot of IC50 grouped by gene expression"
        )),
        html.Div("Interpretation: Higher AXL expression is observed in cell lines with elevated IC50 for Vemurafenib, suggesting resistance association.")
    ], style={"marginBottom": "30px"}),

    html.Div([
        html.H5("STRING Interaction Network"),
        dcc.Graph(figure=string_fig),
        html.Div("Interpretation: ZEB1 acts as a central hub connecting AXL and TWIST1, known EMT regulators in drug resistance.")
    ], style={"marginBottom": "30px"}),

    html.Div([
        html.H5("Enriched Pathways in Resistant Cell Lines"),
        dcc.Graph(figure=px.bar(
            pathway_df, x="pathway_name", y="neg_log10_fdr",
            labels={"-log10(FDR)": "Significance (-log10 FDR)"},
            title="Pathways associated with resistance"
        )),
        html.Div("Interpretation: EMT signaling pathway is significantly enriched in resistant lines, driven by AXL and ZEB1 upregulation.")
    ], style={"marginBottom": "30px"}),

    html.Div([
        html.H5("Download Results"),
        html.Button("Download CSV", id="download-csv-btn"),
        dcc.Download(id="download-csv"),
        html.Button("Download JSON", id="download-json-btn", style={"marginLeft": "10px"}),
        dcc.Download(id="download-json")
    ])
])
