import dash
from dash import html, Input, Output, callback, dcc
import dash_bootstrap_components as dbc
from supabase_client import supabase
from datetime import datetime
from services.dashboard import ( tem_movimentacao_no_mes, calcular_saldo_ate, calcular_despesas_mes, calcular_previsao_caixa,)

dash.register_page(__name__, path='/dashboard', name="Dashboard")

meses_extenso = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

mes_atual = meses_extenso[datetime.now().month]
ano_atual = datetime.now().year
meses_numero = {v: k for k, v in meses_extenso.items()} #Só estou pegando o numero do mes ao inves do nome do mes

ANO_INICIAL = 2026
opcoes_ano = [
    {"label": str(ano), "value": ano} for ano in range(ANO_INICIAL, ano_atual + 1 )
]

#funcao pra criar os cards que mostram os valores
def create_kpi_card(title, value, text_class="text-white"):
    return dbc.Card(
        dbc.CardBody(
            [
                # Titulo do card
                html.H6(title, className="card-title text-white fw-bold mb-2", style={"fontSize": "0.9rem"}),
               
                html.H4(value, className=f"{text_class} fw-bold m-0")
            ]
        ),
        color="#3178d4", 
        className="mb-3 border-0 shadow-sm",
        style={"borderRadius": "8px"}
    )

def montar_kpis(ano, mes):
    #vou pegar os dados do banco de dados para colocar nos cards

    saldo = calcular_saldo_ate(ano,mes)
    sem_movimentacao = not tem_movimentacao_no_mes(ano,mes)

    if sem_movimentacao:
        texto_despesas = "Sem movimentações"
        texto_previsao = "Sem movimentações"
    else:
        despesas = calcular_despesas_mes(ano, mes)
        previsao = calcular_previsao_caixa(ano,mes)
        texto_despesas = f"R$ {despesas:.2f}"
        texto_previsao = f"R$ {previsao:.2f}"

    return [
        create_kpi_card("Saldo Atual:", f"R$ {saldo:.2f}", "text-success"),
        create_kpi_card("Despesas:", texto_despesas, "text-danger"),
        create_kpi_card("Previsão do caixa:", texto_previsao, "text-warning"),
    ]


def layout(**kwargs):
    return dbc.Container([
        dbc.Row(
            [
                dbc.Col(
                    html.H2(f"Visão Geral Financeira - {mes_atual}", id="titulo-dashboard", className="fw-normal text-dark"),
                    xs=12, md="auto"
                ),
                dbc.Col(
                    dbc.Select(
                        id="selecao-mes",
                        options=[
                    {"label": nome, "value": nome} for nome in meses_extenso.values()
                ],
                value=mes_atual,
                className="shadow-sm",
                style={"width": "100%", "maxWidth": "150px"}
                    ),
                    xs=6, md="auto",
                    className="ms-md-auto mt-2 mt-md-0"
                ),
                dbc.Col(
                    dbc.Select(
                        id="selecao-ano",
                        options=opcoes_ano,
                        value=ano_atual,
                        className="shadow-sm",
                        style={"width": "100%", "maxWidth": "100px"}
                    ),
                    xs=6, md="auto",
                    className="mt-2 mt-md-0"
                    ),
            ],
            className="my-4 align-items-center"
        ),

            dbc.Row(
                [
                    dbc.Col(
                    html.Div(
                        id="kpi-cards-container",
                        children=montar_kpis(ano_atual, datetime.now().month)
                    ),
                    xs=12, md=3,
                    className="mb-4 mb-md-0"
                ),

                    dbc.Col(
                        html.Div(
                            [
                                html.H3("Dashboard em construção", className="text-secondary fw-light mb-2"),
                                html.P("Os graficos estarão aqui eu espero", className="text-muted small"),
                                
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
    Output("kpi-cards-container", "children"),
    Input("selecao-mes", "value"),
    Input("selecao-ano", "value")
)
def atualizar_dashboard(mes_selecionado, ano_selecionado):
    numero_mes = meses_numero[mes_selecionado]
    novos_kpis = montar_kpis(int(ano_selecionado), numero_mes)
    return f"Visão Geral Financeira - {mes_selecionado} de {ano_selecionado}", novos_kpis