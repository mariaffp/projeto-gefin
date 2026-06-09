import dash
from dash import html, Input, Output, callback, dcc
import dash_bootstrap_components as dbc
from supabase_client import supabase

#https://www.dash-bootstrap-components.com/docs/themes/explorer/
#abram esse link ^, vai ter cada elemento pra vcs explorarem, e cliquem no livro azul, eles te mandam direto para o docs daquele elemento em especifico

dash.register_page(__name__, path='/')

# peguei as cores no
# https://www.figma.com/design/wKQPYUQwRiwka37pbtDsEm/Focus-Identidade-Visual?node-id=10-1019&t=NDOww80xdSRGagDm-0
COR_BOTAO = "#0067EC"
COR_TEXTO_BRANCO = "#FFFFFF"
COR_DESTAQUE = "#9EBFE8"
COR_FUNDO_DIREITA = "#E4E4E4"

layout = dbc.Container(
    [dcc.Location(id="redirecionar", refresh=True),
    dcc.Location(id="redirecionar-email", refresh=True),
        dbc.Row(
            [
                # lado esquerdo apresentacao (ocupa 6 de 12 colunas)
                dbc.Col(
                    [
                        html.Div(
                            [   # doc HTML Elements: https://dash.plotly.com/dash-html-componen
                                html.H1(
                                    "BEM VINDO AO SISTEMA DE\nGERENCIAMENTO\nFINANCEIRO GEFIN",
                                    style={
                                        "whiteSpace": "pre-line",
                                        "fontWeight": "bold",
                                        "color": COR_TEXTO_BRANCO,
                                        "fontSize": "2.5rem"
                                    }
                                ),
                                html.Img(
                                    src="/assets/gefin1.png",
                                    style={
                                        "marginTop": "80px",
                                        "width": "480px",
                                        "display": "block",
                                        "margin": "60px auto 0 auto"
                                    }
                                )
                            ],
                            style={"maxWidth": "80%"}
                        )
                    ],
                    md=6,
                    className="d-flex flex-column justify-content-center align-items-center vh-100",
                    style={"backgroundColor": COR_BOTAO}
                ),

                # lado direito formulario (ocupa 6 de 12 colunas)
                dbc.Col(
                    [
                        html.Div(
                            [   # inputs de email e senha
                                # doc de i  nputs: https://www.dash-bootstrap-components.com/docs/components/input/
                                html.Div([
                                    dbc.Label("E-mail", style={"fontWeight": "bold", "fontSize": "1.2rem"}),
                                    dbc.Input(
                                        id="input-email",
                                        type="email",
                                        placeholder="🧑🏻‍💻 Digite seu e-mail",
                                        className="mb-4 py-2",
                                        style={"borderRadius": "4px"}
                                    ),
                                    dbc.Label("Senha", style={"fontWeight": "bold", "fontSize": "1.2rem"}),
                                    dbc.Input(
                                        id="input-senha",
                                        type="password",
                                        placeholder="🔐 Digite sua senha aqui",
                                        className="mb-4 py-2",
                                        style={"borderRadius": "4px"}
                                    ),
                                ]),

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
                                    # linha do "OU"
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
                            style={"width": "100%", "maxWidth": "450px"}
                        )
                    ],
                    md=6,
                    className="d-flex justify-content-center align-items-center vh-100",
                    style={"backgroundColor": COR_FUNDO_DIREITA}
                )
            ],
            className="m-0"
        )
    ],
    fluid=True,
    className="p-0",
    style={"fontFamily": "'Trade Gothic Next SR Pro Regular', sans-serif"}
)

#callback do login, sempre que o usuario clicar no botao de acesso, o dash captura esses valores e executa a função
@callback(
    Output("msg-erro", "children"),
    Output("redirecionar-email", "pathname"),
    Input("btn-entrar", "n_clicks"),
    Input("input-email", "value"),
    Input("input-senha", "value"),
    prevent_initial_call=True
)
def login_email(n_clicks, email, senha):
    if not n_clicks:
        return "",dash.no_update
    try: #tenta enviar as credenciais pro supabase autenticar
        supabase.auth.sign_in_with_password({"email": email, "password": senha})
        return "","/dashboard" #se der certo, redireciona para a pagina principal do sistema
    except Exception as e:
        return "E-mail ou senha incorretos.", dash.no_update #tratamento de erro, caso nao encontre o login

#callback responsável pelo login via google
#quando o botao for clicado, o supabase ger uma URL de autenticacao e redireciona o usuario para ela
@callback(
    #Output("btn-google", "disabled"),
    Output("redirecionar", "href"),
    Input("btn-google", "n_clicks"),
    prevent_initial_call=True
)
def login_google(n_clicks):
    if not n_clicks:
        #return False
        return dash.no_update
    #response = supabase.auth.sign_in_with_oauth(
        #{"provider": "google"},
        #options={"redirect_to": "http://localhost:8050"})
    #print("URL Google:", response.url)
    try: #solicita ao supabase o inicio do fluxo oauth com o google
        response = supabase.auth.sign_in_with_oauth(
            {"provider": "google",
            "options":{"redirect_to": "http://localhost:8050"}}
        )
        return response.url #redireciona o navegador para a pag de autenticação
    except Exception as e:
        print("ERRO GOOGLE:", e)
        return dash.no_update
    #return response.url

#Após autenticacao com o google,o usuario retorna para a aplicação, mas esse callback verifica se o codigo de auth foi recebido
@callback(
    Output("redirecionar", "pathname"),
    Input("redirecionar", "search"),
    prevent_initial_call=True
)
def redirecionar_apos_google(search):
    if search and "code=" in search: #verifica se o login foi concluido
        return "/dashboard" #redireciona para a pagina principal do sistema
    return dash.no_update #se nao tem codigo valido, nao faz nada