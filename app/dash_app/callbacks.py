from dash import Input, Output, callback, dash_table, html
from dash import Input, Output, callback, html
from dash import dash_table, html
from dash import Input, Output, callback, html

from ..services.controllers import load_analysis_delta_table
from .callbacks_settings import background_callback_manager
from app.services.controllers import load_analysis_delta_table

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


def dict_to_table(data: dict):
    """Convert a dictionary into a Dash DataTable with 'Key' and 'Value' columns."""
    if not data:
        return html.Div("No data available.")
    
    rows = [{"Key": k, "Value": v if not isinstance(v, (dict, list)) else str(v)} 
            for k, v in data.items()]
    
    return dash_table.DataTable(
        columns=[{"name": "Key", "id": "Key"}, {"name": "Value", "id": "Value"}],
        data=rows,
        page_size=20,
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left", "padding": "4px"},
        style_header={"fontWeight": "bold"},
    )


@callback(
    Output("analysis-store", "data"),
    Input("url", "pathname"),
    background=True,
    manager=background_callback_manager
)
def load_analysis(_):
    variables = load_analysis_delta_table()
    return variables  # must be JSON-serializable

@callback(
    Output("config-panel", "children"),
    Input("analysis-store", "data")
)
def display_config(variables):
    if not variables:
        return html.Div("Loading...")
    
    config = variables["config"]
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
    Input("analysis-store", "data")
)
def display_summary(variables):
    if not variables:
        return html.Div("Loading...")

    top_genes = variables["dir_summary"]["top_genes"]
    analysis_summary = variables["dir_summary"]["summary"]

    if not top_genes:
        return html.Div("No top genes available.")

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
    Input("analysis-store", "data"),
)
def display_llm_response(variables):

    if not variables:
        return html.Div("Loading...")

    llm_summary = variables.get("llm_summary")    
    
    return html.Div(
        [
            html.H4("LLM Response", style={"marginBottom": "10px"}),
            render_dict(llm_summary),
        ],
        style={"fontFamily": "Arial, sans-serif", "fontSize": "14px"},
    )



from dash import callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

@callback(
    Output("pca-3d-plot", "figure"),
    Input("analysis-store", "data")
)
def display_pca_3d(variables):
    if not variables:
        return go.Figure()  # empty figure while loading

    pc_df = pd.DataFrame(variables["dir_summary"].get("pca_data", []))  # expects PC1, PC2, PC3, subgroup, sample_id
    dir_summary = variables["dir_summary"]
    
    if pc_df.empty:
        return go.Figure()

    fig = px.scatter_3d(
        pc_df,
        x="PC1", y="PC2", z="PC3",
        color="subgroup",
        hover_data=["sample_id", "subgroup"],
        title="PCA 3D Plot"
    )

    # Add summary annotation
    fig.add_annotation(
        text=dir_summary.get("summary", ""),
        xref="paper", yref="paper",
        x=0, y=1.15, showarrow=False,
        font=dict(size=12, color="black"),
        align="left"
    )

    # Optionally add top_genes as a table below
    top_genes = dir_summary.get("top_genes", [])
    if top_genes:
        fig.add_trace(go.Table(
            header=dict(values=["Gene", "logFC", "p-value"]),
            cells=dict(
                values=[
                    [g["gene_name"] for g in top_genes],
                    [g["log_fc"] for g in top_genes],
                    [g["p_value"] for g in top_genes],
                ]
            ),
            domain=dict(x=[0, 1], y=[-0.4, -0.05])
        ))

    return fig
