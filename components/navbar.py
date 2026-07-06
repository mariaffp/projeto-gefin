import dash_bootstrap_components as dbc
from dash import html, Input, Output, State, callback, dcc

# Baseado nesse modelo https://www.dash-bootstrap-components.com/docs/components/navbar/

#def create_navbar():
def create_navbar(perfil="NORMAL", nome="Usuário"):
    # Navigation Links (inside dbc.Nav)
    nav_links = [
        dbc.NavItem(dbc.NavLink("Página Inicial", href="/dashboard", active="exact", className="glass-nav-link px-3")),
        dbc.NavItem(dbc.NavLink("Relatórios", href="/relatorios", active="exact", className="glass-nav-link px-3")),
    ]
    if perfil in ["FINANCEIRO", "ADMIN"]:
        nav_links.extend([
            dbc.NavItem(dbc.NavLink("Transações", href="/transacoes", active="exact", className="glass-nav-link px-3")),
            dbc.NavItem(dbc.NavLink("Importação", href="/importacao", active="exact", className="glass-nav-link px-3")),
            dbc.NavItem(dbc.NavLink("Logs do Sistema", href="/logs", active="exact", className="glass-nav-link px-3")),
        ])

    if perfil == "ADMIN":
        nav_links.append(
            dbc.NavItem(dbc.NavLink("Admin", href="/admin", active="exact", className="glass-nav-link px-3"))
        )

    navbar = dbc.Navbar(
        dbc.Container(
            [
                # logo
                html.A(
                    html.Img(src="/assets/Focus_consultoria.svg", height="45px"),
                    href="/dashboard",
                    className="navbar-brand me-4"   
                ),
                
                # navbar mobile
                dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                
                # menu colapsavel
                dbc.Collapse(
                    [
                        dbc.Nav(
                            nav_links,
                            className="me-auto align-items-center",
                            navbar=True,
                        ),
                        # perfil e botao de sair
                        html.Div(
                            [
                                html.Span(f"{nome}", className="glass-nav-text mx-3"),
                                dbc.Button("Sair", id="btn-logout", color="primary", size="sm", outline=True, className="glass-btn"),
                                dcc.Location(id="logout-redirect", refresh=True)
                            ],
                            className="d-flex align-items-center mt-2 mt-lg-0"
                        ),
                    ],
                    id="navbar-collapse",
                    is_open=False,
                    navbar=True,
                ),
            ],
            fluid=True,
        ),
        color="transparent",  
        dark=False,
        #className="glass-navbar mx-auto",
        className="glass-navbar",
        style={
            "width": "90%",
            "maxWidth": "1200px",
            "borderRadius": "16px",
            "padding": "10px 20px",
            "marginTop": "16px"
        }
    )
    
    return navbar


def create_mobile_navbar(perfil="NORMAL", nome="Usuário"):
    itens = [
        {"href": "/dashboard", "icon": "bi-house-fill", "label": "Início"},
        {"href": "/relatorios", "icon": "bi-bar-chart-fill", "label": "Relatórios"},
    ]
    if perfil in ["FINANCEIRO", "ADMIN"]:
        itens.extend([
            {"href": "/transacoes", "icon": "bi-currency-exchange", "label": "Transações"},
            {"href": "/importacao", "icon": "bi-cloud-arrow-up-fill", "label": "Importar"},
        ])

    nav_items = []
    for item in itens:
        nav_items.append(
            dbc.NavLink(
                [
                    html.I(className=f"bi {item['icon']}"),
                    html.Span(item["label"], className="mobile-nav-label"),
                ],
                href=item["href"],
                active="exact",
                className="mobile-nav-item",
            )
        )

    # botão "Mais" — abre o menu flutuante glass acima da navbar
    nav_items.append(
        html.Button(
            [
                html.I(className="bi bi-grid-fill"),
                html.Span("Mais", className="mobile-nav-label"),
            ],
            id="mobile-btn-mais",
            className="mobile-nav-item mobile-nav-mais",
            n_clicks=0,
        )
    )

    # itens do menu flutuante (Mais)
    menu_items = []
    if perfil in ["FINANCEIRO", "ADMIN"]:
        menu_items.append(
            dcc.Link(
                [
                    html.I(className="bi bi-journal-text"),
                    html.Span("Logs do Sistema"),
                ],
                href="/logs",
                className="mobile-menu-item",
            )
        )
    if perfil == "ADMIN":
        menu_items.append(
            dcc.Link(
                [
                    html.I(className="bi bi-shield-lock-fill"),
                    html.Span("Painel Admin"),
                ],
                href="/admin",
                className="mobile-menu-item",
            )
        )

    menu_items.append(
        html.Button(
            [
                html.I(className="bi bi-box-arrow-right"),
                html.Span("Sair"),
            ],
            id="mobile-btn-logout",
            className="mobile-menu-item mobile-menu-logout",
            n_clicks=0,
        )
    )

    # backdrop invisível pra fechar ao clicar fora
    backdrop = html.Div(
        id="mobile-menu-backdrop",
        className="mobile-menu-backdrop",
        n_clicks=0,
        style={"display": "none"},
    )

    # menu flutuante glass (acima da navbar)
    menu = html.Div(
        menu_items,
        id="mobile-menu-flutuante",
        className="mobile-menu-flutuante",
        style={"display": "none"},
    )

    return html.Nav(
        [
            dcc.Location(id="mobile-logout-redirect", refresh=True),
            backdrop,
            menu,
            *nav_items,
        ],
        className="mobile-bottom-nav",
        id="mobile-navbar",
    )


@callback(
    Output("navbar-collapse", "is_open"),
    Input("navbar-toggler", "n_clicks"),
    State("navbar-collapse", "is_open"),
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@callback(
    Output("logout-redirect", "href"),
    Input("btn-logout", "n_clicks"),
    prevent_initial_call=True
)
def fazer_logout(n_clicks):
    from supabase_client import supabase
    supabase.auth.sign_out()
    return "/"

@callback(
    Output("mobile-menu-flutuante", "style"),
    Output("mobile-menu-backdrop", "style"),
    Input("mobile-btn-mais", "n_clicks"),
    Input("mobile-menu-backdrop", "n_clicks"),
    State("mobile-menu-flutuante", "style"),
    prevent_initial_call=True
)
def toggle_mobile_menu(n_mais, n_backdrop, style_atual):
    import dash
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    visivel = style_atual.get("display") == "flex" if style_atual else False

    # clicou no backdrop -> fecha sempre
    if triggered_id == "mobile-menu-backdrop":
        return {"display": "none"}, {"display": "none"}

    # clicou no botão Mais -> toggle
    if triggered_id == "mobile-btn-mais":
        if visivel:
            return {"display": "none"}, {"display": "none"}
        return {"display": "flex"}, {"display": "block"}

    return dash.no_update, dash.no_update

@callback(
    Output("mobile-logout-redirect", "href"),
    Input("mobile-btn-logout", "n_clicks"),
    prevent_initial_call=True
)
def fazer_logout_mobile(n_clicks):
    from supabase_client import supabase
    supabase.auth.sign_out()
    return "/"