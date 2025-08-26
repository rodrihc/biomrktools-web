# pages/survival_analysis.py

from dash import html, dcc, Input, Output, callback
import pandas as pd
import numpy as np
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
import plotly.graph_objects as go

# Example survival data (hardcoded)
np.random.seed(42)
n = 100
df_survival = pd.DataFrame({
    "time": np.random.exponential(scale=10, size=n).round(1),
    "event": np.random.binomial(1, 0.7, size=n),
    "group": np.random.choice(["High expression", "Low expression"], size=n)
})

layout = html.Div([
    html.H3("Survival Analysis"),
    dcc.Graph(id="km-plot"),
    html.Div(id="logrank-result", style={"marginTop": "10px"})
])


@callback(
    Output("km-plot", "figure"),
    Output("logrank-result", "children"),
    Input("km-plot", "id")
)
def update_km_plot(_):
    kmf = KaplanMeierFitter()
    fig = go.Figure()

    group_dfs = {
        name: group for name, group in df_survival.groupby("group")
    }

    for name, group in group_dfs.items():
        kmf.fit(group["time"], event_observed=group["event"], label=name)
        fig.add_trace(go.Scatter(
            x=kmf.survival_function_.index,
            y=kmf.survival_function_[name],
            mode="lines",
            name=name
        ))

    # Log-rank test (only works for exactly 2 groups)
    if len(group_dfs) == 2:
        (name1, df1), (name2, df2) = list(group_dfs.items())
        result = logrank_test(
            df1["time"], df2["time"],
            event_observed_A=df1["event"],
            event_observed_B=df2["event"]
        )
        p_text = f"Log-rank p-value between {name1} and {name2}: {result.p_value:.4f}"
    else:
        p_text = "Log-rank test only shown for 2 groups."

    fig.update_layout(
        title="Kaplan–Meier Survival Curve",
        xaxis_title="Time",
        yaxis_title="Survival Probability",
        template="plotly_dark",
        height=500
    )

    return fig, p_text
