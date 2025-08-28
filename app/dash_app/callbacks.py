from urllib.parse import parse_qs

from dash import Input, Output, callback, dash_table, dcc, html
from dash import Input, Output, callback
from dash import Input, Output, callback
from dash import Input, Output, callback
from dash import Input, Output, callback
from flask import request
import numpy as np
import numpy as np
import numpy as np
import pandas as pd
import pandas as pd
import pandas as pd
import pandas as pd
import pandas as pd
import plotly.express as px
import plotly.express as px
import plotly.express as px
import plotly.graph_objects as go
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app.services import controllers as ctrl
from app.services.controllers import load_analysis_delta_table

from .callbacks_settings import background_callback_manager


def render_value(key, value):
    """Render a single key/value pair or recurse if nested."""
    if isinstance(value, dict):
        return html.Div([
            html.Strong(f"{key}:"),
            html.Ul([html.Li(render_value(k, v)) for k, v in value.items()])
        ], style={"marginBottom": "0.5rem"})
    elif isinstance(value, list):
        return html.Div([
            html.Strong(f"{key}:"),
            html.Ul([html.Li(render_value(f"{key}[{i}]", v)) for i, v in enumerate(value)])
        ], style={"marginBottom": "0.5rem"})
    else:
        return html.Div([
            html.Span(f"{key}: ", style={"fontWeight": "bold"}),
            html.Span(str(value))
        ], style={"marginBottom": "0.25rem"})

def render_dict(d, level=0):
    """Recursively render dict into nested Divs."""
    children = []
    for k, v in d.items():
        if isinstance(v, dict):
            children.append(
                html.Div(
                    [
                        html.Div(f"{k}:", style={"fontWeight": "bold", "marginTop": "4px"}),
                        render_dict(v, level + 1),
                    ],
                    style={"marginLeft": f"{20 * level}px"},
                )
            )
        elif isinstance(v, list):
            children.append(
                html.Div(
                    [
                        html.Div(f"{k}:", style={"fontWeight": "bold", "marginTop": "4px"}),
                        render_list(v, level + 1),
                    ],
                    style={"marginLeft": f"{20 * level}px"},
                )
            )
        else:
            children.append(
                html.Div(
                    [
                        html.Span(f"{k}: ", style={"fontWeight": "bold"}),
                        html.Span(str(v)),
                    ],
                    style={"marginLeft": f"{20 * level}px"},
                )
            )
    return html.Div(children)

def render_list(lst, level=0):
    """Recursively render list into nested Divs."""
    children = []
    for i, v in enumerate(lst):
        if isinstance(v, dict):
            children.append(
                html.Div(
                    [
                        html.Div(f"[{i}]", style={"fontStyle": "italic", "marginTop": "2px"}),
                        render_dict(v, level + 1),
                    ],
                    style={"marginLeft": f"{20 * level}px"},
                )
            )
        elif isinstance(v, list):
            children.append(
                html.Div(
                    [
                        html.Div(f"[{i}]", style={"fontStyle": "italic", "marginTop": "2px"}),
                        render_list(v, level + 1),
                    ],
                    style={"marginLeft": f"{20 * level}px"},
                )
            )
        else:
            children.append(
                html.Div(
                    [
                        html.Span(f"[{i}]: ", style={"fontWeight": "bold"}),
                        html.Span(str(v)),
                    ],
                    style={"marginLeft": f"{20 * level}px"},
                )
            )
    return html.Div(children)


    
@callback(
    Output("params-store", "data"),
    Input("url", "search")
)
def read_query(search):
    if not search:
        return {}
    return {k: v[0] for k, v in parse_qs(search.lstrip("?")).items()}

@callback(
    Output("title-panel", "children"),
    Input("params-store", "data"),
    background=False,
    manager=background_callback_manager
)
def set_title(params):
    return html.Header(params.get("cancer_code"))


