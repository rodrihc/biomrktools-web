
# app.py
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
from pages import deg_analysis, pathway_analysis, drug_sensitivity_prediction_analysis, survival_analysis, omics_integration_analysis, mutation_analysis
from projects import p_researcher, p_clinician, p_scientist

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.CYBORG])

import dash_bootstrap_components as dbc
from dash import html

html.Div([
    dcc.Graph(id="lollipop-plot", figure={}),
    dcc.Graph(id="expression-plot", figure={}),
], style={"display": "none"})

sidebar = html.Div(
    [
        html.H2("Menu", className="display-4"),
        html.Hr(),

        # === Analysis Section ===
        html.H5("Analysis", className="text-white mt-3"),
        dbc.Nav(
            [
                dbc.NavLink("DEG Analysis", href="/deg", active="exact"),
                dbc.NavLink("Pathway Analysis", href="/pathway", active="exact"),
                dbc.NavLink("Drug Sensitivity Prediction Analysis", href="/drug", active="exact"),
                dbc.NavLink("Survival Analysis", href="/survival", active="exact"),
                dbc.NavLink("Omics Integration Analysis", href="/omics", active="exact"),
                dbc.NavLink("Gene Alteration Analysis", href="/mutation", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),

        html.Hr(),

        # === Projects Section ===
        html.H5("Projects", className="text-white mt-3"),
        dbc.Nav(
            [
                dbc.NavLink("Project Research", href="/p_researcher", active="exact"),
                dbc.NavLink("Project Clinician", href="/p_clinician", active="exact"),
                dbc.NavLink("Project Pharma Scientist", href="/p_scientist", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style={
        "position": "fixed",
        "top": "56px",
        "left": 0,
        "bottom": 0,
        "width": "16rem",
        "padding": "2rem 1rem",
        "background-color": "#222",
        "color": "white",
    },
)


navbar = dbc.NavbarSimple(brand="BiomkTools", color="primary", dark=True, fixed="top")

content = html.Div(id="page-content", style={"margin-left": "18rem", "padding": "2rem 1rem"},)

app.layout = html.Div([
    dcc.Location(id="url"),
    navbar,
    sidebar,
    content,
])

@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(pathname):
    if pathname == "/deg":
        return deg_analysis.layout
    elif pathname == "/pathway":
        return pathway_analysis.layout
    elif pathname == "/survival":
        return survival_analysis.layout
    elif pathname == "/drug":
        return drug_sensitivity_prediction_analysis.layout
    elif pathname == "/omics":
        return omics_integration_analysis.layout
    elif pathname == "/mutation":
        return mutation_analysis.layout
    
    elif pathname == "/p_researcher":
        return p_researcher.layout
    elif pathname == "/p_clinician":
        return p_clinician.layout
    elif pathname == "/p_scientist":
        return p_scientist.layout
    else:
        return html.Div([
            html.H3("Welcome to BiomkTools"),
            html.P("Select an analysis from the menu."),
        ])

if __name__ == "__main__":
    app.run(debug=True)
