import dash
from dash import html
import dash_bootstrap_components as dbc

# https://www.dash-bootstrap-components.com/docs/themes/explorer/
#abram esse link ^, vai ter cada elemento pra vcs explorarem, e cliquem no livro azul, eles te mandam direto para o docs daquele elemento em especifico


dash.register_page(__name__, path='/')

layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    #https://www.dash-bootstrap-components.com/docs/components/layout/
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    #https://www.dash-bootstrap-components.com/docs/components/card/
                                    [
                                        html.H3("GEFIN", className="text-center mb-4"),
                                        #https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/Heading_Elements

                                        dbc.Label("E-mail"),
                                        dbc.Input(type="email", placeholder="exemplo@focus.com", className="mb-3"),
                                        dbc.Label("Senha"),
                                        dbc.Input(type="password", placeholder="Sua senha", className="mb-4"),
                                        #https://www.dash-bootstrap-components.com/docs/components/input/
                                        # https://www.dash-bootstrap-components.com/docs/components/form/

                                        dbc.Button("Entrar", color="primary", className="w-100 mb-2"),
                                        dbc.Button("Entrar com Google", color="light", className="w-100"),
                                        dbc.NavLink("Redefinir senha", href="/login", className="nav-link"),
                                        #https://www.dash-bootstrap-components.com/docs/components/button/
                                    ]
                                )
                            ],
                            className="shadow",  # sombreamento na caixa
                            style={"width": "24rem", "border-radius": "10px"} #largura da caixa
                        )
                    ],
                    className="d-flex justify-content-center"  #alinha a caixa ao centro horizonalmente
                )
            ],
            className="align-items-center vh-100" #alinha ao centro verticalmente
        )
    ],
    fluid=True,
    style={"background-color": "#f4f6f8"}
)