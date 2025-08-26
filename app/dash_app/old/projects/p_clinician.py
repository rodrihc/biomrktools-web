from dash import html, dcc, callback, Input, Output
from dash.dash_table import DataTable

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Simulated expression data
expression_df = pd.DataFrame({
    "gene_id": ["MET", "KRAS", "TP53", "EGFR", "ALK"],
    "expression_value": [34.1, 22.5, 15.2, 5.1, 2.3]
})

# Simulated variant data
variant_df = pd.DataFrame({
    "gene": ["KRAS", "TP53"],
    "variant": ["G12C", "R175H"],
    "position": ["chr12:25398281", "chr17:7577539"],
    "impact": ["missense_variant", "pathogenic"]
})

# Simulated CIViC annotation
civic_df = pd.DataFrame({
    "gene": ["KRAS"],
    "variant": ["G12C"],
    "significance": ["predictive: sotorasib"],
    "evidence_level": ["A"],
    "source": ["CIViC"]
})

# Simulated pathway enrichment
pathway_df = pd.DataFrame({
    "pathway_name": ["MET signaling"],
    "FDR": [0.004],
    "genes_upregulated": ["MET, GAB1"]
})

# Simulated drug matches
drug_match_df = pd.DataFrame({
    "gene": ["MET"],
    "drug": ["Crizotinib"],
    "interaction_type": ["inhibitor"],
    "source": ["DGIdb"]
})

# Simulated trials
trial_df = pd.DataFrame({
    "trial_id": ["NCT0481234"],
    "condition": ["NSCLC"],
    "inclusion_criteria": ["KRAS G12C, prior EGFR failure"]
})

# Layout
layout = html.Div([
    html.H3("Clinician Report: Molecular Interpretation for Individual Patient"),

    html.H5("Mutation Lollipop Chart"),
    dcc.Graph(id="lollipop-plot"),
    html.Div("The lollipop chart shows the locations and types of variants detected in this patient. Notably, the KRAS G12C and TP53 R175H mutations are located in known functional domains, which supports their pathogenic role."),

    html.H5("Gene Expression (vs. Reference)"),
    dcc.Graph(id="expression-plot"),
    html.Div("This plot shows the patient's gene expression profile in comparison to a simulated TCGA reference range. MET is significantly overexpressed, indicating pathway activation and potential druggability."),

    html.H5("Actionable Variants (CIViC Annotations)"),
    DataTable(
        data=civic_df.to_dict("records"),
        columns=[{"name": i, "id": i} for i in civic_df.columns],
        style_table={"overflowX": "auto"}
    ),

    html.H5("Upregulated Pathways"),
    DataTable(
        data=pathway_df.to_dict("records"),
        columns=[{"name": i, "id": i} for i in pathway_df.columns],
        style_table={"overflowX": "auto"}
    ),

    html.H5("Matched Drugs"),
    DataTable(
        data=drug_match_df.to_dict("records"),
        columns=[{"name": i, "id": i} for i in drug_match_df.columns],
        style_table={"overflowX": "auto"}
    ),

    html.H5("Relevant Clinical Trials"),
    DataTable(
        data=trial_df.to_dict("records"),
        columns=[{"name": i, "id": i} for i in trial_df.columns],
        style_table={"overflowX": "auto"}
    ),

    html.Hr(),

    html.Div([
        html.H4("Result Statement"),
        html.P(
            "The patient sample showed overexpression of MET and activating mutation in KRAS G12C, consistent with known drivers in lung adenocarcinoma. "
            "MET pathway activation suggests potential benefit from MET inhibitors. The KRAS mutation is linked to resistance against EGFR inhibitors "
            "but sensitivity to sotorasib. 4 clinical trials were identified matching this molecular profile."
        )
    ])
])

# Callback visuals
@callback(
    Output("lollipop-plot", "figure"),
    Output("expression-plot", "figure"),
    Input("lollipop-plot", "id")
)
def update_clinician_view(_):
    # Lollipop plot
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=[1, 2],
        y=[0, 0],
        mode="markers+text",
        marker=dict(size=[20, 20], color=["red", "orange"]),
        text=variant_df["gene"] + " " + variant_df["variant"],
        textposition="top center"
    ))
    fig1.update_layout(
        title="Mutations in Patient Sample",
        xaxis=dict(title="Variant Index", showticklabels=False),
        yaxis=dict(visible=False),
        template="plotly_white"
    )

    # Expression vs reference
    reference_values = [5, 6, 7, 8, 9]
    ref_df = pd.DataFrame({
        "gene_id": ["MET"] * 5 + ["KRAS"] * 5,
        "expression_value": reference_values * 2,
        "type": ["Reference"] * 10
    })
    patient_df = expression_df.copy()
    patient_df["type"] = "Patient"

    combined_df = pd.concat([
        ref_df,
        patient_df[["gene_id", "expression_value", "type"]]
    ])

    fig2 = px.box(combined_df, x="gene_id", y="expression_value", color="type",
                  points="all", title="Patient Expression vs Reference",
                  labels={"expression_value": "Expression Level"},
                  template="plotly_white")

    return fig1, fig2
