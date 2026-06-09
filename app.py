from dash import Dash, html, dcc, Input, Output, callback
import dash
import dash_bootstrap_components as dbc
import os
from dotenv import load_dotenv
from supabase_client import supabase

load_dotenv()

app = Dash(__name__, use_pages= True, external_stylesheets=[dbc.themes.ZEPHYR]) # tema zephyr
server = app.server

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="auth-check"),
     dash.page_container
])
@app.callback(
    Output("auth-check", "children"),
    Input("url", "pathname"),
    Input("url", "search")
)
def verificar_autenticacao(pathname,search):
    paginas_publicas = ["/", "/login"]
    if pathname in paginas_publicas:
        return ""
    if search and "code=" in search:
        return ""#dcc.Location(href="/", id="redirecionar-auth", refresh=True)
    session = supabase.auth.get_session()
    if session is None:
        return dcc.Location(href="/", id="redirecionar-auth", refresh=True)
    return ""

if __name__ == "__main__":
    app.run(debug=True)
