import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")

from dash import Dash, html, dcc, Input, Output, callback
import dash
import dash_bootstrap_components as dbc
from supabase_client import supabase
from components.navbar import create_navbar, create_mobile_navbar
from services.usuario import buscar_perfil, eh_financeiro, buscar_usuario, eh_admin
from flask import request, redirect

app = Dash(__name__, use_pages= True, external_stylesheets=[dbc.themes.ZEPHYR, "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"], suppress_callback_exceptions=True) # tema zephyr
server = app.server

@server.before_request
def checar_permissao_antes_de_carregar():
    pathname = request.path  # pega a URL que está sendo acessada, ex: "/admin"

    paginas_publicas = ["/", "/login"]
    if pathname in paginas_publicas:
        return None  # deixa passar normal, sem checagem

    # Ignora chamadas internas do Dash (assets, callbacks, etc) - não são "páginas" de verdade
    if pathname.startswith("/_dash") or pathname.startswith("/assets"):
        return None

    session = supabase.auth.get_session()
    if session is None:
        return redirect("/")  # bloqueia AQUI, antes do Dash processar

    usuario = buscar_usuario(session.user.id)
    perfil = usuario["perfil"] if usuario else buscar_perfil(session.user.id)

    paginas_financeiro = ["/transacoes", "/importacao"]
    if pathname in paginas_financeiro and not eh_financeiro(perfil):
        return redirect("/dashboard")

    if pathname.startswith("/admin") and not eh_admin(perfil):
        return redirect("/dashboard")

    return None  # tudo certo, deixa passar

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="global-navbar-container"),
    html.Div(id="mobile-navbar-container"),
    html.Div(id="auth-check"),
    html.Div(dash.page_container, id="page-content-wrapper")
])
@app.callback(
    Output("page-content-wrapper", "style"),
    Input("url", "pathname")
)
def ajustar_padding(pathname):
    paginas_publicas = ["/", "/login"]
    if pathname in paginas_publicas:
        return {"paddingTop": "0px"}
    return {"paddingTop": "90px"}


@app.callback(
    [Output("auth-check", "children"),
    Output("global-navbar-container", "children"),
    Output("mobile-navbar-container", "children")],
    [Input("url", "pathname"),
    Input("url", "search")]
)

def verificar_autenticacao(pathname, search):
    paginas_publicas = ["/", "/login"]
    if pathname in paginas_publicas:
        return "", "", ""
    
    session = supabase.auth.get_session()
    if session is None:
        return dcc.Location(href="/", id="redirecionar-auth", refresh=True), "", ""

    usuario = buscar_usuario(session.user.id)
    nome = usuario["nome"] if usuario else "Usuário"
    perfil = usuario["perfil"] if usuario else buscar_perfil(session.user.id)
    paginas_financeiro = ["/transacoes", "/importacao", "/logs"]
    
    if pathname in paginas_financeiro and not eh_financeiro(perfil):
        return dcc.Location(href="/dashboard", id="redirecionar-perfil", refresh=True), create_navbar(perfil), create_mobile_navbar(perfil)
        
    #paginas_admin = ["/admin"]

    if pathname.startswith("/admin") and not eh_admin(perfil):
        return (
            dcc.Location(
                href="/dashboard",
                id="redirecionar-admin",
                refresh=True
            ),
            create_navbar(perfil, nome), create_mobile_navbar(perfil,nome)
    )
    return "", create_navbar(perfil, nome), create_mobile_navbar(perfil,nome)


if __name__ == "__main__":
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        lan_ip = s.getsockname()[0]
        s.close()
    except Exception:
        lan_ip = "SEU_IP_LOCAL"
    
    port = int(os.environ.get("PORT", 8050))

    print(f" desktop:  http://localhost:{port}")
    print(f" celular: http://{lan_ip}:{port}")

    app.run(debug=True, host="0.0.0.0", port=port)
