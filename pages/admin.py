import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/admin')

COR_BOTAO = "#0067EC"
COR_TEXTO_BRANCO = "#FFFFFF"

layout = dbc.Container([
    html.H2("Painel Admin", className="fw-normal text-dark my-4"),

    dbc.Row([
        dbc.Col([
            dcc.Link(
                dbc.Card([
                    dbc.CardBody([
                        html.Div(
                            html.I(className="bi bi-person-plus-fill",
                                   style={"fontSize": "2rem", "color": COR_BOTAO}),
                            className="mb-3",
                        ),
                        html.H5("Cadastrar usuário", className="fw-bold mb-2"),
                        html.P("Crie uma nova conta para acessar o sistema.",
                               className="text-muted small mb-0"),
                    ]),
                ], className="shadow-sm h-100 admin-card"),
                href="/admin/cadastro",
                style={"textDecoration": "none", "color": "inherit"},
            ),
        ], xs=12, md=6, className="mb-3"),

        dbc.Col([
            dcc.Link(
                dbc.Card([
                    dbc.CardBody([
                        html.Div(
                            html.I(className="bi bi-people-fill",
                                   style={"fontSize": "2rem", "color": COR_BOTAO}),
                            className="mb-3",
                        ),
                        html.H5("Gerenciar usuários", className="fw-bold mb-2"),
                        html.P("Altere perfis e remova usuários cadastrados.",
                               className="text-muted small mb-0"),
                    ]),
                ], className="shadow-sm h-100 admin-card"),
                href="/admin/usuarios",
                style={"textDecoration": "none", "color": "inherit"},
            ),
        ], xs=12, md=6, className="mb-3"),
    ]),
], fluid=True, className="py-2")
