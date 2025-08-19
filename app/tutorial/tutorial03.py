from dash import html, dcc, dash_table, Input, Output, Dash
import pandas as pd
import plotly.express as px
import numpy as np
import uuid

# Load data
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

# Initialize app
app = Dash()


def load_mock_deg_data():
        data = [
            ("MMP9", 3.2, 0.0000012, 0.0000012, True),
            ("COL1A1", 2.9, 0.00015, 0.0002, True),
            ("CDH1", -2.3, 0.0008, 0.001, True),
            ("TP53INP1", -1.8, 0.002, 0.0025, True),
            ("ACTB", 0.4, 0.3, 0.35, False)
        ]

        return pd.DataFrame(data, columns=["Gene", "log2FC", "p-value", "adj. p-value", "Significant"])

def load_mock_heatmap_data():
        genes = ["MMP9", "COL1A1", "CDH1", "TP53INP1"]
        samples = [f"Sample{i}" for i in range(1, 6)]
        expr_values = [
            [2.1, 2.3, 2.0, 2.2, 2.4],
            [1.5, 1.7, 1.4, 1.6, 1.9],
            [-1.3, -1.1, -1.2, -1.4, -1.5],
            [-2.0, -1.9, -2.1, -2.2, -2.0]
        ]

        return pd.DataFrame(expr_values, index=genes, columns=samples)

def grid_tile(content, grid_opts):
        tile_id = f"tile-{uuid.uuid4()}"
        return html.Div([
            html.Div(content, className="grid-stack-item-content")
        ], className="grid-stack-item", **{f"data-gs-{k}": v for k, v in grid_opts.items()}, title=tile_id)


df_deg = load_mock_deg_data()
df_heatmap = load_mock_heatmap_data()

def callbacks(self):
        @self.app.callback(
            Output("volcano-plot", "figure"),
            Input("deg-table", "data")
        )
        def update_volcano(_):
            df = df_deg
            fig = px.scatter(
                df, x="log2FC", y=-np.log10(df["adj. p-value"]),
                color="Significant",
                hover_data=["Gene"],
                title="Volcano Plot",
                color_discrete_map={True: "crimson", False: "gray"},
            )
            fig.update_layout(template="plotly_dark", height=400)
            return fig

        @self.app.callback(
            Output("heatmap", "figure"),
            Input("deg-table", "data")
        )
        def update_heatmap(_):
            fig = px.imshow(
                df_heatmap,
                labels=dict(x="Sample", y="Gene", color="Expression (Z-score)"),
                color_continuous_scale="RdBu_r",
                title="Heatmap of Selected DEGs"
            )
            fig.update_layout(template="plotly_dark", height=400)
            return fig


# App layout with left/right margins
app.layout = html.Div([
    grid_tile(dcc.Graph(id="volcano-plot"), {"x": 6, "y": 0, "width": 6, "height": 4}),
    grid_tile(dcc.Graph(id="heatmap"), {"x": 6, "y": 4, "width": 6, "height": 4}),  # fixed y to 4 (not 100)
    grid_tile(html.Div([
                    html.H5("🔬 DEG Table", className="text-info mb-2"),
                    dash_table.DataTable(
                        id="deg-table",
                        columns=[{"name": i, "id": i} for i in load_mock_deg_data().columns],
                        data=load_mock_deg_data().to_dict("records"),
                        sort_action="native",
                        filter_action="native",
                        page_size=5,
                        style_table={'overflowX': 'auto'},
                        style_cell={'padding': '5px', 'textAlign': 'left'},
                        style_header={'backgroundColor': '#222', 'color': 'white', 'fontWeight': 'bold'},
                        style_data={'backgroundColor': '#333', 'color': 'white'},
                    )
                ]), {"x": 0, "y": 8, "width": 12, "height": 3}),

    html.H1('My First App with Data and a Graph'),
    dash_table.DataTable(data=df.to_dict('records'), page_size=10),
    dcc.Graph(figure=px.histogram(df, x='continent', y='lifeExp', histfunc='avg'))
], style={
    "maxWidth": "1140px",       # standard website width
    "margin": "0 auto",         # center horizontally
    "padding": "20px"           # optional inner spacing
})


# Run app
if __name__ == '__main__':
    app.run(debug=True)
