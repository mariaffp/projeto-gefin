import dash
from dash import html
import dash_bootstrap_components as dbc

# https://www.dash-bootstrap-components.com/docs/themes/explorer/
#abram esse link ^, vai ter cada elemento pra vcs explorarem, e cliquem no livro azul, eles te mandam direto para o docs daquele elemento em especifico


dash.register_page(__name__, path='/')


# peguei as cores no
# https://www.figma.com/design/wKQPYUQwRiwka37pbtDsEm/Focus-Identidade-Visual?node-id=10-1019&t=NDOww80xdSRGagDm-0
COR_BOTAO = "#0067EC"
COR_TEXTO_BRANCO = "#FFFFFF"
COR_DESTAQUE = "#9EBFE8"
COR_FUNDO_DIREITA = "#E4E4E4"

layout = dbc.Container(
    [
        dbc.Row(
            [
                # lado esqsuerdo apresentacao (ocupa 6 de 12 colunas)
                dbc.Col(
                    [
                        html.Div(
                            [
                                # doc HTML Elements: https://dash.plotly.com/dash-html-components
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
                                        "margin": "60px auto 0 auto" #centraliza a imgem
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
                            [
                                # inputs de email e senha
                                # doc de i  nputs: https://www.dash-bootstrap-components.com/docs/components/input/
                                html.Div([
                                    dbc.Label("E-mail", style={"fontWeight": "bold", "fontSize": "1.2rem"}),
                                    dbc.Input(
                                        type="email",
                                        placeholder="🧑🏻‍💻 Digite seu e-mail",
                                        className="mb-4 py-2",
                                        style={"borderRadius": "4px"}
                                    ),

                                    dbc.Label("Senha", style={"fontWeight": "bold", "fontSize": "1.2rem"}),
                                    dbc.Input(
                                        type="password",
                                        placeholder="🔐 Digite sua senha aqui",
                                        className="mb-4 py-2",
                                        style={"borderRadius": "4px"}
                                    ),
                                ]),

                                # botões
                                # doc dos botoes: https://www.dash-bootstrap-components.com/docs/components/button/
                                html.Div([
                                    dbc.Button(
                                        "Acessar",
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
                                            html.Div(
                                                html.Img(
                                                    src="/assets/google.png",
                                                    style={
                                                        "width": "30px",

                                                    }
                                            ),
                                                style={
                                                    "padding": "1px",
                                                    "borderRadius": "2px",
                                                    "marginRight": "30px",
                                                    "display": "inline-block",
                                                    "position": "absolute",
                                                    "top": "500px",
                                                    "right": "520px"
                                                }
                                            ),
                                             html.Span("Acessar utilizando Google")
                                        ],
                                        className="w-100",
                                        style={
                                            "backgroundColor": COR_BOTAO,
                                            "borderColor": COR_BOTAO,
                                            "color": COR_TEXTO_BRANCO,
                                            "fontSize": "1.1rem",
                                            "alignItems": "center",
                                            "justifyContent": "center",
                                            "gap": "15px"

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