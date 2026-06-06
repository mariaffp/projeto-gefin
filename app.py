from dash import Dash, html
import dash
import dash_bootstrap_components as dbc
import os
from dotenv import load_dotenv

load_dotenv()

app = Dash(__name__, use_pages= True, external_stylesheets=[dbc.themes.ZEPHYR]) # tema zephyr
server = app.server

app.layout = html.Div([
     dash.page_container
])

if __name__ == "__main__":
    app.run(debug=True)
