import dash_bootstrap_components as dbc
from dash import html, Input, Output, State, callback, dcc

# Baseado nesse modelo https://www.dash-bootstrap-components.com/docs/components/navbar/

#def create_navbar():
def create_navbar(perfil="NORMAL"):
   
    nav_content = dbc.Row(
        [
            # Logo e Links
            dbc.Col(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src="/assets/gefin1.png", height="30px"), width="auto", className="pe-3"),
                        dbc.Col(dbc.NavLink("Página Inicial", href="/dashboard", className="text-white pe-3")),
                    ] +
                    ([
                        dbc.Col(dbc.NavLink("Transações", href="/transacoes", className="text-white pe-3")),
                        dbc.Col(dbc.NavLink("Relatórios", href="/relatorios", className="text-white pe-3")),
                        dbc.Col(dbc.NavLink("Importação", href="/importacao", className="text-white")),
                    ] if perfil in ["FINANCEIRO", "ADMIN"] else []) +
                    ([
                        dbc.Col(dbc.NavLink("Admin", href="/admin", className="text-white pe-3")),
                    ] if perfil == "ADMIN" else []),
                    align="center",
                    className="g-0"
                ),
                className="flex-grow-1"
            ),
            
            # Bem vindo
            dbc.Col(
                html.Div(
                    [
                        html.Span("Bem vindo, Nome", className="text-white me-2"),
                        dbc.Button("Sair", id="btn-logout", color="light", size="sm", outline=True),
                        dcc.Location(id="logout-redirect", refresh=True)
                    ]
                ),
                width="auto",
                className="mt-2 mt-md-0"
            ),
        ],
        className="g-0 w-100 align-items-center",
    )

    
    navbar = dbc.Navbar(
        dbc.Container(
            [
                # Funcionabilidade pro mobile
                dbc.NavbarToggler(id="navbar-toggler", n_clicks=0, className="ms-auto me-2"),
                
                # Colapso
                dbc.Collapse(
                    nav_content,
                    id="navbar-collapse",
                    is_open=False,
                    navbar=True,
                    className="w-100"
                ),
            ],
            fluid=True,
        ),
        color="#1d6fcc",  
        dark=True,
        className="py-2",
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