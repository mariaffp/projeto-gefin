import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/transacoes', name='Transações')

layout = dbc.Container([
    dbc.Row(
        dbc.Col(
            html.H2("Gerenciamento de Transações", className="fw-normal text-dark"),
            width="auto"
        ),
        className="my-4 align-items-center"
    ),

        #filtros.
        dbc.Card([
            dbc.CardBody([
                html.H5("Filtros de Busca", className="card-title mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Descrição"),
                        dbc.Input(placeholder="Buscar por palavra-chave...", type="text"),
                    ], md=4),

                    dbc.Col([
                        dbc.Label("Tipo"),
                        dbc.Select(
                            options=[
                                {"label": "Todos", "value": "todos"},
                                {"label": "Receita", "value": "receita"},
                                {"label": "Despesa", "value": "despesa"},
                            ],
                            value="todos"
                        ),
                    ], md=2),

                    dbc.Col([
                        dbc.Label("Data Inicial"),
                        dbc.Input(type="date"),
                    ], md=3),

                    dbc.Col([
                        dbc.Label("Data Final"),
                        dbc.Input(type="date"),
                    ], md=3),
                ], className="g-3"),
            ])
        ], className="mb-4 shadow-sm"),

        # botoes
        dbc.Row([
            dbc.Col([
                dbc.Button("Nova Transação", color="success", className="me-2 shadow-sm fw-bold"),
                dbc.Button("Editar", color="warning", className="me-2 text-white shadow-sm fw-bold"),
                dbc.Button("Excluir", color="danger", className="shadow-sm fw-bold"),
            ], width=12, className="mb-3 d-flex justify-content-start")
        ]),

        # tabela das transacoes
        dbc.Card([
            dbc.CardHeader("Registros Encontrados", className="fw-bold"),
            dbc.Table([
                html.Thead(
                    html.Tr([
                        html.Th("", style={"width": "40px"}),
                        html.Th("Data"),
                        html.Th("Descrição"),
                        html.Th("Categoria"),
                        html.Th("Valor"),
                        html.Th("Status")
                    ])
                ),
                html.Tbody([
                    # placeholder 1
                    html.Tr([
                        html.Td(dbc.Checkbox(value=False)),
                        html.Td("18/06/2026"),
                        html.Td("WebApp de Gerenciamento Financeiro"),
                        html.Td("Serviços"),
                        html.Td("R$ 9.000,00", className="text-success fw-bold"),
                        html.Td(dbc.Badge("Recebido", color="success"))
                    ]),
                    # placeholder 2
                    html.Tr([
                        html.Td(dbc.Checkbox(value=False)),
                        html.Td("15/06/2026"),
                        html.Td("Infraestrutura do Supabase"),
                        html.Td("Servidores"),
                        html.Td("- R$ 100,00", className="text-danger fw-bold"),
                        html.Td(dbc.Badge("Pago", color="success"))
                    ]),
                    # Placeholder 3
                    html.Tr([
                        html.Td(dbc.Checkbox(value=False)),
                        html.Td("10/06/2026"),
                        html.Td("Renovação de Licença da IDE"),
                        html.Td("Ferramentas"),
                        html.Td("- R$ 420,00", className="text-danger fw-bold"),
                        html.Td(dbc.Badge("Pendente", color="warning"))
                    ]),
                ])
            ], striped=True, hover=True, responsive=True, className="mb-0")
        ], className="shadow-sm")

], fluid=True, className="py-2")
