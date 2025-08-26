from dash import Output, Input, html, callback
from .callbacks_settings import background_callback_manager
from .controllers import load_latest_analysis
from ..services.storage import read_delta_head


@callback(
    Output("analysis-store", "data"),
    Input("url", "pathname"),
    background=True,
    manager=background_callback_manager
)
def load_analysis(_):
    variables = read_delta_head()
    return variables  # must be JSON-serializable

@callback(
    Output("config-panel", "children"),
    Input("analysis-store", "data")
)
def display_config(variables):
    if not variables:
        return html.Div("Loading...")
    return [
        #html.Div(f"{k}: {', '.join(map(str, v)) if isinstance(v, list) else v}")
        #for k, v in variables["config"]#.items()
        html.Div( variables["config"])
    ]

@callback(
    Output("summary-panel", "children"),
    Input("analysis-store", "data")
)
def display_summary(variables):
    if not variables:
        return html.Div("Loading...")
    summary = variables["dir_summary"]#["summary"]
    return html.Div(summary)