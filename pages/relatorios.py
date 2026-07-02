import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
#imports para gerar tabela e conexão com o banco de dados
from datetime import date, timedelta
from services.transacao import listar_transacoes
from services.categoria import listar_categorias
from services.conta import listar_contas
from supabase_client import supabase
import pandas as pd
#imports para gerar pdf
from io import BytesIO
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Image
from reportlab.lib.utils import ImageReader


dash.register_page(__name__, path='/relatorios', name="Relatórios")


def layout(**kwargs):
    #Busco todas as categorias e contas do banco de dados e armazeno elas nas variaveis
    categorias = listar_categorias() 
    contas = listar_contas()

    #Criando as opçoes que vão realmente aparecer para o usuario e os valores delas que o sistema precisa reconhecer
    opcoes_categoria = [{"label": c["nome"], "value": c["id_categoria"]} for c in categorias.data]
    opcoes_conta = [{"label": c["nome"], "value": c["id_conta"]} for c in contas.data]



    return dbc.Container([
    dcc.Store(id="store-transacoes-filtradas"), #armazena temporariamente as transações filtradas no navegador
    #permite fazer download em pdf e css
    dcc.Download(id="download-csv"), 
    dcc.Download(id="download-pdf"),

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
                options=opcoes_categoria, #passei a variavel que continha as opções de categoria
                placeholder="Selecione a categoria...",
                clearable=True
            )
        ], xs=12, sm=6, md=3, className="mb-3"),

        dbc.Col([
            html.Label("Tipo", className="fw-semibold mb-1 small"),
            dcc.Dropdown(
                id="filtro-tipo",
                options=[
                    {"label": "Receita (Entrada)", "value": "ENTRADA"},
                    {"label": "Despesa (Saída)", "value": "SAIDA"},
                ],
                placeholder="Selecione o tipo...",
                clearable=True,
                searchable=False
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
                clearable=True,
                placeholder="Selecione o período...",
                searchable=False #tirei a possibilidade de pesquisar escrevendo
            )
        ], xs=12, sm=6, md=3, className="mb-3"),

        dbc.Col([
            html.Label("Instituição", className="fw-semibold mb-1 small"),
            dcc.Dropdown(
                id="filtro-instituicao",
                options=opcoes_conta, #passei a variavel que continha as opções de conta
                placeholder="Selecione a instituição...",
                clearable=True
            )
        ], xs=12, sm=6, md=3, className="mb-3"),
    ]),

 # Datas personalizadas, só aparecem se "Personalizado" for selecionado
        dbc.Row([
            dbc.Col([
                html.Label("Data Início", className="fw-semibold mb-1 small"),
                dcc.DatePickerSingle(
                    id="filtro-data-inicio", 
                    placeholder="Selecione uma data...",
                    display_format="DD/MM/YYYY"
                    )
            ], xs=12, sm=6, md=3, className="mb-3"),
            dbc.Col([
                html.Label("Data Fim", className="fw-semibold mb-1 small"),
                dcc.DatePickerSingle(
                    id="filtro-data-fim", 
                    placeholder="Selecione uma data...",
                    display_format="DD/MM/YYYY"
                    )
            ], xs=12, sm=6, md=3, className="mb-3"),
        ], 
        id="linha-datas-personalizadas", 
        style={"display": "none"} #começa escondida
        ),

        dbc.Row([
            dbc.Col(
                dbc.Button(
                    "Aplicar Filtros",
                    id="btn-aplicar-filtros",
                    color="primary",
                    className="mt-2"
                ),
                width=12,
                className="d-flex justify-content-start justify-content-sm-end"
            )
        ])
    ]),
], className="shadow-sm mb-4"),

 # Card com o resultado do relatório
        dbc.Card([
            dbc.CardHeader("Visualização do Relatório", className="fw-bold bg-light"),
            dbc.CardBody([
                dcc.Loading(
                    id="loading-relatorio",
                    type="circle",
                    children=html.Div(
                        [
                            html.I(className="bi bi-graph-up shadow-sm mb-3 text-muted",
                                   style={"fontSize": "2.5rem"}),
                            html.H5("Selecione os filtros e clique em Aplicar",
                                    className="text-muted fw-normal"),
                        ],
                        id="area-relatorio-gerado",
                        className="d-flex flex-column align-items-center justify-content-center py-5 border rounded bg-light text-secondary",
                        style={"minHeight": "300px", "borderStyle": "dashed !important"}
                    )
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
                    [html.I(className="bi bi-file-earmark-pdf me-2"), "Exportar em PDF"],
                    id="btn-exportar-pdf",
                    color="secondary",
                    size="sm"
                ),
            ], className="d-flex justify-content-start justify-content-sm-end flex-wrap mt-4"),
            width=12
        )
        ])  
    ])
    ], className="shadow-sm mb-5"),
    ], fluid=True, className="px-4")


    #Funções:
