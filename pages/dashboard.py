import dash
from dash import html, Input, Output, callback, dcc
import dash_bootstrap_components as dbc
from supabase_client import supabase
from datetime import datetime

dash.register_page(__name__, path='/dashboard', name="Dashboard")

meses_extenso = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

mes_atual = meses_extenso[datetime.now().month]

#funcao pra criar os cards que mostram os valores
def create_kpi_card(title, value, text_class="text-white"):
    return dbc.Card(
        dbc.CardBody(
            [
                # Titulo do card
                html.H6(title, className="card-title text-muted fw-bold mb-2", style={"fontSize": "0.9rem"}),
               
                html.H4(value, className=f"{text_class} fw-bold m-0")
            ]
        ),
        color="#3178d4", 
        className="mb-3 border-0 shadow-sm",
        style={"borderRadius": "8px"}
    )

layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.H2(f"Visão Geral Financeira - {mes_atual}", id="titulo-dashboard", className="fw-normal text-dark"),
                    width="auto"
                ),
                dbc.Col(
                    dbc.Select(
                        id="selecao-mes",
                        options=[
                    {"label": "Janeiro", "value": "Janeiro"},
                    {"label": "Fevereiro", "value": "Fevereiro"},
                    {"label": "Março", "value": "Março"},
                    {"label": "Abril", "value": "Abril"},
                    {"label": "Maio", "value": "Maio"},
                    {"label": "Junho", "value": "Junho"},
                    {"label": "Julho", "value": "Julho"},
                    {"label": "Agosto", "value": "Agosto"},
                    {"label": "Setembro", "value": "Setembro"},
                    {"label": "Outubro", "value": "Outubro"},
                    {"label": "Novembro", "value": "Novembro"},
                    {"label": "Dezembro", "value": "Dezembro"},
                ],
                value=mes_atual,
                className="shadow-sm",
                style={"width": "150px"}
                    ),
                    width="auto",
                    className="ms-auto"
                )
            ],
            className="my-4 align-items-center"
        ),

            dbc.Row(
                [
                    dbc.Col(
                        [
                        create_kpi_card("Saldo Atual:", "R$ 5.000,00", "text-success"),
                        create_kpi_card("Despesas:", "R$ 2.000,00", "text-danger"),
                        create_kpi_card("Previsão do caixa:", "R$ 3.000,00", "text-warning"),
                        ],
                        xs=12, md=3,
                        className="mb-4 mb-md-0"
                    ),

                    dbc.Col(
                        html.Div(
                            [
                                html.H3("Dashboard em construção", className="text-secondary fw-light mb-2"),
                                html.P("Os graficos estarão aqui eu espero", className="text-muted small"),
                                #dbc.Button(
                                    #"Importação de Extratos",
                                    #href="/importacao",
                                    #color="primary",
                                    #className="mt-3 me-2"
                                #),
                                #dbc.Button(
                                    #"Transações",
                                    #href="/transacoes",
                                    #color="secondary",
                                    #className="mt-3"
                                #),
                                
                            ],
                            id="dashboard-content",
                            style={
                                "backgroundColor": "#f8f9fad8",
                            "minHeight": "550px", 
                            "display": "flex", 
                            "flexDirection": "column",
                            "justifyContent": "center", 
                            "alignItems": "center",
                            "borderRadius": "8px",
                            "border": "2px dashed #dee2e6"
                            },
                            className="p-4"
                        ),
                        xs=12, md=9
                    )
                ]
            )
 
        ],
        fluid=True,
        className="py-2"
    )

#altera o titulo de acordo com o mes selecionando
@callback(
    Output("titulo-dashboard", "children"),
    Input("selecao-mes", "value")
)
def atualizar_titulo(mes_selecionado):
    # Retorna o texto formatado que vai substituir o "children" do html.H2
    return f"Visão Geral Financeira - {mes_selecionado}"