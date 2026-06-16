import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/teste')

layout = dbc.Container([
    html.H1("Dashboard", className="text-center mt-5"),   
    html.P("Lorem ipsum dolor sit amet consectetur, adipisicing elit. Enim quidem aliquid fugiat corrupti, ipsa beatae veritatis rem impedit aspernatur! Aliquam molestiae a rerum nisi, possimus saepe quod assumenda porro maiores?", className="text-center"),
])   