@callback(
    Output("linha-datas-personalizadas", "style"),
    Input("filtro-periodo", "value"),
)
def alternar_datas_personalizadas(periodo):
    if periodo == "custom":
        return {"display": "flex"}
    return {"display": "none"} #se value for custom, entao mostra campos da data


#  Calcula as datas de início/fim a partir do período escolhido
def calcular_periodo(periodo, data_inicio_custom, data_fim_custom):
    hoje = date.today()

    if periodo == "este_mes":
        inicio = hoje.replace(day=1) #data de inicio vai ser o dia 1 do mes que estamos hoje
        return inicio.isoformat(), hoje.isoformat() #isoformat coloca a data no padrão AAAA-MM-DD

    if periodo == "3_meses":
        inicio = hoje - timedelta(days=90) #o inicio vai ser 90 dias antes de hoje
        return inicio.isoformat(), hoje.isoformat()

    if periodo == "este_ano":
        inicio = hoje.replace(month=1, day=1) #dia de inicio é dia 1/1
        return inicio.isoformat(), hoje.isoformat()

    if periodo == "custom":
        return data_inicio_custom, data_fim_custom #retorna as datas escolhidas pelo usuario

    return None, None # se nao se encaixa em nenhuma das datas, retorna none


#  aplica os filtros e busca no banco 
@callback(
    Output("area-relatorio-gerado", "children"), #atualiza onde o relatorio vai ser mostrado
    Output("store-transacoes-filtradas", "data"), #salva as transações filtradas para depois poder exportar
    Input("btn-aplicar-filtros", "n_clicks"),
    Input("filtro-categoria", "value"),
    Input("filtro-tipo", "value"),
    Input("filtro-periodo", "value"),
    Input("filtro-instituicao", "value"),
    Input("filtro-data-inicio", "date"),
    Input("filtro-data-fim", "date"),
    prevent_initial_call=True
)
def gerar_relatorio(n_clicks, id_categoria, tipo, periodo, id_conta, data_inicio_custom, data_fim_custom):
    if not n_clicks:
        return dash.no_update, dash.no_update

    data_inicio, data_fim = calcular_periodo(periodo, data_inicio_custom, data_fim_custom)

    try:
        transacoes = listar_transacoes(id_categoria=id_categoria, tipo=tipo, id_conta=id_conta, data_inicio=data_inicio, data_fim=data_fim,)
    except Exception as e:
        return html.Div(f"Erro ao buscar transações: {e}", className="text-danger"), []

    if not transacoes:
        return html.Div(
            "Nenhuma transação encontrada para os filtros selecionados.",
            className="text-muted text-center py-5"
        ), []

    # Montando uma tabela simples com o resultado
    linhas = []
    for t in transacoes:
        nome_categoria = t["categoria"]["nome"] if t.get("categoria") else "—"
        nome_conta = t["conta"]["nome"] if t.get("conta") else "—"

        linhas.append(html.Tr([
            html.Td(t["data"]),
            html.Td(t["descricao"]),
            html.Td(nome_categoria),
            html.Td(nome_conta),
            html.Td(t["tipo"]),
            html.Td(f"R$ {t['valor']:.2f}"),
        ]))

    tabela = dbc.Table([
        html.Thead(html.Tr([
            html.Th("Data"), html.Th("Descrição"), html.Th("Categoria"),
            html.Th("Conta"), html.Th("Tipo"), html.Th("Valor"),
        ])),
        html.Tbody(linhas)
    ], bordered=True, hover=True, responsive=True, className="mt-3 text-dark")

    return tabela, transacoes


