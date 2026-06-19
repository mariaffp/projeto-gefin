import dash
from dash import html, dcc
import dash_bootstrap_components as dbc


dash.register_page(__name__, path='/relatorios', name="Relatórios")

def layout():
    return dbc.Container([
    dbc.Row(
        dbc.Col(
            html.H1("Relatórios", className="text-dark mt-4 mb-4 fw-bold"),
            width=12
        )
    ),

  # Dropdowns na área dos filtros  
dbc.Card([
    dbc.CardHeader("Filtros de Relatório", className="fw-bold bg-light"),
    dbc.CardBody([
        dbc.Row([
        dbc.Col([
            html.Label("Categoria", className="fw-semibold mb-1 small"),
            dcc.Dropdown(
                id="filtro-categoria",
                options=[
                    {"label": "placeholder", "value": "placeholder"},
                ],
                placeholder="Selecione o tipo...",
                clearable=True
            )
        ], xs=12, sm=6, md=3, className="mb-3"),

        dbc.Col([
            html.Label("Tipo", className="fw-semibold mb-1 small"),
            dcc.Dropdown(
                id="filtro-tipo",
                options=[
                    {"label": "Receita (Entrada)", "value": "receita"},
                    {"label": "Despesa (Saída)", "value": "despesa"},
                ],
                placeholder="Selecione o tipo...",
                clearable=True
            )
        ], xs=12, sm=6, md=3, className="mb-3"),

        dbc.Col([
            html.Label("Período", className="fw-semibold mb-1 small"),
            dcc.Dropdown(
                id="filtro-periodo",
                options=[
                    {"label": "Este Mês", "value": "este_mes"},
                    {"label": "Últimos 3 Meses", "value": "3_meses"},
                    {"label": "Este Ano", "value": "este_ano"},
                    {"label": "Personalizado", "value": "custom"},
                ],
                value="este-mes",
                clearable=False
            )
        ], xs=12, sm=6, md=3, className="mb-3"),

        dbc.Col([
            html.Label("Instituição", className="fwsemibold mb-1 small"),
            dcc.Dropdown(
                id="filtro-instiuicao",
                options=[
                   {"label": "Banco do Brasil", "value": "bb"},
                    {"label": "Itaú", "value": "itau"},
                    {"label": "Nubank", "value": "nubank"},
                    {"label": "Dinheiro em Espécie", "value": "especie"}, 
                ],
                placeholder="Todas as contas...",
                clearable=True
            )
        ], xs=12, sm=6, md=3, className="mb-3"),
    ]),
 ])
], className="shadow-sm mb-4"),

# placehplder do relatorio
dbc.Card([
    dbc.CardHeader("Visualização do Relatório", className="fw-bold bg-light"),
    dbc.CardBody([
        html.Div(
            [
            html.I(className="bi bi-graph-up shadow-sm mb-3 text-muted", style={"fontSize": "2.5rem"}),
            html.H5("O relatório estará aqui eventualmente", className= "text-muted fw-normal"),
            ],
        id="area-relatorio-gerado",
        className="d-flex flex-column align-items-center justify-content-center py-5 border rounded bg-light text-secondary",
        style={"minHeight": "300px", "borderStyle": "dashed !important"}
    ),

    dbc.Row([
        dbc.Col(
            html.Div([
                #Botão para exportação
                dbc.Button(
                    [html.I(className="bi bi-filetype-csv me-2"), "Exportar em CSV"],
                    id="btn-exportar-csv",
                    color="secondary",
                    size="sm",
                    className="me-2" 
                ),
                dbc.Button(
                    [html.I(className="bi bi-file-earmark-pdf me-2"), "Importar relatório em PDF"],
                    id="btn-importar-pdf",
                    color="secondary",
                    size="sm"
                ),
            ], className="d-flex justify-content-end mt-4"),
            width=12
        )
        ])  
    ])
    ], className="shadow-sm mb-5"),
    ], fluid=True, className="px-4")