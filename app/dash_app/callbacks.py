from dash import Input, Output, callback, dash_table, html
from dash import Input, Output, callback, html
from dash import dash_table, html
import pandas as pd
import plotly.express as px

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
    Input("analysis-store", "data"),
    background=True,
    manager=background_callback_manager
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
    Input("analysis-store", "data"),
    background=True,
    manager=background_callback_manager
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
    background=True,
    manager=background_callback_manager
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


@callback(
    Output("pca-3d-plot", "figure"),
    Input("analysis-store", "data"),
    background=True,
    manager=background_callback_manager
)
def display_pca_3d(variables):
    if not variables:
        return px.scatter_3d()  # empty figure

    result = variables.get("results", [])
    if not result:
        return px.scatter_3d()  # still empty if no results

    # Build flattened DataFrame
    pc_rows = []
    for row in result:
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
