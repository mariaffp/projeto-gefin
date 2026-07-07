import dash
from dash import html, Input, Output, State, callback, dcc
import dash_bootstrap_components as dbc
from datetime import datetime, date
import calendar
from supabase_client import supabase
from services.dashboard import (tem_movimentacao_no_mes,calcular_saldo_ate,calcular_despesas_mes,calcular_previsao_caixa,dados_entradas_saidas_por_periodo,dados_despesas_por_categoria_periodo,dados_evolucao_saldo_periodo,MESES_ABREV,)
import plotly.graph_objects as go

dash.register_page(__name__, path='/dashboard', name="Dashboard")

meses_extenso = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}
meses_numero = {v: k for k, v in meses_extenso.items()}
ANO_INICIAL = 2025


def create_kpi_card(title, value, tipo="neutro"):
    cores_destaque = {
        "sucesso": "#28a745",
        "perigo":  "#dc3545",
        "info":    "#6f42c1",
        "neutro":  "#6c757d"
    }
    cor_borda = cores_destaque.get(tipo, cores_destaque["neutro"])
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="text-white-50 text-uppercase fw-semibold mb-1",
                    style={"fontSize": "0.75rem", "letterSpacing": "0.5px"}),
            html.H3(value, className="text-white fw-bold m-0")
        ]),
        style={
            "backgroundColor": "#3178d4",
            "borderRadius": "12px",
            "border": "none",
            "borderLeft": f"6px solid {cor_borda}",
            "boxShadow": "0 4px 6px rgba(0,0,0,0.1)"
        },
        className="h-100"
    )


def montar_kpis(ano, mes):
    saldo = calcular_saldo_ate(ano, mes)
    sem_movimentacao = not tem_movimentacao_no_mes(ano, mes)
    tipo_saldo = "perigo" if saldo < 0 else "sucesso"

    if sem_movimentacao:
        return [
            dbc.Col(create_kpi_card("Saldo Atual", f"R$ {saldo:.2f}", "neutro"),
                    xs=12, md=4, className="mb-3 mb-md-0"),
            dbc.Col(create_kpi_card("Despesas", "Sem movimentações", "neutro"),
                    xs=12, md=4, className="mb-3 mb-md-0"),
            dbc.Col(create_kpi_card("Previsão do caixa", "Sem movimentações", "neutro"),
                    xs=12, md=4, className="mb-3 mb-md-0"),
        ]

    despesas = calcular_despesas_mes(ano, mes)
    previsao = calcular_previsao_caixa(ano, mes)
    return [
        dbc.Col(create_kpi_card("Saldo Atual", f"R$ {saldo:.2f}", tipo_saldo),
                xs=12, md=4, className="mb-3 mb-md-0"),
        dbc.Col(create_kpi_card("Despesas", f"R$ {despesas:.2f}", "perigo"),
                xs=12, md=4, className="mb-3 mb-md-0"),
        dbc.Col(create_kpi_card("Previsão do caixa", f"R$ {previsao:.2f}", "info"),
                xs=12, md=4, className="mb-3 mb-md-0"),
    ]


def seletor_periodo(id_mes_inicio, id_ano_inicio, id_mes_fim, id_ano_fim, id_aviso):   
    hoje = date.today()
    ano_atual = hoje.year
    opcoes_ano = [{"label": str(a), "value": a} for a in range(ANO_INICIAL, ano_atual + 1)]
    opcoes_mes = [{"label": nome, "value": num} for num, nome in meses_extenso.items()]

    return dbc.Row([
        dbc.Col([
            html.Label("De", className="fw-semibold small mb-1"),
            dbc.Row([
                dbc.Col(
                    dbc.Select(
                        id=id_mes_inicio, 
                        options=opcoes_mes,
                        value=1, 
                        style={"width": "130px"}
                    ),
                    width="auto"
                ),

                dbc.Col(
                    dbc.Select(
                        id=id_ano_inicio, 
                        options=opcoes_ano,
                        value=ano_atual, style={"width": "100px"}
                    ),
                    width="auto"
                ),

            ], 
            className="g-2")

        ], 
        width="auto"),

        dbc.Col([
            html.Label("Até", className="fw-semibold small mb-1"),
            dbc.Row([
                dbc.Col(
                    dbc.Select(
                        id=id_mes_fim, 
                        options=opcoes_mes,
                        value=hoje.month, 
                        style={"width": "130px"}
                    ),
                    width="auto"
                ),
                dbc.Col(
                    dbc.Select(
                        id=id_ano_fim, 
                        options=opcoes_ano,
                        value=ano_atual, 
                        style={"width": "100px"}
                    ),
                    width="auto"
                ),
            ], 
            className="g-2"
            )
        ], 
        width="auto"
        ),

        dbc.Col(
            html.Div(id=id_aviso, className="text-danger small mt-4"),
            width="auto"
        ),
    ], className="mb-3 align-items-end g-3")


