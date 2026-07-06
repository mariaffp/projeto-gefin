import dash
from dash import html, Input, Output, callback, dcc
import dash_bootstrap_components as dbc
from supabase_client import supabase
from services.usuario import cadastrar_usuario

dash.register_page(__name__, path='/admin/cadastro')

COR_BOTAO = "#0067EC"
COR_TEXTO_BRANCO = "#FFFFFF"


def obter_user_id_logado():
    session = supabase.auth.get_session()
    if session is None:
        raise Exception("Usuário não autenticado")
    return session.user.id


layout = dbc.Container([
    dcc.Location(id="redirecionar-admin", refresh=True),

    dbc.Row([
        dbc.Col([
            html.H2("Cadastrar Usuário", className="fw-normal text-dark my-4"),

            dbc.Card([
                dbc.CardBody([
                    html.P("Crie uma nova conta para acessar o sistema.",
                           className="text-muted mb-4"),

                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Nome", className="fw-semibold"),
                            dbc.Input(
                                id="input-nome",
                                type="text",
                                placeholder="Digite o nome do usuário",
                                className="mb-3",
                            ),
                        ], md=6),
                        dbc.Col([
                            dbc.Label("Perfil", className="fw-semibold"),
                            dbc.Select(
                                id="input-perfil",
                                options=[
                                    {"label": "Normal", "value": "NORMAL"},
                                    {"label": "Financeiro", "value": "FINANCEIRO"},
                                    {"label": "Admin", "value": "ADMIN"},
                                ],
                                value="NORMAL",
                                className="mb-3",
                            ),
                        ], md=6),
                    ]),

                    dbc.Row([
                        dbc.Col([
                            dbc.Label("E-mail", className="fw-semibold"),
                            dbc.Input(
                                id="input-email",
                                type="email",
                                placeholder="Digite o e-mail",
                                className="mb-3",
                            ),
                        ], md=6),
                        dbc.Col([
                            dbc.Label("Senha", className="fw-semibold"),
                            dbc.Input(
                                id="input-senha",
                                type="password",
                                placeholder="Digite a senha escolhida",
                                className="mb-3",
                            ),
                        ], md=6),
                    ]),

                    html.Div(id="msg-erro-admin", className="mb-3"),

                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                dbc.Button(
                                    "Cadastrar",
                                    id="btn-cadastrar",
                                    color="primary",
                                    className="me-2",
                                    style={
                                        "backgroundColor": COR_BOTAO,
                                        "borderColor": COR_BOTAO,
                                    },
                                ),
                                dcc.Link(
                                    dbc.Button("Voltar", color="secondary", outline=True),
                                    href="/admin",
                                    style={"textDecoration": "none"},
                                ),
                            ], className="d-flex flex-wrap gap-2")
                        ], width=12),
                    ]),
                ]),
            ], className="shadow-sm"),
        ], md=10, lg=8),
    ]),
], fluid=True, className="py-2")


@callback(
    Output("msg-erro-admin", "children"),
    Output("redirecionar-admin", "href"),
    Output("input-nome", "value"),
    Output("input-email", "value"),
    Output("input-senha", "value"),
    Output("input-perfil", "value"),
    Input("btn-cadastrar", "n_clicks"),
    [
        dash.dependencies.State("input-nome", "value"),
        dash.dependencies.State("input-email", "value"),
        dash.dependencies.State("input-senha", "value"),
        dash.dependencies.State("input-perfil", "value"),
    ],
    prevent_initial_call=True
)
def callback_cadastrar_usuario(n_clicks, nome, email, senha, perfil):
    if not all([nome, email, senha, perfil]):
        return (
            "Preencha todos os campos.",
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update
        )

    try:
        sucesso = cadastrar_usuario(email, senha, nome, perfil)
        if sucesso:
            return (
                "Usuário cadastrado com sucesso!",
                dash.no_update,
                "",
                "",
                "",
                "NORMAL"
            )
        else:
            return (
                "Erro ao cadastrar usuário.",
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update
            )
    except Exception as e:
        return (
            f"Erro ao cadastrar usuário: {str(e)}",
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update
        )
