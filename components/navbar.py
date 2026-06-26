import dash_bootstrap_components as dbc
from dash import html, Input, Output, State, callback, dcc

# Baseado nesse modelo https://www.dash-bootstrap-components.com/docs/components/navbar/

#def create_navbar():
def create_navbar(perfil="NORMAL"):
    # Navigation Links (inside dbc.Nav)
    nav_links = [
        dbc.NavItem(dbc.NavLink("Página Inicial", href="/dashboard", active="exact", className="glass-nav-link px-3")),
        dbc.NavItem(dbc.NavLink("Relatórios", href="/relatorios", active="exact", className="glass-nav-link px-3")),
    ]
    if perfil in ["FINANCEIRO", "ADMIN"]:
        nav_links.extend([
            dbc.NavItem(dbc.NavLink("Transações", href="/transacoes", active="exact", className="glass-nav-link px-3")),
            dbc.NavItem(dbc.NavLink("Importação", href="/importacao", active="exact", className="glass-nav-link px-3")),
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
                                html.Span("Nome", className="glass-nav-text mx-3"),
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
        className="glass-navbar mx-auto mt-3",
        style={
            "width": "90%",
            "maxWidth": "1200px",
            "borderRadius": "16px",
            "padding": "10px 20px"
        }
    )
    
    return navbar



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