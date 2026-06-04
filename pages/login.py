import dash
from dash import html

dash.register_page(__name__, path="/")

layout = html.Div([
    html.H2(children="ola equipe"),
    html.Hr(),
])