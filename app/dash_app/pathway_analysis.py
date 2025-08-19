# pages/pathway_analysis.py

from dash import html, dcc, Input, Output, callback
import pandas as pd
import numpy as np
import plotly.express as px

# Simulated pathway enrichment results
np.random.seed(42)
all_pathways = [
    "PI3K-Akt signaling", "MAPK signaling", "Apoptosis", "Cell Cycle",
    "p53 signaling", "WNT signaling", "Notch signaling", "TGF-beta signaling"
]
p_values = np.sort(np.random.uniform(0.0001, 0.05, len(all_pathways)))
gene_counts = np.random.randint(5, 25, len(all_pathways))
base_df = pd.DataFrame({
    "Pathway": all_pathways,
    "PValue": p_values,
    "GeneCount": gene_counts
})
base_df["-log10(PValue)"] = -np.log10(base_df["PValue"])

# Simulated gene categories
gene_sets = {
    "All": base_df,
    "Oncogenic": base_df.iloc[:5],
    "Immune": base_df.iloc[2:],
    "Metabolic": base_df.iloc[1:6]
}

# Simulated gene-pathway heatmap matrix
genes = ["TP53", "KRAS", "PIK3CA", "BRAF", "PTEN", "RB1", "EGFR", "CDK4"]
gene_pathway_matrix = pd.DataFrame(
    np.random.choice([0, 1], size=(len(genes), len(all_pathways))),
    index=genes, columns=all_pathways
)

# Layout
layout = html.Div([
    html.H3("Pathway Enrichment Analysis"),

    html.Label("Select Gene Set Category:", style={"marginTop": "10px"}),
    dcc.Dropdown(
        id="pathway-category",
        options=[{"label": k, "value": k} for k in gene_sets.keys()],
        value="All",
        clearable=False,
        style={"width": "300px", "marginBottom": "30px"}
    ),

    html.H5("Enriched Pathways (Bar Plot)"),
    dcc.Graph(id="pathway-bar"),
    html.Div(id="pathway-bar-text", style={"marginBottom": "30px"}),

    html.H5("Enriched Pathways (Dot Plot)"),
    dcc.Graph(id="pathway-dotplot"),
    html.Div(id="pathway-dotplot-text", style={"marginBottom": "30px"}),

    html.H5("Gene-Pathway Membership"),
    dcc.Graph(id="pathway-heatmap"),
    html.Div(id="pathway-heatmap-text"),
])


@callback(
    Output("pathway-bar", "figure"),
    Output("pathway-bar-text", "children"),
    Output("pathway-dotplot", "figure"),
    Output("pathway-dotplot-text", "children"),
    Output("pathway-heatmap", "figure"),
    Output("pathway-heatmap-text", "children"),
    Input("pathway-category", "value")
)
def update_pathway_figures(category):
    df = gene_sets[category]

    # Bar Plot
    fig_bar = px.bar(
        df.sort_values("-log10(PValue)", ascending=False),
        x="-log10(PValue)", y="Pathway",
        orientation="h",
        labels={"-log10(PValue)": "-log10(P-value)", "Pathway": "Pathway"},
        title=f"Top Enriched Pathways – {category}"
    )
    fig_bar.update_layout(template="plotly_dark", height=500)

    explanation_bar = (
        f"This bar plot shows the top pathways enriched in the selected gene set category: '{category}'. "
        "Bar height reflects statistical strength using the -log10 transformation of P-values. "
        "It enables easy comparison of biological relevance across pathways."
    )

    # Dot Plot
    fig_dot = px.scatter(
        df,
        x="-log10(PValue)", y="Pathway",
        size="GeneCount", color="-log10(PValue)",
        color_continuous_scale="Viridis",
        labels={"GeneCount": "Gene Count"},
        title=f"Pathway Dot Plot – {category}"
    )
    fig_dot.update_layout(template="plotly_dark", height=500)

    explanation_dot = (
        f"This dot plot visualizes the significance and gene count for each enriched pathway in the '{category}' gene set. "
        "Larger dots indicate more genes in a pathway; deeper colors indicate stronger enrichment. "
        "This view is useful for prioritizing biologically dense and statistically robust pathways."
    )

    # Filter heatmap matrix to match selected pathways
    selected_cols = df["Pathway"].values
    matrix = gene_pathway_matrix[selected_cols]

    fig_heatmap = px.imshow(
        matrix,
        labels=dict(x="Pathway", y="Gene", color="Membership"),
        color_continuous_scale=["#ffffff", "#636EFA"],
        title=f"Gene-to-Pathway Membership – {category}",
        text_auto=True
    )
    fig_heatmap.update_layout(template="plotly_dark", height=500)

    explanation_heatmap = (
        f"This matrix shows which genes are involved in the selected '{category}' pathways. "
        "It highlights overlap and multifunctionality. Blue cells mark gene membership in each pathway, "
        "allowing insight into pathway redundancy and pleiotropy."
    )

    return fig_bar, explanation_bar, fig_dot, explanation_dot, fig_heatmap, explanation_heatmap