@callback(
    Output("download-csv", "data"),
    Input("btn-exportar-csv", "n_clicks"),
    Input("store-transacoes-filtradas", "data"),
    prevent_initial_call=True
)
def exportar_csv(n_clicks, transacoes):
    if not n_clicks:
        return dash.no_update

    if not transacoes:
        return dash.no_update

    # Monta uma lista simplificada para o CSV
    linhas = []
    for t in transacoes:
        linhas.append({
            "Data": t["data"],
            "Descrição": t["descricao"],
            "Categoria": t["categoria"]["nome"] if t.get("categoria") else "",
            "Conta": t["conta"]["nome"] if t.get("conta") else "",
            "Tipo": t["tipo"],
            "Valor": t["valor"],
        })

    df = pd.DataFrame(linhas)

    return dcc.send_data_frame(df.to_csv, "relatorio_transacoes.csv", index=False, encoding="utf-8-sig")

@callback(
    Output("download-pdf", "data"),
    Input("btn-exportar-pdf", "n_clicks"),
    Input("store-transacoes-filtradas", "data"),
    prevent_initial_call=True
)
def exportar_pdf(n_clicks, transacoes):
    if not n_clicks:
        return dash.no_update

    if not transacoes:
        return dash.no_update

    buffer = BytesIO() #cria um buffer na memoria, o pdf vai ser montado nele
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4)) #criando pdf, ele vai ser armazenado no buffer, tem tamanho de uma folha A4 com orientação horizontal
    styles = getSampleStyleSheet() #pegando os estilos prontos do reportlab
    elementos = []

    img_reader = ImageReader("assets/Focus_consultoria_preto.png") #carregando logo

    #alterando tamanho da logo para ela não ficar estranha
    largura_original, altura_original = img_reader.getSize()
    proporcao = altura_original / largura_original
    largura_desejada = 120
    altura_calculada = largura_desejada * proporcao

    #criando a logo e adicionando no pdf
    logo = Image("assets/Focus_consultoria_preto.png", width=largura_desejada, height=altura_calculada)
    elementos.append(logo)
    elementos.append(Spacer(1, 20)) #espaço em branco, para pular linha depois da logo

    # Título
    elementos.append(Paragraph("Relatório de Transações - FOCUS", styles["Title"]))
    elementos.append(Spacer(1, 12))

    # Cabeçalho da tabela
    dados_tabela = [["Data", "Descrição", "Categoria", "Conta", "Tipo", "Valor"]]

    # Linhas com os dados
    for t in transacoes:
        nome_categoria = t["categoria"]["nome"] if t.get("categoria") else "—"
        nome_conta = t["conta"]["nome"] if t.get("conta") else "—"
        #adicionando na tabela os dados
        dados_tabela.append([ 
            t["data"],
            t["descricao"],
            nome_categoria,
            nome_conta,
            t["tipo"],
            f"R$ {t['valor']:.2f}",
        ])

    tabela = Table(dados_tabela, repeatRows=1) #criando tabela e depois estilizando ela
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0067EC")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 15),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # CENTRALIZA
        ("TOPPADDING", (0, 0), (-1, -1), 8),      #  adiciona espaçamento interno
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),   #  adiciona espaçamento interno
    ]))

    elementos.append(tabela) #adicionando tabela no pdf
    doc.build(elementos) #gerando pdf

    buffer.seek(0) #voltando para inicio do buffer
    return dcc.send_bytes(buffer.read(), "relatorio_transacoes.pdf") #retorno o documento pdf byte por byte e o nome dele