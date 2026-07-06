import dash
from dash import html, Input, Output, callback, dcc
import dash_bootstrap_components as dbc
from supabase_client import supabase, supabase_admin
from services.usuario import cadastrar_usuario, buscar_perfil, eh_financeiro, buscar_usuario, eh_admin
from urllib.parse import parse_qs

#https://www.dash-bootstrap-components.com/docs/themes/explorer/
#abram esse link ^, vai ter cada elemento pra vcs explorarem, e cliquem no livro azul, eles te mandam direto para o docs daquele elemento em especifico

dash.register_page(__name__, path='/admin/cadastro')

# https://www.figma.com/design/wKQPYUQwRiwka37pbtDsEm/Focus-Identidade-Visual?node-id=10-1019&t=NDOww80xdSRGagDm-0
COR_BOTAO = "#0067EC"
COR_TEXTO_BRANCO = "#FFFFFF"
COR_DESTAQUE = "#9EBFE8"
COR_FUNDO_DIREITA = "#E4E4E4"

ESTILO_LABEL = {
    "fontWeight": "600",
    "fontSize": "1rem",
    "color": COR_BOTAO,
    "marginTop": "12px",
    "marginBottom": "6px"
}

def obter_user_id_logado():
    session = supabase.auth.get_session()

    if session is None:
        raise Exception("Usuário não autenticado")

    return session.user.id

layout = html.Div(
    [
        dcc.Location(id="redirecionar-admin", refresh=True),
        dcc.Location(id="url", refresh=False),
        html.Div(id="auth-check", style={"display": "none"}),
        #dcc.Store(id="hcaptcha-token-store"),

        # fundo com o blur
        html.Div(
            style={
                "position": "fixed",
                "top": 0,
                "left": 0,
                "width": "100vw",
                "height": "100vh",
                "background": "linear-gradient(to bottom right, rgba(109, 237, 255, 0.6), rgba(171, 195, 255, 0.6)), url('/assets/focusbackground.png')",
                "backgroundSize": "cover",
                "backgroundPosition": "center",
                "filter": "blur(5px)",
                "transform": "scale(1.1)",
                "zIndex": -1,
            }
        ),

        # camda principal
        html.Div(
            [
                # caixa do cadastro
                html.Div(
                    [
                        html.Div([
                            html.H2(
                                "Cadastrar usuário",
                                className="text-center mb-2",
                                style={
                                    "color": COR_BOTAO,
                                    "fontWeight": "bold",
                                }
                            ),
                            html.P(
                                "Crie uma nova conta para acessar o sistema.",
                                className="text-center text-muted mb-4",
                            ),
                            dbc.Label("Nome",style=ESTILO_LABEL),
                            dbc.Input(
                                id="input-nome",
                                type="text",
                                className="mb-3 py-2",
                                style={"borderRadius": "6px"},
                                placeholder="Digite o nome do usuário"
                            ),
                            dbc.Label("Perfil", style=ESTILO_LABEL),
                            dbc.Select(
                                id="input-perfil",
                                options=[
                                    {"label": "Normal", "value": "NORMAL"},
                                    {"label": "Financeiro", "value": "FINANCEIRO"},
                                ],
                                value="NORMAL",
                                className="mb-3",
                                style={
                                    "color": COR_BOTAO,
                                    "height": "48px",
                                    "borderRadius": "6px",
                                }
                            ),
                            dbc.Label("E-mail", style=ESTILO_LABEL),
                            dbc.Input(
                                id="input-email",
                                type="email",
                                placeholder="  Digite o e-mail",
                                className="mb-4 py-2",
                                style={"borderRadius": "6px"}
                            ),
                            dbc.Label("Senha", style=ESTILO_LABEL),
                            dbc.Input(
                                id="input-senha",
                                type="password",
                                placeholder="  Digite a senha escolhida",
                                className="mb-4 py-2",
                                style={"borderRadius": "6px"}
                            ),
                        ]
                        ),
                        html.Div(id="msg-erro-admin", className="text-danger mb-2"),
                        html.Div([
                            dbc.Button(
                                "Cadastrar",
                                id="btn-cadastrar",
                                className="w-100 mb-3 py-2",
                                style={
                                    "backgroundColor": COR_BOTAO,
                                    "borderColor": COR_BOTAO,
                                    "color": COR_TEXTO_BRANCO,
                                    "fontSize": "1.1rem"
                                }
                            ),
                            html.Div(
                                [
                                    html.Hr(style={"flex": "1", "borderColor": "#666"}),
                                    html.Span("OU", style={"padding": "0 15px", "fontSize": "1.1rem"}),
                                    html.Hr(style={"flex": "1", "borderColor": "#666"}),
                                ],
                                className="d-flex align-items-center mb-3"
                            ),
                            dbc.Button(
                                "Voltar para a página inicial",
                                id="btn-voltar-inicio",
                                className="w-100 py-2",
                                style={
                                    "backgroundColor": COR_DESTAQUE,
                                    "borderColor": COR_DESTAQUE,
                                    "color": COR_TEXTO_BRANCO,
                                    "fontSize": "1.1rem"
                                }
                            ),
                        ])
                    ],

                    className="glass-box p-5",
                    style={
                        "backgroundColor": COR_FUNDO_DIREITA,
                        "padding": "40px",
                        "borderRadius": "12px",
                        "boxShadow": "0px 15px 35px rgba(0, 0, 0, 0.5)",
                        "width": "100%",
                        "maxWidth": "450px",
                        "marginLeft": "8vw",
                        "zIndex": 2
                    }
                ),

            ],
            # w-100 e justify-content-between organizam o espaço horizontalmente
            className="d-flex align-items-center justify-content-between w-100",
            style={"position": "relative", "zIndex": 1,"minHeight": "calc(100vh - 90px)"}
        )
    ],
    style={"fontFamily": "'Trade Gothic Next SR Pro Regular', sans-serif"}
)
@callback(
    Output("redirecionar-admin", "pathname"),
    Input("btn-voltar-inicio", "n_clicks"),
    prevent_initial_call=True
)
def voltar_dashboard(n):
    if n:
        return "/admin"
    return dash.no_update

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
        #return "Preencha todos os campos.", dash.no_update
        return (
            "Preencha todos os campos.",
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update
)

    try:
        admin_id = obter_user_id_logado()

        sucesso = cadastrar_usuario(
        email,
        senha,
        nome,
        perfil,
        admin_id=admin_id
        )
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
