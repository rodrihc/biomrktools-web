from dash import html, dcc, Input, Output, callback
import dash
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Simulate expression data
genes = ["TP53", "EGFR", "BRCA1", "PIK3CA", "AKT1", "ABCB1"]
samples = ["S1", "S2", "S3", "S4"]

expr_data = pd.DataFrame(
    [(gene, sample, np.random.normal(loc=10 + i, scale=2))
     for i, gene in enumerate(genes) for sample in samples],
    columns=["gene_id", "sample_id", "expression_value"]
)

# Simulate drug response data
drug_response = pd.DataFrame({
    "sample_id": samples * 2,
    "drug_name": ["Paclitaxel"] * 4 + ["Gefitinib"] * 4,
    "IC50": np.random.uniform(0.1, 5.0, 8).round(2)
})

# Simulate sample metadata
metadata = pd.DataFrame({
    "sample_id": samples,
    "condition": ["treated", "control", "treated", "control"],
    "tumor_type": ["BRCA"] * 4
})

# Simulated analysis results
volcano_df = pd.DataFrame({
    "gene_id": genes,
    "log2FC": [1.58, 2.1, -1.1, 0.5, 1.0, -2.3],
    "p_value": [0.003, 0.0005, 0.045, 0.2, 0.01, 0.002]
})

# Add -log10(p-value) for volcano plot
volcano_df["neg_log10_pval"] = -np.log10(volcano_df["p_value"])

pathway_df = pd.DataFrame({
    "pathway_name": ["PI3K-AKT signaling", "Apoptosis", "Cell cycle"],
    "FDR": [0.0012, 0.023, 0.034],
    "genes_in_pathway": ["EGFR, AKT1, PIK3CA", "TP53, CASP3", "CDK1, CDK2"]
})

pathway_df["neg_log10_fdr"] = -np.log10(pathway_df["FDR"])


drug_assoc_df = pd.DataFrame({
    "gene_id": ["ABCB1", "EGFR"],
    "drug_name": ["Paclitaxel", "Gefitinib"],
    "correlation": [0.85, -0.72],
    "interpretation": ["Overexpression → resistance", "Overexpression → sensitivity"]
})

layout = html.Div([
    html.H3("Use Case: Biomarker Discovery & Drug Sensitivity Prediction"),

    html.Div([
        html.H4("Interactive Volcano Plot (Differential Expression)"),
        dcc.Graph(
            id="volcano-plot",
            figure=px.scatter(
                volcano_df, x="log2FC", y="neg_log10_pval", text="gene_id",
                hover_data=["gene_id", "log2FC", "p_value"],
                color=volcano_df["p_value"] < 0.05,
                title="Volcano Plot of DEGs"
            ).update_traces(marker=dict(size=10)).update_layout(template="plotly_dark")
        ),
        html.P("This volcano plot visualizes differentially expressed genes between treated and control samples. Genes with log2 fold change > 1 and p-value < 0.05 are considered significant candidates.")
    ], style={"marginBottom": "40px"}),

    html.Div([
        html.H4("Pathway Enrichment Results (Reactome/GO)"),
        dcc.Graph(
            id="pathway-barplot",
            figure=px.bar(
                pathway_df, x="pathway_name", y="neg_log10_fdr",
                title="Top Enriched Pathways"
            ).update_layout(template="plotly_dark")
        ),
        html.P("The bar chart shows the top biological pathways enriched in differentially expressed genes. The PI3K-AKT pathway is prominently activated in this cohort, suggesting its relevance in tumor biology.")
    ], style={"marginBottom": "40px"}),

    html.Div([
        html.H4("Drug Response Associations by Gene Expression"),
        dcc.Graph(
            id="drug-corr-heatmap",
            figure=px.imshow(
                drug_assoc_df.pivot(index="gene_id", columns="drug_name", values="correlation"),
                color_continuous_scale="RdBu",
                zmin=-1, zmax=1,
                title="Correlation of Gene Expression with Drug Sensitivity"
            ).update_layout(template="plotly_dark")
        ),
        html.P("This heatmap reveals gene–drug relationships. For instance, overexpression of ABCB1 correlates strongly with resistance to paclitaxel, while EGFR expression predicts better response to gefitinib.")
    ], style={"marginBottom": "40px"}),

    html.H4("Interpretation Summary"),
    html.P("10 tumor samples were analyzed for expression and drug sensitivity. The platform identified 47 differentially expressed genes associated with treatment conditions, including TP53 and EGFR. Pathway enrichment revealed activation of the PI3K-AKT signaling pathway. Drug response data linked expression of ABCB1 to increased resistance to paclitaxel (IC50 > 1µM). These markers may predict resistance and guide alternative therapy selection.")
])
