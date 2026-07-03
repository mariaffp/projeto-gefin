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
def create_kpi_card(title, value, tipo="neutro"):

    cores_destaque = {
        "sucesso": "#28a745", # Verde
        "perigo":  "#dc3545", # Vermelho
        "info":    "#6f42c1", # Roxo
        "neutro":  "#6c757d"  # Cinza
    }
    cor_borda = cores_destaque.get(tipo, cores_destaque["neutro"]) #pegando a cor que vai ser usada na borda
    card_style = {
        "backgroundColor": "#3178d4",
        "borderRadius": "12px",
        "border": "none",
        "borderLeft": f"6px solid {cor_borda}", #  Borda esquerda colorida
        "boxShadow": "0 4px 6px rgba(0,0,0,0.1)"
    }
    title_class = "text-white-50 text-uppercase fw-semibold mb-1"
    value_class = "text-white fw-bold m-0" 
        
    return dbc.Card(
        dbc.CardBody(
            [
                html.H6(title, className=title_class, style={"fontSize": "0.75rem", "letterSpacing": "0.5px"}),
                html.H3(value, className=value_class)
            ]
        ),
        style=card_style,
        className="h-100"
    )

def montar_kpis(ano, mes):
    saldo = calcular_saldo_ate(ano,mes)
    sem_movimentacao = not tem_movimentacao_no_mes(ano,mes)
    tipo_saldo = "perigo" if saldo < 0 else "sucesso"
    texto_saldo = f"R$ {saldo:.2f}"

    if sem_movimentacao:
        texto_despesas = "Sem movimentações"
        texto_previsao = "Sem movimentações"
        # Se não tem movimentação, passamos tudo como neutro
        return [
            dbc.Col(
                create_kpi_card("Saldo Atual", texto_saldo, "neutro"), 
                xs=12, 
                md=4, 
                className="mb-3 mb-md-0"
            ),
            dbc.Col(
                create_kpi_card("Despesas", texto_despesas, "neutro"), 
                xs=12, 
                md=4, 
                className="mb-3 mb-md-0"
            ),
            dbc.Col(
                create_kpi_card("Previsão do caixa", texto_previsao, "neutro"), 
                xs=12, 
                md=4, 
                className="mb-3 mb-md-0"
            ),
        ]
    else:
        despesas = calcular_despesas_mes(ano, mes)
        previsao = calcular_previsao_caixa(ano,mes)
        texto_despesas = f"R$ {despesas:.2f}"
        texto_previsao = f"R$ {previsao:.2f}"
        

        return [
            dbc.Col(
                create_kpi_card("Saldo Atual", texto_saldo, tipo_saldo), 
                xs=12, 
                md=4, 
                className="mb-3 mb-md-0"
            ),
            dbc.Col(
                create_kpi_card("Despesas", texto_despesas, "perigo"), 
                xs=12, 
                md=4, 
                className="mb-3 mb-md-0"
            ),
            dbc.Col(
                create_kpi_card("Previsão do caixa", texto_previsao, "info"), 
                xs=12, 
                md=4, 
                className="mb-3 mb-md-0"
            ),
        ]

def layout(**kwargs):
    return dbc.Container([
        
        dbc.Row(
            [
                dbc.Col(
                    html.H3(f"Visão Geral Financeira - {mes_atual}", id="titulo-dashboard", className="fw-semibold text-dark mb-0"),
                    width="auto"
                ),
                dbc.Col(
                    dbc.Select(
                        id="selecao-mes",
                        options=[{"label": nome, "value": nome} for nome in meses_extenso.values()],
                        value=mes_atual,
                        className="shadow-sm border-0",
                        style={"width": "150px", "borderRadius": "8px"}
                    ),
                    xs=6, md="auto",
                    className="ms-md-auto mt-2 mt-md-0"
                ),
                dbc.Col(
                    dbc.Select(
                        id="selecao-ano",
                        options=opcoes_ano,
                        value=ano_atual,
                        className="shadow-sm border-0",
                        style={"width": "100px", "borderRadius": "8px"}
                    ),
                    width="auto"
                ),
            ],
            className="my-4 align-items-center"
        ),

    
        dbc.Row(
            id="kpi-cards-container",
            children=montar_kpis(ano_atual, datetime.now().month),
            className="mb-4" 
        ),

        
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.H4("Dashboard em construção", className="text-secondary fw-light mb-2"),
                            html.P("Os gráficos estarão aqui em breve", className="text-muted small"),
                        ],
                        id="dashboard-content",
                        style={
                            "backgroundColor": "white", # Fundo branco limpo
                            "minHeight": "450px", 
                            "display": "flex", 
                            "flexDirection": "column",
                            "justifyContent": "center", 
                            "alignItems": "center",
                            "borderRadius": "12px",
                            "border": "1px solid #e9ecef",
                            "boxShadow": "0 .125rem .25rem rgba(0,0,0,.075)" 
                        },
                        className="p-4"
                    ),
                    xs=12 # Agora ocupa a tela toda de ponta a ponta
                )
            ]
        )
    ],
    fluid=True,
    className="py-3 px-4" 
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