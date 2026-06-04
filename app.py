from dash import Dash, html
import dash
import os
from dotenv import load_dotenv

load_dotenv()

app = Dash(__name__, use_pages= True)
server = app.server

app.layout = html.Div([
    html.Div("GEFIN", style={'text-align': 'center', 'padding-top': '10px', 'background-color': 'white'}),
    dash.page_container
])

if __name__ == "__main__":
    app.run(debug=True)