@callback(
    Output("config-store", "data"),
    Output("summary-store", "data"),
    Output("top-genes-store", "data"),
    Output("llm-summary-store", "data"),
    Output("results-store", "data"),
    Output("pc-avg-exprs-store", "data"),
    Input("params-store", "data"),
    background=False,
    manager=background_callback_manager
)
def load_analysis(params):

    print("params:", params)
    if not params:
        return ("No params", params)

    variables = load_analysis_delta_table(cancer_code=params.get("cancer_code")) or {}

    return (
        variables.get("config"),
        variables.get("dir_summary", {}).get("summary"),
        variables.get("dir_summary", {}).get("top_genes"),
        variables.get("llm_summary"),
        variables.get("results"),
        variables.get("pc_avg_exprs_pivot"),
    )

@callback(
    Output("config-panel", "children"),
    Input("config-store", "data"),
    background=True,
    manager=background_callback_manager
)
def display_config(config):

    rows = [{"Key": k, "Value": v if not isinstance(v, (dict, list)) else str(v)} 
            for k, v in config.items()]

    return dash_table.DataTable(
            columns=[{"name": "Key", "id": "Key"}, {"name": "Value", "id": "Value"}],
            data=rows,
            page_size=20,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "4px"},
            style_header={"fontWeight": "bold"},
        )

@callback(
    Output("summary-panel", "children"),
    Input("top-genes-store", "data"),
    Input("summary-store", "data"),
    background=True,
    manager=background_callback_manager
)
def display_summary(top_genes, analysis_summary):

    if not top_genes:
        return html.Div("No results available.")

    if not analysis_summary:
        return html.Div("No analysis summary available.")    

    top_genes_table = dash_table.DataTable(
        columns=[{"name": k, "id": k} for k in top_genes[0].keys()],
        data=top_genes,
        page_size=20,
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left", "padding": "4px"},
        style_header={"fontWeight": "bold"},
    )

    analysis_summary_rows = [
        {"Key": k, "Value": v if not isinstance(v, (dict, list)) else str(v)} 
            for k, v in analysis_summary.items()]

    summary_table = dash_table.DataTable(
            columns=[{"name": "Key", "id": "Key"}, {"name": "Value", "id": "Value"}],
            data=analysis_summary_rows,
            page_size=20,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "4px"},
            style_header={"fontWeight": "bold"},
        )

    return html.Div([
        html.Header("Top Genes: "),   
                html.Div(top_genes_table), 
                html.Header("Summary of analysis: "),   
                html.Hr(),
                html.Div(summary_table)
                ]
    )
                
@callback(
    Output("llm-response-panel", "children"),
    Input("llm-summary-store", "data"),
    background=True,
    manager=background_callback_manager
)
def display_llm_response(llm_summary):

    return html.Div(
        [
            html.H4("LLM Response", style={"marginBottom": "10px"}),
            render_dict(llm_summary),
        ],
        style={"fontFamily": "Arial, sans-serif", "fontSize": "14px"},
    )


@callback(
    Output("pca-3d-plot", "figure"),
    Input("results-store", "data"),
    background=True,
    manager=background_callback_manager
)
def display_pca_3d(pca_results):

    if not pca_results:
        return html.Div("No results available")
        
    
    # Build flattened DataFrame
    pc_rows = []
    for row in pca_results:
        values = row.get("values", [])
        row_dict = {d.get('column'): d.get('value') for d in values if 'column' in d and 'value' in d}
        if not row_dict:
            continue
        row_dict['sample_id'] = row.get('sample_id', 'Unknown')
        row_dict['subgroup'] = row.get('subgroup', 'Unknown')
        pc_rows.append(row_dict)

    pc_df = pd.DataFrame(pc_rows)

    # Ensure PC1, PC2, PC3 exist
    for col in ['PC1', 'PC2', 'PC3']:
        if col not in pc_df.columns:
            pc_df[col] = 0.0

    if pc_df.empty:
        return px.scatter_3d()  # still empty if no valid data

    fig = px.scatter_3d(
        pc_df,
        x='PC1',
        y='PC2',
        z='PC3',
        color='subgroup',
        hover_data=['sample_id', 'subgroup'],
        title="PCA 3D Plot"
    )

    fig.update_layout(
        scene=dict(
            xaxis_title='PC1',
            yaxis_title='PC2',
            zaxis_title='PC3'
        ),
        margin=dict(l=0, r=0, b=0, t=40)
    )

    return fig


@callback(       
    Output("heatmap-container", "data"),
    Input("pc-avg-exprs-store", "data"),
    background=True,
    manager=background_callback_manager)
