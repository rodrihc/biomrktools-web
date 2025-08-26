# pages/mutation_analysis.py

from dash import html, dcc, Input, Output, callback
import pandas as pd
import numpy as np
import plotly.express as px

# Simulated binary mutation data (1 = mutated, 0 = wild-type)
genes = ["TP53", "KRAS", "PIK3CA", "EGFR", "PTEN", "BRAF", "IDH1", "CDKN2A"]
samples = [f"Sample{i}" for i in range(1, 21)]

np.random.seed(42)
mutation_matrix = pd.DataFrame(
    np.random.binomial(1, 0.2, size=(len(genes), len(samples))),
    index=genes, columns=samples
)

# Layout
layout = html.Div([
    html.H3("Gene Alteration / Mutation Analysis"),

    html.H5("Mutation Matrix"),
    dcc.Graph(id="mutation-heatmap"),
    html.Div(id="mutation-heatmap-text", style={"marginBottom": "30px"}),

    html.H5("Mutation Frequency"),
    dcc.Graph(id="mutation-frequency"),
    html.Div(id="mutation-frequency-text", style={"marginBottom": "30px"}),

    html.H5("Co-Mutation Matrix"),
    dcc.Graph(id="co-mutation-heatmap"),
    html.Div(id="co-mutation-text"),
])

# Unified callback
@callback(
    Output("mutation-heatmap", "figure"),
    Output("mutation-heatmap-text", "children"),
    Output("mutation-frequency", "figure"),
    Output("mutation-frequency-text", "children"),
    Output("co-mutation-heatmap", "figure"),
    Output("co-mutation-text", "children"),
    Input("mutation-heatmap", "id")
)
def update_mutation_figures(_):
    # Heatmap
    fig_heatmap = px.imshow(
        mutation_matrix,
        color_continuous_scale=["#ffffff", "#d62728"],
        labels=dict(x="Sample", y="Gene", color="Mutated"),
        title="Mutation Matrix (1 = mutated, 0 = wild-type)"
    )
    fig_heatmap.update_layout(template="plotly_dark", height=500)

    explanation_heatmap = (
        "This heatmap shows mutation status for 8 genes across 20 samples. "
        "Red blocks mark mutated genes. Some samples exhibit clustered mutations, "
        "suggesting possible co-altered pathways or mutational hotspots."
    )

    # Frequency bar chart
    mutation_counts = mutation_matrix.sum(axis=1).sort_values(ascending=True)
    fig_bar = px.bar(
        mutation_counts,
        orientation="h",
        labels={"value": "Number of Mutated Samples", "index": "Gene"},
        title="Mutation Frequency per Gene"
    )
    fig_bar.update_layout(template="plotly_dark", height=400)

    explanation_bar = (
        "The bar chart ranks genes by mutation frequency. "
        f"{mutation_counts.idxmax()} is mutated in the highest number of samples "
        f"({mutation_counts.max()}), potentially indicating oncogenic significance. "
        "Genes with fewer mutations may still have clinical relevance if they're actionable."
    )

    # Co-mutation matrix
    co_matrix = mutation_matrix.dot(mutation_matrix.T)
    np.fill_diagonal(co_matrix.values, 0)

    fig_co = px.imshow(
        co_matrix,
        text_auto=True,
        labels=dict(x="Gene", y="Gene", color="Co-Mutation Count"),
        color_continuous_scale="Blues",
        title="Pairwise Co-Mutation Matrix"
    )
    fig_co.update_layout(template="plotly_dark", height=600)

    explanation_co = (
        "This matrix counts how often gene pairs are mutated together. "
        "High values suggest synergistic or co-occurring mutations, possibly in shared pathways. "
        "Diagonal is zeroed out since it represents self-comparisons."
    )

    return fig_heatmap, explanation_heatmap, fig_bar, explanation_bar, fig_co, explanation_co
