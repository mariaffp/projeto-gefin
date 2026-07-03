import dash
from dash import html, Input, Output, callback, dcc
import dash_bootstrap_components as dbc
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import request
from urllib.parse import parse_qs
from supabase_client import supabase
from services.usuario import buscar_perfil, eh_financeiro

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

#https://www.dash-bootstrap-components.com/docs/themes/explorer/
#abram esse link ^, vai ter cada elemento pra vcs explorarem, e cliquem no livro azul, eles te mandam direto para o docs daquele elemento em especifico

dash.register_page(__name__, path='/')

# peguei as cores no
# https://www.figma.com/design/wKQPYUQwRiwka37pbtDsEm/Focus-Identidade-Visual?node-id=10-1019&t=NDOww80xdSRGagDm-0
COR_BOTAO = "#0067EC"
COR_TEXTO_BRANCO = "#FFFFFF"
COR_DESTAQUE = "#9EBFE8"
COR_FUNDO_DIREITA = "#E4E4E4"

layout = html.Div(
    [
        dcc.Location(id="redirecionar", refresh=True),
        dcc.Location(id="url", refresh=False),
        html.Div(id="auth-check", style={"display": "none"}),
        dcc.Store(id="hcaptcha-token-store"),

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
                # caixa do login
                html.Div(
                    [
                        html.Div([
                            dbc.Label("E-mail", style={"fontWeight": "bold", "fontSize": "1.2rem", "color": "#000000"}),
                            dbc.Input(
                                id="input-email",
                                type="email",
                                placeholder="  Digite seu e-mail",
                                className="mb-4 py-2",
                                style={"borderRadius": "4px"}
                            ),
                            dbc.Label("Senha", style={"fontWeight": "bold", "fontSize": "1.2rem", "color": "#000000"}),
                            dbc.Input(
                                id="input-senha",
                                type="password",
                                placeholder="  Digite sua senha aqui",
                                className="mb-4 py-2",
                                style={"borderRadius": "4px"}
                            ),
                        ]
                        ),
                        html.Div(id="msg-erro", className="text-danger mb-2"),
                        html.Div([
                            dbc.Button(
                                "Acessar",
                                id="btn-entrar",
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
                                [
                                    html.Img(
                                        src="/assets/google.png",
                                        style={
                                            "width": "24px",
                                            "marginRight": "10px",
                                            "verticalAlign": "middle"
                                        }
                                    ),
                                    html.Span("Acessar utilizando Google")
                                ],
                                id="btn-google",
                                className="w-100",
                                style={
                                    "backgroundColor": COR_BOTAO,
                                    "borderColor": COR_BOTAO,
                                    "color": COR_TEXTO_BRANCO,
                                    "fontSize": "1.1rem",
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "center",
                                }
                            )
                        ])
                    ],

                    className="glass-box p-4 p-md-5 login-box",
                    style={
                        "backgroundColor": COR_FUNDO_DIREITA,
                        "padding": "40px",
                        "borderRadius": "12px",
                        "boxShadow": "0px 15px 35px rgba(0, 0, 0, 0.5)",
                        "width": "100%",
                        "maxWidth": "450px",
                        "marginLeft": "0",
                        "zIndex": 2
                    }
                ),

                # logo svg,
                html.ObjectEl(
                    data="/assets/Focus_consultoria.svg",
                    type="image/svg+xml",
                    style={
                        "width": "100%",
                        "maxWidth": "400px",
                        "maxHeight": "60vh",
                        "height": "auto",
                        "marginRight": "0",
                        "pointerEvents": "none",
                        "zIndex": 0
                    },
                    className="login-logo",
                )
            ],
            # w-100 e justify-content-between organizam o espaço horizontalmente
            className="d-flex align-items-center justify-content-between min-vh-100 w-100 login-main flex-column flex-lg-row",
            style={"position": "relative", "zIndex": 1, "padding": "24px 48px", "gap": "24px"}
        )
    ],
    style={"fontFamily": "'Trade Gothic Next SR Pro Regular', sans-serif"}
)

#callback do login, sempre que o usuario clicar no botao de acesso, o dash captura esses valores e executa a função
@callback(
    Output("msg-erro", "children"),
    Output("redirecionar", "pathname", allow_duplicate=True),
    Input("btn-entrar", "n_clicks"),
    Input("input-email", "value"),
    Input("input-senha", "value"),
    prevent_initial_call=True
)
def login_email(n_clicks, email, senha):
    if not n_clicks:
        return "",dash.no_update
    try: #tenta enviar as credenciais pro supabase autenticar
        resposta = supabase.auth.sign_in_with_password({"email": email, "password": senha})
       
        #buscando perfil do usuario
        user_id = resposta.user.id
        perfil = buscar_perfil(user_id)

        return "","/dashboard" #se der certo, redireciona para a pagina principal do sistema
    except Exception as e:
        return "E-mail ou senha incorretos.", dash.no_update #tratamento de erro, caso nao encontre o login

#callback responsável pelo login via google
#quando o botao for clicado, o supabase ger uma URL de autenticacao e redireciona o usuario para ela
@callback(
    Output("redirecionar", "href"),
    Input("btn-google", "n_clicks"),
    prevent_initial_call=True
)
def login_google(n_clicks):
    if not n_clicks:
        return dash.no_update

    try: #solicita ao supabase o inicio do fluxo oauth com o google
        redirect_url = f"http://{request.host}"
        response = supabase.auth.sign_in_with_oauth(
            {"provider": "google",
            "options":{"redirect_to": redirect_url}}
        )
        return response.url #redireciona o navegador para a pag de autenticação
    except Exception as e:
        print("ERRO GOOGLE:", e)
        return dash.no_update

#Após autenticacao com o google,o usuario retorna para a aplicação, mas esse callback verifica se o codigo de auth foi recebido
@callback(
    Output("redirecionar", "pathname", allow_duplicate=True),
    Input("redirecionar", "search"),
    prevent_initial_call=True
)
def redirecionar_apos_google(search):
    if search and "code=" in search:
        try:
            # Extrai o code da URL
            code = search.split("code=")[1].split("&")[0]
            
            # Troca o code pela sessão
            resposta = supabase.auth.exchange_code_for_session({"auth_code": code})
            
            # Busca o perfil e redireciona
            user_id = resposta.user.id
            perfil = buscar_perfil(user_id)
            return "/dashboard"

        except Exception as e:
            print("ERRO ao trocar code:", e)
            return "/"
    return dash.no_update
