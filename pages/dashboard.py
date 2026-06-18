import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/dashboard')

layout = dbc.Container([
    html.H1("Dashboard", className="text-center mt-5"),
    html.P("Bem-vindo ao GEFIN!", className="text-center"),

    #botao pra pagina
    html.Div([
        dbc.Button(
            "Importação de Extratos",
            href="/importacao",
            color="primary",
            className="mt-4"
        )
    ], className="text-center")
])