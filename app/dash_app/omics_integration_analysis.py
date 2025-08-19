from dash import html, dcc, Input, Output, callback
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.decomposition import PCA

# Simulate multi-omics data
np.random.seed(42)
genes = [f"Gene{i+1}" for i in range(30)]
samples = [f"Sample{i+1}" for i in range(10)]

# Transcriptomics
df_transcript = pd.DataFrame(np.random.randn(30, 10), index=genes, columns=samples).reset_index().melt(id_vars="index", var_name="Sample", value_name="Expression")
df_transcript["Omics"] = "Transcriptomics"
df_transcript.rename(columns={"index": "Gene"}, inplace=True)

# Proteomics
df_protein = pd.DataFrame(np.random.randn(30, 10), index=genes, columns=samples).reset_index().melt(id_vars="index", var_name="Sample", value_name="Expression")
df_protein["Omics"] = "Proteomics"
df_protein.rename(columns={"index": "Gene"}, inplace=True)

# Methylation
df_methyl = pd.DataFrame(np.random.rand(30, 10), index=genes, columns=samples).reset_index().melt(id_vars="index", var_name="Sample", value_name="Expression")
df_methyl["Omics"] = "Methylation"
df_methyl.rename(columns={"index": "Gene"}, inplace=True)

# Combine
df_omics = pd.concat([df_transcript, df_protein, df_methyl], ignore_index=True)

layout = html.Div([
    html.H3("Multi-Omics Integration"),

    html.Div([
        html.Div([
            html.Label("Select Gene"),
            dcc.Dropdown(
                id="gene-dropdown",
                options=[{"label": g, "value": g} for g in sorted(df_omics["Gene"].unique())],
                value="Gene1",
                clearable=False
            )
        ], style={"width": "48%", "display": "inline-block", "marginRight": "4%"}),

        html.Div([
            html.Label("Select Sample"),
            dcc.Dropdown(
                id="sample-dropdown",
                options=[{"label": s, "value": s} for s in sorted(df_omics["Sample"].unique())],
                value="Sample1",
                clearable=False
            )
        ], style={"width": "48%", "display": "inline-block"})
    ], style={"marginBottom": "30px"}),

    dcc.Graph(id="omics-barplot"),
    html.Div(id="omics-barplot-text", style={"marginBottom": "30px"}),

    dcc.Graph(id="omics-heatmap"),
    html.Div(id="omics-heatmap-text", style={"marginBottom": "30px"}),

    dcc.Graph(id="omics-correlation"),
    html.Div(id="omics-correlation-text", style={"marginBottom": "30px"}),

    dcc.Graph(id="omics-pca"),
    html.Div(id="omics-pca-text", style={"marginBottom": "30px"})
])

@callback(
    Output("omics-barplot", "figure"),
    Output("omics-barplot-text", "children"),
    Output("omics-heatmap", "figure"),
    Output("omics-heatmap-text", "children"),
    Output("omics-correlation", "figure"),
    Output("omics-correlation-text", "children"),
    Output("omics-pca", "figure"),
    Output("omics-pca-text", "children"),
    Input("gene-dropdown", "value"),
    Input("sample-dropdown", "value")
)
def update_omics_figures(selected_gene, selected_sample):
    bar_df = df_omics[(df_omics["Gene"] == selected_gene) & (df_omics["Sample"] == selected_sample)]

    fig_bar = px.bar(
        bar_df, x="Omics", y="Expression", color="Omics",
        title=f"{selected_gene} Expression across Omics in {selected_sample}",
        labels={"Expression": "Expression Level"}
    )
    fig_bar.update_layout(template="plotly_dark", height=400)

    explanation_bar = (
        f"This bar chart shows {selected_gene}'s expression level across omics layers in {selected_sample}. "
        "Concordance between transcriptomics and proteomics may indicate strong regulation, while methylation patterns "
        "can help infer epigenetic silencing or activation."
    )

    heat_df = df_omics[df_omics["Gene"] == selected_gene].pivot(index="Omics", columns="Sample", values="Expression")

    fig_heat = px.imshow(
        heat_df,
        color_continuous_scale="RdBu_r",
        title=f"{selected_gene} Expression Across Samples and Omics",
        labels=dict(x="Sample", y="Omics", color="Expression"),
        text_auto=".2f"
    )
    fig_heat.update_layout(template="plotly_dark", height=500)

    explanation_heat = (
        f"The heatmap illustrates {selected_gene}'s multi-omics expression across all samples. "
        "High expression in transcriptomics and low in proteomics may suggest post-transcriptional repression. "
        "Conversely, high methylation paired with low gene expression could indicate epigenetic silencing."
    )

    # Correlation between omics layers
    corr_df = df_omics[df_omics["Gene"] == selected_gene].pivot(index="Sample", columns="Omics", values="Expression")
    corr_matrix = corr_df.corr()
    fig_corr = px.imshow(corr_matrix, text_auto=".2f", title="Omics Correlation Matrix")
    fig_corr.update_layout(template="plotly_dark", height=400)
    explanation_corr = (
        "This matrix shows Pearson correlation between omics layers for the selected gene. "
        "High correlation between transcriptomics and proteomics suggests consistent expression, while a negative correlation "
        "between methylation and expression layers may imply epigenetic control."
    )

    # PCA plot of all genes in transcriptomics (as example)
    transcript_df = df_transcript.pivot(index="Gene", columns="Sample", values="Expression")
    pca = PCA(n_components=2).fit_transform(transcript_df)
    pca_fig = px.scatter(
        x=pca[:, 0], y=pca[:, 1], text=transcript_df.index,
        labels={"x": "PC1", "y": "PC2"},
        title="PCA of Transcriptomics Data"
    )
    pca_fig.update_layout(template="plotly_dark", height=500)
    explanation_pca = (
        "This PCA plot reduces the dimensionality of the transcriptomics data across all genes. "
        "Genes clustering together may share regulatory or functional roles, and the overall structure reflects transcriptional diversity."
    )

    return fig_bar, explanation_bar, fig_heat, explanation_heat, fig_corr, explanation_corr, pca_fig, explanation_pca