def layout(**kwargs):
    mes_atual = meses_extenso[datetime.now().month]
    ano_atual = datetime.now().year
    opcoes_ano = [{"label": str(a), "value": a} for a in range(ANO_INICIAL, ano_atual + 1)]

    return dbc.Container([

        dbc.Row([
            dbc.Col(
                html.H3(f"Visão Geral Financeira - {mes_atual}",
                        id="titulo-dashboard", className="fw-semibold text-dark mb-0"),
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
                xs=6, md="auto", className="ms-md-auto mt-2 mt-md-0"
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
        ], className="my-4 align-items-center"),


        dbc.Row(
            id="kpi-cards-container",
            children=montar_kpis(ano_atual, datetime.now().month),
            className="mb-4"
        ),


        html.Hr(style={
            "borderTop": "1px solid #E2E8F0", 
            "opacity": "0.6", 
            "marginTop": "45px", 
            "marginBottom": "35px"
        }),

        dbc.Row([
            dbc.Col(
                html.H3(" Dashboards - Análise Histórica por Período",
                        id="subtitulo-dashboard", className="fw-semibold text-dark mb-0",
                        style={"fontSize": "26px"}), 
                width="auto"
            ),
        ], className="mb-4"),

       
        dbc.Row([
            dbc.Col([
                dbc.Tabs([

                    dbc.Tab(
                        tab_id="tab-barras",
                        label="Entradas vs Saídas",
                        children=[dbc.Card([dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Tipo", className="fw-semibold small"),
                                    dcc.Dropdown(
                                        id="filtro-barras-tipo",
                                        options=[
                                            {"label": "Entradas e Saídas", "value": "ambos"},
                                            {"label": "Só Entradas", "value": "ENTRADA"},
                                            {"label": "Só Saídas", "value": "SAIDA"},
                                        ],
                                        value="ambos",
                                        clearable=False,
                                        searchable=False,
                                        style={"width": "200px"}
                                    )
                                ], 
                                width="auto"),
                            ], 
                            className="mb-2"),
                            seletor_periodo(
                                "barras-mes-inicio", 
                                "barras-ano-inicio",
                                "barras-mes-fim", 
                                "barras-ano-fim",
                                "barras-aviso"
                            ),
                            dcc.Graph(id="grafico-barras")
                        ])], className="border-0 shadow-sm mt-2")]
                    ),

                    
                    dbc.Tab(
                        tab_id="tab-pizza",
                        label="Despesas por Categoria",
                        children=[dbc.Card([dbc.CardBody([
                            seletor_periodo(
                                "pizza-mes-inicio", 
                                "pizza-ano-inicio",
                                "pizza-mes-fim", 
                                "pizza-ano-fim",
                                "pizza-aviso"
                            ),
                            dcc.Graph(id="grafico-pizza")
                        ])], className="border-0 shadow-sm mt-2")]
                    ),

                    
                    dbc.Tab(
                        tab_id="tab-linha",
                        label="Evolução do Saldo",
                        children=[dbc.Card([dbc.CardBody([
                            seletor_periodo(
                                "linha-mes-inicio", 
                                "linha-ano-inicio",
                                "linha-mes-fim", 
                                "linha-ano-fim",
                                "linha-aviso"
                            ),
                            dcc.Graph(id="grafico-linha")
                        ])], className="border-0 shadow-sm mt-2")]
                    ),

                ],
                id="abas-dashboard",
                active_tab="tab-barras",
                className="mb-3"
                ),
            ], xs=12)
        ])
    ], fluid=True, className="py-3 px-4")


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


