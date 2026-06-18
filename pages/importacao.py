import dash
from components.navbar import render_navbar
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/importacao', name='Importação')

layout = dbc.Container([
    html.H2("Importação de Extratos", className="mt-4 mb-4"),

    # importar arquivos
    dbc.Card([
        dbc.CardBody([
            html.H5("Importar Novo Arquivo", className="card-title"),
            html.P("Selecione ou arraste o arquivo do extrato para importar os dados.",
                   className="card-text text-muted"),

            # upload
            dcc.Upload(
                id='upload-dados',
                children=html.Div([
                    'Arraste e solte ou ',
                    html.A('Selecione um Arquivo', className="fw-bold text-primary")
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '2px',
                    'borderStyle': 'dashed',
                    'borderRadius': '8px',
                    'textAlign': 'center',
                    'backgroundColor': '#f8f9fa',
                    'cursor': 'pointer'
                },
                multiple=False
            ),
        ])
    ], className="mb-4 shadow-sm"),

    #lista dos arquvios
    dbc.Card([
        dbc.CardHeader("Histórico de Importações", className="fw-bold"),
        dbc.ListGroup([
            #placeholder 1
            dbc.ListGroupItem([
                html.Div([
                    html.H6("extrato_maio_2026.csv", className="mb-1"),
                    html.Small("17/06/2026 - 16:20", className="text-muted"),
                ], className="d-flex w-100 justify-content-between"),
                html.Small("Status: Concluído", className="text-success fw-bold")
            ]),

            #placheholder 2
            dbc.ListGroupItem([
                html.Div([
                    html.H6("extrato_abril_2026.xlsx", className="mb-1"),
                    html.Small("17/05/2026 - 19:67", className="text-muted"),
                ], className="d-flex w-100 justify-content-between"),
                html.Small("Status: Concluído", className="text-success fw-bold")
            ]),
        ], flush=True)
    ], className="shadow-sm")

], fluid=True, className="p-4")
