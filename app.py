from dash import Dash, html, dcc, Input, Output, callback
import dash
import dash_bootstrap_components as dbc
import os
from dotenv import load_dotenv
from supabase_client import supabase
from components.navbar import create_navbar
from services.usuario import buscar_perfil, eh_financeiro

load_dotenv()

app = Dash(__name__, use_pages= True, external_stylesheets=[dbc.themes.ZEPHYR, "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"], suppress_callback_exceptions=True) # tema zephyr
server = app.server

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="global-navbar-container"),
    html.Div(id="auth-check"),
    dash.page_container
])
@app.callback(
    [Output("auth-check", "children"),
    Output("global-navbar-container", "children")],
    [Input("url", "pathname"),
    Input("url", "search")]
)
#def verificar_autenticacao(pathname,search):
    #paginas_publicas = ["/", "/login"]
    #if pathname in paginas_publicas:
        #return "", ""
    #if search and "code=" in search:
        #return "", create_navbar() # dcc.Location(href="/", id="redirecionar-auth", refresh=True)
    #session = supabase.auth.get_session()
    #if session is None:
        #return dcc.Location(href="/", id="redirecionar-auth", refresh=True), ""
    #return "", create_navbar()
def verificar_autenticacao(pathname, search):
    paginas_publicas = ["/", "/login"]
    if pathname in paginas_publicas:
        return "", ""
    #if search and "code=" in search:
        #return "", ""
    session = supabase.auth.get_session()
    if session is None:
        return dcc.Location(href="/", id="redirecionar-auth", refresh=True), ""

    perfil = buscar_perfil(session.user.id)
    paginas_financeiro = ["/transacoes", "/relatorios", "/importacao"]
    if pathname in paginas_financeiro and not eh_financeiro(perfil):
        return dcc.Location(href="/dashboard", id="redirecionar-perfil", refresh=True), create_navbar(perfil)

    return "", create_navbar(perfil)

if __name__ == "__main__":
    app.run(debug=True)