@callback(
    Output("grafico-barras", "figure"),
    Output("barras-aviso", "children"),
    Input("barras-mes-inicio", "value"),
    Input("barras-ano-inicio", "value"),
    Input("barras-mes-fim", "value"),
    Input("barras-ano-fim", "value"),
    Input("filtro-barras-tipo", "value")
)
def atualizar_barras(mes_ini, ano_ini, mes_fim, ano_fim, tipo_filtro):
    data_inicio = date(int(ano_ini), int(mes_ini), 1).isoformat()
    ultimo_dia = calendar.monthrange(int(ano_fim), int(mes_fim))[1]
    data_fim = date(int(ano_fim), int(mes_fim), ultimo_dia).isoformat()

    if data_inicio > data_fim:
        fig = go.Figure()
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        return fig, "A data inicial deve ser anterior à data final."

    labels, entradas, saidas = dados_entradas_saidas_por_periodo(data_inicio, data_fim)

    barras = []
    if tipo_filtro in ("ambos", "ENTRADA"):
        barras.append(go.Bar(name="Entradas", x=labels, y=entradas, marker_color="#28a745"))
    if tipo_filtro in ("ambos", "SAIDA"):
        barras.append(go.Bar(name="Saídas", x=labels, y=saidas, marker_color="#dc3545"))

    fig = go.Figure(barras)
    fig.update_layout(
        barmode="group",
        title=f"Entradas vs Saídas — {MESES_ABREV[int(mes_ini)]}/{ano_ini} a {MESES_ABREV[int(mes_fim)]}/{ano_fim}",
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis=dict(tickprefix="R$ "),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig, ""



@callback(
    Output("grafico-pizza", "figure"),
    Output("pizza-aviso", "children"),
    Input("pizza-mes-inicio", "value"),
    Input("pizza-ano-inicio", "value"),
    Input("pizza-mes-fim", "value"),
    Input("pizza-ano-fim", "value")
)
def atualizar_pizza(mes_ini, ano_ini, mes_fim, ano_fim):
    data_inicio = date(int(ano_ini), int(mes_ini), 1).isoformat()
    ultimo_dia = calendar.monthrange(int(ano_fim), int(mes_fim))[1]
    data_fim = date(int(ano_fim), int(mes_fim), ultimo_dia).isoformat()

    if data_inicio > data_fim:
        fig = go.Figure()
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        return fig, "A data inicial deve ser anterior à data final."

    categorias = dados_despesas_por_categoria_periodo(data_inicio, data_fim)

    if not categorias:
        fig = go.Figure()
        fig.update_layout(
            title="Sem despesas para o período selecionado",
            plot_bgcolor="white", paper_bgcolor="white"
        )
        return fig, ""

    fig = go.Figure([go.Pie(
        labels=list(categorias.keys()),
        values=list(categorias.values()),
        hole=0.4
    )])
    fig.update_layout(
        title=f"Despesas por Categoria — {MESES_ABREV[int(mes_ini)]}/{ano_ini} a {MESES_ABREV[int(mes_fim)]}/{ano_fim}",
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    return fig, ""



@callback(
    Output("grafico-linha", "figure"),
    Output("linha-aviso", "children"),
    Input("linha-mes-inicio", "value"),
    Input("linha-ano-inicio", "value"),
    Input("linha-mes-fim", "value"),
    Input("linha-ano-fim", "value")
)
def atualizar_linha(mes_ini, ano_ini, mes_fim, ano_fim):
    data_inicio = date(int(ano_ini), int(mes_ini), 1).isoformat()
    ultimo_dia = calendar.monthrange(int(ano_fim), int(mes_fim))[1]
    data_fim = date(int(ano_fim), int(mes_fim), ultimo_dia).isoformat()

    if data_inicio > data_fim:
        fig = go.Figure()
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        return fig, "A data inicial deve ser anterior à data final."

    labels, saldos = dados_evolucao_saldo_periodo(data_inicio, data_fim)

    if not saldos:
        fig = go.Figure()
        fig.update_layout(
            title="Sem dados para o período selecionado",
            plot_bgcolor="white", paper_bgcolor="white"
        )
        return fig, ""

    fig = go.Figure([go.Scatter(
        x=labels,
        y=saldos,
        mode="lines+markers",
        line=dict(color="#3178d4", width=3),
        marker=dict(size=8),
        fill="tozeroy",
        fillcolor="rgba(49, 120, 212, 0.1)"
    )])
    fig.update_layout(
        title=f"Evolução do Saldo — {MESES_ABREV[int(mes_ini)]}/{ano_ini} a {MESES_ABREV[int(mes_fim)]}/{ano_fim}",
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis=dict(tickprefix="R$ ")
    )
    return fig, ""