import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/admin')

COR_BOTAO = "#0067EC"
COR_TEXTO_BRANCO = "#FFFFFF"

layout = html.Div(
    [
        html.Div(
            style={
                "position": "fixed",
                "top": 0, "left": 0,
                "width": "100vw", "height": "100vh",
                "background": "linear-gradient(to bottom right, rgba(109, 237, 255, 0.6), rgba(171, 195, 255, 0.6)), url('/assets/focusbackground.png')",
                "backgroundSize": "cover",
                "backgroundPosition": "center",
                "filter": "blur(5px)",
                "transform": "scale(1.1)",
                "zIndex": -1,
            }
        ),
        html.Div(
            [
                html.H2("Painel Admin", className="text-center mb-4", style={"color": COR_BOTAO, "fontWeight": "bold"}),
                dcc.Link(
                    dbc.Button("Cadastrar usuário", className="w-100 mb-3 py-3",
                               style={"backgroundColor": COR_BOTAO, "borderColor": COR_BOTAO, "color": COR_TEXTO_BRANCO, "fontSize": "1.1rem"}),
                    href="/admin/cadastro"
                ),
                dcc.Link(
                    dbc.Button("Gerenciar usuários", className="w-100 py-3",
                               style={"backgroundColor": COR_BOTAO, "borderColor": COR_BOTAO, "color": COR_TEXTO_BRANCO, "fontSize": "1.1rem"}),
                    href="/admin/usuarios"
                ),
            ],
            className="glass-box p-5",
            style={
                "backgroundColor": "rgba(228, 228, 228, 0.5)",
                "borderRadius": "12px",
                "boxShadow": "0px 15px 35px rgba(0, 0, 0, 0.5)",
                "width": "100%", "maxWidth": "400px",
                "margin": "0 auto",
                "position": "relative", "zIndex": 2
            }
        )
    ],
    style={"minHeight": "calc(100vh - 90px)", "display": "flex", "alignItems": "center", "justifyContent": "center"}
)