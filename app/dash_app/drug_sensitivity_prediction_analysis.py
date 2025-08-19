from dash import html, dcc, Input, Output, callback, State
import pandas as pd
import numpy as np
import plotly.express as px
import dash
import json
import io
import base64


# Simulate drug sensitivity data
np.random.seed(42)
cancer_types = ["Lung", "Breast", "Colorectal", "Melanoma"]
drug_classes = ["Kinase Inhibitor", "Chemotherapy", "Immunotherapy"]
drugs = [f"{cls} {i+1}" for cls in drug_classes for i in range(4)]
samples = [f"Sample{i+1}" for i in range(30)]

df = pd.DataFrame({
    "Sample": np.random.choice(samples, 120),
    "CancerType": np.random.choice(cancer_types, 120),
    "Drug": np.random.choice(drugs, 120),
    "IC50": np.random.normal(loc=5, scale=1.5, size=120).clip(0.1, 10),
})

# 🧠 Fix incorrect lambda-as-column error
df["DrugClass"] = df["Drug"].apply(lambda d: " ".join(d.split()[:2]))


# Layout
layout = html.Div([
    html.H3("Drug Sensitivity Analysis"),

    html.Div([
        html.Div([
            html.Label("Select Cancer Type"),
            dcc.Dropdown(
                id="cancer-type-dropdown",
                options=[{"label": c, "value": c} for c in sorted(df["CancerType"].unique())],
                value="Lung",
                clearable=False
            )
        ], style={"width": "45%", "display": "inline-block", "marginRight": "5%"}),

        html.Div([
            html.Label("Select Drug Class"),
            dcc.Dropdown(
                id="drug-class-dropdown",
                options=[{"label": d, "value": d} for d in sorted(df["DrugClass"].unique())],
                value="Kinase Inhibitor",
                clearable=False
            )
        ], style={"width": "45%", "display": "inline-block"}),
    ], style={"marginBottom": "30px"}),

    dcc.Graph(id="sensitivity-boxplot"),
    html.Div(id="sensitivity-boxplot-text", style={"marginBottom": "30px"}),

    dcc.Graph(id="sensitivity-heatmap"),
    html.Div(id="sensitivity-heatmap-text", style={"marginBottom": "30px"}),

    html.Div([
        html.Button("Download CSV", id="btn-csv", n_clicks=0, style={"marginRight": "15px"}),
        dcc.Download(id="download-csv"),
        html.Button("Download JSON", id="btn-json", n_clicks=0),
        dcc.Download(id="download-json")
    ], style={"marginTop": "20px"})
])

# Callback for filtering and visualization
@callback(
    Output("sensitivity-boxplot", "figure"),
    Output("sensitivity-boxplot-text", "children"),
    Output("sensitivity-heatmap", "figure"),
    Output("sensitivity-heatmap-text", "children"),
    Input("cancer-type-dropdown", "value"),
    Input("drug-class-dropdown", "value")
)
def update_figures(selected_cancer, selected_class):
    filtered = df[(df["CancerType"] == selected_cancer) & (df["DrugClass"] == selected_class)]

    fig_box = px.box(
        filtered, x="Drug", y="IC50", color="Drug",
        title=f"IC50 Distribution by Drug – {selected_cancer} / {selected_class}",
        labels={"IC50": "IC50 (µM)"}
    )
    fig_box.update_layout(template="plotly_dark", height=500)

    explanation_box = (
        f"This box plot displays IC50 distributions for drugs in the class '{selected_class}' across samples from '{selected_cancer}' cancer. "
        "Drugs with lower median IC50s (lower boxes) are more potent. Outliers indicate response variability, which can guide drug prioritization or biomarker exploration."
    )

    heatmap_df = filtered.pivot_table(index="Sample", columns="Drug", values="IC50")
    fig_heatmap = px.imshow(
        heatmap_df,
        color_continuous_scale="Reds",
        labels=dict(x="Drug", y="Sample", color="IC50"),
        title="Sample-wise Drug Sensitivity (IC50 Heatmap)",
        text_auto=True
    )
    fig_heatmap.update_layout(template="plotly_dark", height=600)

    explanation_heatmap = (
        "This heatmap shows IC50 values per sample and drug. Darker cells indicate greater resistance (higher IC50), lighter cells indicate sensitivity. "
        "Patterns in the heatmap may highlight subgroups of samples that are particularly sensitive or resistant to specific drugs."
    )

    return fig_box, explanation_box, fig_heatmap, explanation_heatmap

# Callbacks for download buttons
@callback(
    Output("download-csv", "data"),
    Input("btn-csv", "n_clicks"),
    State("cancer-type-dropdown", "value"),
    State("drug-class-dropdown", "value"),
    prevent_initial_call=True
)
def download_csv(n, cancer, drug_class):
    filtered = df[(df["CancerType"] == cancer) & (df["DrugClass"] == drug_class)]
    return dcc.send_data_frame(filtered.to_csv, filename=f"{cancer}_{drug_class}_sensitivity.csv", index=False)

@callback(
    Output("download-json", "data"),
    Input("btn-json", "n_clicks"),
    State("cancer-type-dropdown", "value"),
    State("drug-class-dropdown", "value"),
    prevent_initial_call=True
)
def download_json(n, cancer, drug_class):
    filtered = df[(df["CancerType"] == cancer) & (df["DrugClass"] == drug_class)]
    return dict(content=filtered.to_json(orient="records", indent=2), filename=f"{cancer}_{drug_class}_sensitivity.json")