def update_all_heatmaps(pc_avg_exprs_pivot):

    if not pc_avg_exprs_pivot:
        return html.Div("No results available")
        
    figs = []
    for pc_name in pc_avg_exprs_pivot:

        pc_data = pc_avg_exprs_pivot[pc_name]  # list of dicts
        pivot_df = pd.DataFrame(pc_data).set_index("ensembl")

        # heatmap
        fig = px.imshow(
            pivot_df,
            labels=dict(x="Subgroup", y="Gene (Ensembl)", color="Expression"),
            x=pivot_df.columns,
            y=pivot_df.index,
            color_continuous_scale="Viridis",
            title=f"Heatmap for {pc_name}"
        )
        fig.update_layout(xaxis={"side": "top"})
        figs.append(
            dcc.Graph(figure=fig, id=f"heatmap-{pc_name}")
        )

    return figs


@callback(
    Output("limma-logfc-plot", "figure"),
    Input("top-genes-store", "data"),
    background=True,
    manager=background_callback_manager)
def update_limma_voom_graph(top_genes, top_n=20):

    # Guard against empty or missing data
    if not top_genes:
        return go.Figure()

    # convert list of dicts to DataFrame
    df = pd.DataFrame(top_genes)

    # select top positive and negative logFC
    top_pos = df.sort_values("log_fc", ascending=False).head(top_n)
    top_neg = df.sort_values("log_fc", ascending=True).head(top_n)
    top_combined = pd.concat([top_neg, top_pos])

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=top_combined["log_fc"],
            y=top_combined["gene"],
            orientation="h",
            marker_color=np.where(top_combined["log_fc"] >= 0, "steelblue", "indianred")
        )
    )

    fig.update_layout(
        title=f"Top ±{top_n} logFC genes (limma-voom)",
        xaxis_title="log Fold Change",
        yaxis_title="Gene",
        height=600,
        margin=dict(l=200, r=50, t=50, b=50)
    )

    return fig


@callback(
    Output("limma-voom-volcano-plot", "figure"),
    Input("top-genes-store", "data"),
    background=True,
    manager=background_callback_manager)
def update_volcano_plot(top_genes):
    # Guard against missing data
    if not top_genes:
        return px.scatter(title="No data available")

    df = pd.DataFrame(top_genes)

    # Compute -log10 adjusted p-value
    df["neg_log10_adj_p"] = -np.log10(df["adj_p_value"])

    # Define significance
    df["significant"] = (df["adj_p_value"] < 0.05) & (abs(df["log_fc"]) > 1)

    fig = px.scatter(
        df,
        x="log_fc",
        y="neg_log10_adj_p",
        hover_data=["gene", "log_fc", "adj_p_value"],
        color="significant",
        color_discrete_map={True: "red", False: "grey"},
        labels={
            "log_fc": "Log2 Fold Change",
            "neg_log10_adj_p": "-log10(FDR)"
        },
        title="Volcano Plot"
    )

    fig.update_traces(marker=dict(size=6, opacity=0.8), selector=dict(mode='markers'))
    fig.update_layout(height=600, width=800, updatemenus=[{
        "buttons": [
            {"args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}],
             "label": "Play", "method": "animate"}
        ],
        "showactive": True
    }])

    return fig


@callback(
    Output("pc-box-scatter-plot", "figure"),
    Input("results-store", "data"),
    background=True,
    manager=background_callback_manager)
def update_pc_box_scatter(pca_results):
    # Guard against empty data

    # Flatten nested structure into long-format DataFrame
    rows = []
    for sample in pca_results:
        sample_id = sample["sample_id"]
        subgroup = sample["subgroup"]
        for val in sample["values"]:
            rows.append({
                "sample_id": sample_id,
                "subgroup": subgroup,
                "PC": val["column"],
                "value": val["value"]
            })

    df = pd.DataFrame(rows)

    # Create combined box + scatter plot
    fig = px.box(
        df,
        x="PC",
        y="value",
        color="subgroup",
        points="all",  # show scatter points
        hover_data=["sample_id"]
    )

    fig.update_layout(
        height=600,
        width=800,
        boxmode="group",  # group boxes by PC
        title="PC values by Subgroup with Scatter Points"
    )

    return fig