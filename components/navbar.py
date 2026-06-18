import dash_bootstrap_components as dbc
from dash import html

def render_navbar():
    return dbc.Navbar(
        dbc.Container(
            [
                # Canto Esquerdo: Ícone SVG + Nome do sistema (ambos clicáveis para voltar ao Dashboard)
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Img(
                                    src="/assets/focus_sem_logos.svg",
                                    height="40px",
                                    style={
                                        "transform": "scale(2.3) translateY(6px)",
                                        "transformOrigin": "left center",
                                        "marginRight": "50px",
                                        "zIndex": "1050",
                                        "position": "relative"
                                    }
                                ),
                                width="auto"
                            ),
                            dbc.Col(
                                dbc.NavbarBrand("GEFIN", className="text-white fw-bold")
                            ),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="/dashboard",
                    style={"textDecoration": "none"},
                ),

                # links das paginas
                dbc.Nav(
                    [
                        dbc.NavLink(
                            "Dashboard",
                            href="/dashboard",
                            active="exact",
                            className="text-white me-3 px-3", # 'px-3' adiciona preenchimento horizontal
                            style={
                                "backgroundColor": "#0132B9", # Cor solicitada
                                "borderRadius": "8px"         # Cantos arredondados no botão
                            }
                        ),
                        dbc.NavLink(
                            "Importação",
                            href="/importacao",
                            active="exact",
                            className="text-white px-3"
                        ),
                        dbc.NavLink(
                            "Transações",
                            href="/transacoes",
                            active="exact",
                            className="text-white px-3"
                        ),
                    ],
                    className="ms-auto",
                    navbar=True,
                ),
            ],
            fluid=True,
        ),
        color="primary",
        dark=True,
        # Adição de 'mt-3' e 'mx-3' (margens superior e laterais) para que o arredondamento fique visível contra o fundo da tela.
        className="shadow-sm mb-4 mt-3 mx-3",
        style={"borderRadius": "15px"} # Arredondamento do Navbar
    )