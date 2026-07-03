import dash
from dash import html, dcc, Input, Output, State, callback, MATCH, ALL, ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from supabase_client import supabase
from services.categoria import listar_categorias
from services.conta import listar_contas
from services.forma_pagamento import listar_forma_pagamento
from services.transacao import listar_transacoes, criar_transacao, editar_transacao, excluir_transacao
from services.categoria import *

dash.register_page(__name__, path='/transacoes', name='Transações')

def obter_user_id_logado():
    session = supabase.auth.get_session()

    if session is None:
        raise Exception("Usuário não autenticado")

    return session.user.id

# helpers

def _build_lookup(*lists):
    """cria dicionário {value: label} a partir de listas de opções"""
    return {item["value"]: item["label"] for lst in lists for item in lst}

def _is_image(contents):
    return bool(contents and "image" in contents)

def formata_data(data_iso):
    if not data_iso:
        return ""
    try:
        y, m, d = data_iso.split("-")
        return f"{d}/{m}/{y}"
    except (ValueError, AttributeError):
        return data_iso

def formata_valor(val_num, tipo):
    valor_str = f"R$ {abs(val_num):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    if tipo == "SAIDA":
        return f"- {valor_str}", "text-danger"

    return valor_str, "text-success"

def cor_situacao(situacao):
    if situacao in ("Pago", "Recebido"):
        return "success"

    if situacao in ("A Pagar", "A Receber"):
        return "warning"

    return "secondary"

def render_file_preview(f):
    fname = f.get("filename", "arquivo")
    contents = f.get("contents", "")

    if _is_image(contents):
        return html.A(
            html.Div([
                html.Img(src=contents, className="attachment-thumbnail"),
                html.Div(html.I(className="bi bi-box-arrow-up-right", style={"fontSize": "1.4rem"}), className="attachment-overlay"),
            ], className="attachment-card"),
            href=contents, target="_blank",
        )

    if fname and fname.lower().endswith(".pdf"):
        return html.Div([
            html.Iframe(src=contents, style={"width": "100%", "maxWidth": "500px", "height": "300px", "border": "1px solid #dee2e6", "borderRadius": "8px"}),
            html.Div(
                html.A(
                    [html.I(className="bi bi-box-arrow-up-right me-1"), "Abrir em nova guia"],
                    href=contents, target="_blank",
                    className="text-primary small fw-semibold",
                    style={"textDecoration": "none"}
                ), className="mt-2"
            ),
        ])

    return html.A(
        html.Div([
            html.I(className="bi bi-file-earmark-fill me-2", style={"fontSize": "1.3rem", "color": "#6c757d"}),
            html.Span(fname, className="fw-semibold"),
            html.I(className="bi bi-box-arrow-up-right ms-auto", style={"fontSize": "1rem"}),
        ], className="attachment-file-chip"),
        href=contents, target="_blank",
        style={"textDecoration": "none", "color": "inherit"}
    )

def render_modal_thumb(i, f):
    """gera mini preview com botão X para o modal de edição"""
    fname = f.get("filename", "arquivo")
    contents = f.get("contents", "")

    if _is_image(contents):
        thumb = html.Img(src=contents, style={
            "width": "80px", "height": "80px", "objectFit": "cover",
            "borderRadius": "6px", "border": "1px solid #dee2e6"
        })
    else:
        icon_color = "#dc3545" if fname.lower().endswith(".pdf") else "#6c757d"
        thumb = html.Div(
            html.I(className="bi bi-file-earmark-pdf-fill", style={"fontSize": "2rem", "color": icon_color}),
            style={
                "width": "80px", "height": "80px", "display": "flex",
                "alignItems": "center", "justifyContent": "center",
                "borderRadius": "6px", "border": "1px solid #dee2e6", "background": "#f8f9fa"
            }
        )

    return html.Div([
        html.Div([
            thumb,
            html.Button(
                html.I(className="bi bi-x-lg"),
                id={"type": "btn-remove-file", "index": i},
                className="btn-close-file", n_clicks=0,
            ),
        ], className="file-preview-card"),
        html.Div(fname, className="text-muted", style={
            "fontSize": "0.7rem", "maxWidth": "80px",
            "overflow": "hidden", "textOverflow": "ellipsis",
            "whiteSpace": "nowrap", "textAlign": "center"
        }),
    ], style={"display": "inline-block"})


# número de colunas na tabela
_N_COLS = 7
# numero de outputs do callback do modal
_N_MODAL_OUTPUTS = 17


# modal para nova / editar transação
transacao_modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Transação", id="modal-titulo")),

    dbc.ModalBody([
        dbc.Form([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Descrição *"),
                    dbc.Input(
                        type="text",
                        placeholder="Ex: Pagamento Cliente X",
                        id="form-descricao"
                    )
                ], md=8),

                dbc.Col([
                    dbc.Label("Data *"),
                    dbc.Input(type="date", id="form-data")
                ], md=4),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Tipo *"),
                    dbc.Select(options=[
                        {"label": "Entrada", "value": "ENTRADA"},
                        {"label": "Saída", "value": "SAIDA"},
                    ], id="form-tipo")
                ], md=4),

                dbc.Col([
                    dbc.Label("Valor (R$) *"),
                    dbc.Input(
                        type="number",
                        placeholder="0.00",
                        id="form-valor",
                        step="0.01"
                    )
                ], md=4),

                dbc.Col([
                    dbc.Label("Situação"),
                    dbc.Select(options=[
                        {"label": "Pago", "value": "Pago"},
                        {"label": "Recebido", "value": "Recebido"},
                        {"label": "A Pagar", "value": "A Pagar"},
                        {"label": "A Receber", "value": "A Receber"},
                    ], id="form-situacao")
                ], md=4),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Conta *"),
                    dbc.Select(
                        id="form-conta",
                        placeholder="Selecione a Conta..."
                    )
                ], md=4),

                dbc.Col([
                    dbc.Label("Categoria"),
                    dbc.Select(
                        id="form-categoria",
                        placeholder="Opcional..."
                    )
                ], md=4),

                dbc.Col([
                    dbc.Label("Forma de Pagamento"),
                    dbc.Select(
                        id="form-forma-pagamento",
                        placeholder="Opcional..."
                    )
                ], md=4),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Parcela Atual"),
                    dbc.Input(
                        type="number",
                        placeholder="Ex: 1",
                        id="form-numero-parcela",
                        step=1,
                        min=1
                    )
                ], md=3),

                dbc.Col([
                    dbc.Label("Total de Parcelas"),
                    dbc.Input(
                        type="number",
                        placeholder="Ex: 12",
                        id="form-total-parcelas",
                        step=1,
                        min=1
                    )
                ], md=3),

                dbc.Col([
                    dbc.Label("Subcategoria"),
                    dbc.Select(options=[
                        {"label": "Pendente", "value": "PENDENTE"},
                        {"label": "Receita", "value": "RECEITA"},
                        {"label": "Custo", "value": "CUSTO"},
                        {"label": "Custo Fixo", "value": "CUSTO_FIXO"},
                    ], id="form-subcategoria", value="PENDENTE")
                ], md=6),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Identificação / Observações"),
                    dbc.Textarea(
                        placeholder="Adicione informações adicionais sobre esta transação...",
                        id="form-identificacao",
                        rows=3
                    )
                ])
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Arquivos Anexados"),
                    html.Div(
                        id="modal-files-preview",
                        className="d-flex flex-wrap gap-2 mb-2"
                    ),
                ])
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Adicionar Arquivos"),
                    dcc.Upload(
                        id="upload-pdf",
                        children=html.Div([
                            html.I(className="bi bi-cloud-arrow-up me-2"),
                            "Arraste ou ",
                            html.A("selecione arquivos", className="text-primary fw-bold")
                        ]),
                        style={
                            "width": "100%",
                            "height": "60px",
                            "lineHeight": "60px",
                            "borderWidth": "2px",
                            "borderStyle": "dashed",
                            "borderRadius": "8px",
                            "textAlign": "center",
                            "cursor": "pointer",
                            "borderColor": "#ccc"
                        },
                        multiple=True
                    ),
                ])
            ])
        ]),

        html.Div(id="msg-transacao", className="mt-3"),

        html.Div([
            dbc.Button(
                "Criar mesmo assim",
                id="btn-confirmar-transacao-duplicada",
                color="primary",
                className="me-2"
            ),
            dbc.Button(
                "Cancelar",
                id="btn-cancelar-transacao-duplicada",
                color="danger"
            )
        ], id="acoes-transacao-duplicada", className="mt-2", style={"display": "none"})
    ]),

    dbc.ModalFooter([
        dbc.Button(
            "Cancelar",
            id="btn-cancelar",
            color="secondary",
            outline=True,
            className="ms-auto"
        ),
        dbc.Button(
            "Salvar Transação",
            id="btn-salvar",
            color="primary"
        )
    ]),
], id="modal-transacao", is_open=False, size="lg")
    

modal_categorias = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Gerenciar Categorias")),

    dbc.ModalBody([
        html.Div(id="msg-categoria", className="mb-3"),

        dbc.Row([
            dbc.Col([
                dbc.Label("Nome da categoria"),
                dbc.Input(id="input-nome-categoria", placeholder="Ex: Alimentação")
            ], md=8),

            dbc.Col([
                dbc.Label("Filtro"),
                dbc.Select(
                    id="filtro-status-categoria",
                    options=[
                        {"label": "Ativas", "value": "ativas"},
                        {"label": "Desativadas", "value": "desativadas"},
                    ],
                    value="ativas"
                )
            ], md=4),
        ], className="mb-3"),

        dbc.Button(
            "Criar Categoria",
            id="btn-criar-categoria",
            color="primary",
            className="mb-3"
        ),

        dcc.Store(id="store-categoria-editando"),

        html.Div(id="lista-categorias")
    ]),

    dbc.ModalFooter([
        dbc.Button("Fechar", id="btn-fechar-categorias", color="secondary")
    ])
], id="modal-categorias", is_open=False, size="lg")

# layout

layout = dbc.Container([
    dcc.Store(id="store-transacoes"),
    dcc.Store(id="store-contas"),
    dcc.Store(id="store-transacao-pendente"),
    dcc.Store(id="store-categorias"),
    dcc.Store(id="store-formas-pagamento"),
    dcc.Store(id="store-transacao-editando", data=None),
    dcc.Store(id="store-modal-files", data=[]),

    transacao_modal,
    modal_categorias,

    dbc.Row(
        dbc.Col(html.H2("Gerenciamento de Transações", className="fw-normal text-dark"), width="auto"),
        className="my-4 align-items-center"
    ),

    # filtros
    dbc.Card([
        dbc.CardBody([
            html.H5("Filtros de Busca", className="card-title mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Descrição"),
                    dbc.Input(id="filtro-descricao", placeholder="Buscar por palavra-chave...", type="text"),
                ], md=4),
                dbc.Col([
                    dbc.Label("Tipo"),
                    dbc.Select(id="filtro-tipo", options=[
                        {"label": "Todos", "value": "todos"},
                        {"label": "Receita", "value": "ENTRADA"},
                        {"label": "Despesa", "value": "SAIDA"},
                    ], value="todos"),
                ], md=2),
                dbc.Col([
                    dbc.Label("Data Inicial"),
                    dbc.Input(id="filtro-data-inicial", type="date"),
                ], md=3),
                dbc.Col([
                    dbc.Label("Data Final"),
                    dbc.Input(id="filtro-data-final", type="date"),
                ], md=3),
            ], className="g-3"),
        ])
    ], className="mb-4 shadow-sm"),

    # botoes de acao
    dbc.Row([
        dbc.Col([
            dbc.Button("Nova Transação", id="btn-nova-transacao", color="success", className="mb-2 me-sm-2 shadow-sm fw-bold"),
            dbc.Button("Editar Selecionada", id="btn-editar", color="warning", className="mb-2 me-sm-2 text-white shadow-sm fw-bold"),
            dbc.Button("Excluir Selecionadas", id="btn-excluir", color="danger", className="mb-2 me-sm-2 shadow-sm fw-bold"),
            dbc.Button(
            "Gerenciar Categorias",
            id="btn-gerenciar-categorias",
            color="primary",
            className="mb-2 shadow-sm fw-bold"
            ),
        ], width=12, className="mb-3 d-flex justify-content-start flex-wrap")
    ]),

    # tabela
    dbc.Card([
        dbc.CardHeader("Registros Encontrados", className="fw-bold"),
        dbc.Table([
            html.Thead(html.Tr([
                html.Th("", style={"width": "40px"}),
                html.Th("Data"),
                html.Th("Descrição"),
                html.Th("Categoria"),
                html.Th("Conta"),
                html.Th("Valor"),
                html.Th("Situação")
            ])),
            html.Tbody(id="tbody-transacoes")
        ], striped=True, hover=True, responsive=True, className="mb-0")
    ], className="shadow-sm")

], fluid=True, className="py-2")


# callbacks

@callback(
    Output("store-transacoes", "data"),
    Output("store-contas", "data"),
    Output("store-categorias", "data"),
    Output("store-formas-pagamento", "data"),
    Input("url", "pathname")
)
def carregar_dados_banco(pathname):
    if pathname != "/transacoes":
        raise PreventUpdate

    user_id = obter_user_id_logado()

    transacoes = listar_transacoes(user_id).data
    contas = listar_contas().data
    categorias = listar_categorias().data
    formas_pagamento = listar_forma_pagamento(user_id).data

    return transacoes, contas, categorias, formas_pagamento


@callback(
    Output("form-conta", "options"),
    Output("form-categoria", "options"),
    Output("form-forma-pagamento", "options"),
    Input("store-contas", "data"),
    Input("store-categorias", "data"),
    Input("store-formas-pagamento", "data"),
)

def carregar_options(contas, categorias, formas):
    contas = [
        {"label": c["nome"], "value": c["id_conta"]}
        for c in (contas or [])
    ]

    categorias = [
        {"label": c["nome"], "value": c["id_categoria"]}
        for c in (categorias or [])
    ]

    formas = [
        {"label": f["nome"], "value": f["id_forma_pagamento"]}
        for f in (formas or [])
    ]

    return contas, categorias, formas


@callback(
    Output("tbody-transacoes", "children"),
    Input("store-transacoes", "data"),
    Input("store-contas", "data"),
    Input("store-categorias", "data"),
    Input("store-formas-pagamento", "data"),
    Input("filtro-descricao", "value"),
    Input("filtro-tipo", "value"),
    Input("filtro-data-inicial", "value"),
    Input("filtro-data-final", "value")
)

def render_table_rows(store_data, contas, categorias, formas_pagamento, f_desc, f_tipo, f_data_ini, f_data_fim):
    if not store_data:
        return []

    lookup_cat = {
        c["id_categoria"]: c["nome"]
        for c in (categorias or [])
    }

    lookup_conta = {
        c["id_conta"]: c["nome"]
        for c in (contas or [])
    }

    lookup_fp = {
        f["id_forma_pagamento"]: f["nome"]
        for f in (formas_pagamento or [])
    }

    rows = []

    for t in store_data:
        if f_desc and f_desc.lower() not in t.get("descricao", "").lower():
            continue

        if f_tipo and f_tipo != "todos" and t.get("tipo") != f_tipo:
            continue

        if f_data_ini and (t.get("data") or "") < f_data_ini:
            continue

        if f_data_fim and (t.get("data") or "") > f_data_fim:
            continue

        tid = t["id_transacao"]

        categoria_nome = lookup_cat.get(t.get("id_categoria"), "")
        subcategoria = t.get("subcategoria") or ""

        incompleta = (
            not t.get("descricao")
            or not t.get("data")
            or t.get("valor") is None
            or not t.get("id_conta")
            or not t.get("tipo")
            or not t.get("situacao")
            or categoria_nome.upper() == "PENDENTE"
            or subcategoria.upper() == "PENDENTE"
        )

        row_class = "table-warning" if incompleta else ""

        desc_content = [
            html.I(className="bi bi-chevron-down me-2"),
            t.get("descricao", "")
        ]

        if incompleta:
            desc_content.append(
                dbc.Badge(
                    "Incompleta",
                    color="warning",
                    className="ms-2 text-dark"
                )
            )

        files = t.get("files") or []
        n_files = len(files)

        if n_files > 0:
            desc_content.append(
                dbc.Badge(
                    [
                        html.I(className="bi bi-paperclip me-1"),
                        str(n_files)
                    ],
                    color="secondary",
                    className="ms-2"
                )
            )

        val_num = float(t.get("valor") or 0)
        valor_str, valor_color = formata_valor(val_num, t.get("tipo", ""))
        situacao = t.get("situacao", "PENDENTE")

        main_row = html.Tr([
            html.Td(
                dbc.Checkbox(
                    value=False,
                    id={
                        "type": "checkbox-transacao",
                        "index": tid
                    }
                )
            ),
            html.Td(formata_data(t.get("data", ""))),
            html.Td(desc_content),
            html.Td(categoria_nome),
            html.Td(lookup_conta.get(t.get("id_conta"), "")),
            html.Td(valor_str, className=f"fw-bold {valor_color}"),
            html.Td(
                dbc.Badge(
                    situacao,
                    color=cor_situacao(situacao)
                )
            )
        ],
            id={
                "type": "row",
                "index": tid
            },
            style={"cursor": "pointer"},
            className=row_class
        )

        detail_children = []

        parcela_str = (
            f"{t.get('numero_parcela') or '-'} "
            f"de {t.get('total_parcelas') or '-'}"
        )

        detail_children.append(
            html.P([
                html.Strong("Identificação: "),
                html.Span(t.get("identificacao") or "Nenhuma"),
                html.Br(),

                html.Strong("Tipo: "),
                html.Span(t.get("tipo", "")),

                html.Strong(" | Forma de Pagamento: "),
                html.Span(
                    lookup_fp.get(
                        t.get("id_forma_pagamento"),
                        "—"
                    )
                ),
                html.Br(),

                html.Strong("Parcelas: "),
                html.Span(parcela_str),

                html.Strong(" | Subcategoria: "),
                html.Span(subcategoria),
            ],
                className="small text-muted"
            )
        )

        if files:
            detail_children.append(
                html.H6(
                    [
                        html.I(className="bi bi-paperclip me-2"),
                        f"Anexos ({len(files)})"
                    ],
                    className="mt-3 fw-bold text-muted"
                )
            )

            detail_children.append(
                html.Div(
                    [
                        render_file_preview(f)
                        for f in files
                    ],
                    className="d-flex flex-wrap gap-3 mt-2"
                )
            )

        collapse_row = html.Tr([
            html.Td(
                dbc.Collapse(
                    dbc.Card(
                        dbc.CardBody([
                            html.H6(
                                "Detalhes da Transação",
                                className="fw-bold"
                            ),
                            *detail_children
                        ]),
                        className="border-0 bg-light"
                    ),
                    id={
                        "type": "collapse",
                        "index": tid
                    },
                    is_open=False,
                ),
                colSpan=_N_COLS,
                className="p-0 border-0"
            )
        ])

        rows.extend([main_row, collapse_row])

    return rows

@callback(
    Output({"type": "collapse", "index": MATCH}, "is_open"),
    Input({"type": "row", "index": MATCH}, "n_clicks"),
    State({"type": "collapse", "index": MATCH}, "is_open"),
    prevent_initial_call=True
)
def toggle_collapse(n, is_open):
    return not is_open if n else is_open


@callback(
    Output("store-modal-files", "data"),
    Output("modal-files-preview", "children"),
    [
        Input("upload-pdf", "contents"),
        Input({"type": "btn-remove-file", "index": ALL}, "n_clicks"),
    ],
    [
        State("upload-pdf", "filename"),
        State("store-modal-files", "data"),
    ],
    prevent_initial_call=True
)
def gerenciar_arquivos_modal(new_contents, _remove_clicks, new_filenames, current_files):
    triggered = ctx.triggered_id
    current_files = current_files or []

    if triggered == "upload-pdf" and new_contents:
        if isinstance(new_contents, list):
            current_files.extend({"contents": c, "filename": f} for c, f in zip(new_contents, new_filenames))
        else:
            current_files.append({"contents": new_contents, "filename": new_filenames})

    elif isinstance(triggered, dict) and triggered.get("type") == "btn-remove-file":
        idx = triggered["index"]
        if 0 <= idx < len(current_files):
            current_files.pop(idx)

    previews = [render_modal_thumb(i, f) for i, f in enumerate(current_files)]
    if not previews:
        previews = html.Span("Nenhum arquivo anexado.", className="text-muted small")

    return current_files, previews

def renderizar_lista_categorias(categorias, status):
    if not categorias:
        return dbc.Alert("Nenhuma categoria encontrada.", color="secondary")

    itens = []

    for cat in categorias:
        nome = cat["nome"]
        id_cat = cat["id_categoria"]

        if status == "ativas":
            botoes = []

            if nome != "Pendente":
                botoes = [
                    dbc.Button(
                        "Editar",
                        id={"type": "btn-editar-categoria", "index": id_cat},
                        color="warning",
                        size="sm",
                        className="me-2 text-white"
                    ),
                    dbc.Button(
                        "Desativar",
                        id={"type": "btn-desativar-categoria", "index": id_cat},
                        color="danger",
                        size="sm"
                    )
                ]

            else:
                botoes = [
                    dbc.Badge("Sistema", color="secondary")
                ]

        else:
            botoes = [
                dbc.Button(
                    "Reativar",
                    id={"type": "btn-reativar-categoria", "index": id_cat},
                    color="success",
                    size="sm"
                )
            ]

        itens.append(
            dbc.ListGroupItem([
                html.Div([
                    html.Strong(nome),
                    html.Div(botoes)
                ], className="d-flex justify-content-between align-items-center")
            ])
        )

    return dbc.ListGroup(itens, flush=True)

@callback(
    Output("modal-categorias", "is_open"),
    Output("msg-categoria", "children", allow_duplicate=True),
    Input("btn-gerenciar-categorias", "n_clicks"),
    Input("btn-fechar-categorias", "n_clicks"),
    State("modal-categorias", "is_open"),
    prevent_initial_call=True
)

def abrir_fechar_modal_categorias(n_abrir, n_fechar, is_open):
    return not is_open, ""

@callback(
    Output("lista-categorias", "children"),
    Input("modal-categorias", "is_open"),
    Input("filtro-status-categoria", "value"),
    Input("store-categorias", "data")
)

def carregar_lista_categorias_modal(is_open, status, _):
    if not is_open:
        raise PreventUpdate

    user_id = obter_user_id_logado()
    todas = listar_todas_categorias(user_id).data

    if status == "desativadas":
        categorias = [c for c in todas if c.get("deletado") is not None]
    else:
        categorias = [c for c in todas if c.get("deletado") is None]

    return renderizar_lista_categorias(categorias, status)


@callback(
    Output("input-nome-categoria", "value"),
    Output("store-categoria-editando", "data"),
    Output("btn-criar-categoria", "children"),
    Output("msg-categoria", "children", allow_duplicate=True),
    Input({"type": "btn-editar-categoria", "index": ALL}, "n_clicks"),
    State({"type": "btn-editar-categoria", "index": ALL}, "id"),
    State("store-categorias", "data"),
    prevent_initial_call=True
)

def preparar_edicao_categoria(n_clicks, ids_editar, categorias):
    triggered = ctx.triggered_id

    if not triggered:
        raise PreventUpdate

    index = next(
        (i for i, item in enumerate(ids_editar or []) if item["index"] == triggered["index"]),
        None
    )

    if index is None or not n_clicks[index]:
        raise PreventUpdate

    id_cat = triggered["index"]

    categoria = next(
        (c for c in (categorias or []) if c["id_categoria"] == id_cat),
        None
    )

    if not categoria:
        raise PreventUpdate

    return categoria["nome"], id_cat, "Salvar Alteração", ""


@callback(
    Output("msg-categoria", "children", allow_duplicate=True),
    Output("store-categorias", "data", allow_duplicate=True),
    Output("input-nome-categoria", "value", allow_duplicate=True),
    Output("store-categoria-editando", "data", allow_duplicate=True),
    Output("btn-criar-categoria", "children", allow_duplicate=True),
    Input("btn-criar-categoria", "n_clicks"),
    State("input-nome-categoria", "value"),
    State("store-categoria-editando", "data"),
    prevent_initial_call=True
)

def salvar_categoria_modal(n_clicks, nome, categoria_editando):
    if not nome:
        return (
            dbc.Alert("Informe o nome da categoria.", color="warning"),
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update
        )

    user_id = obter_user_id_logado()

    try:
        if categoria_editando:
            editar_categoria(categoria_editando, nome, user_id)
            mensagem = "Categoria editada com sucesso."
        else:
            criar_categoria(nome, user_id)
            mensagem = "Categoria criada/reativada com sucesso."

        categorias = listar_categorias().data

        return (
            dbc.Alert(mensagem, color="success"),
            categorias,
            "",
            None,
            "Criar Categoria"
        )

    except Exception as e:
        return (
            dbc.Alert(str(e), color="danger"),
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update
        )


@callback(
    Output("msg-categoria", "children", allow_duplicate=True),
    Output("store-categorias", "data", allow_duplicate=True),
    Output("input-nome-categoria", "value", allow_duplicate=True),
    Output("store-categoria-editando", "data", allow_duplicate=True),
    Output("btn-criar-categoria", "children", allow_duplicate=True),
    Input({"type": "btn-desativar-categoria", "index": ALL}, "n_clicks"),
    Input({"type": "btn-reativar-categoria", "index": ALL}, "n_clicks"),
    State({"type": "btn-desativar-categoria", "index": ALL}, "id"),
    State({"type": "btn-reativar-categoria", "index": ALL}, "id"),
    prevent_initial_call=True
)

def alterar_status_categoria(n_desativar, n_reativar, ids_desativar, ids_reativar):
    triggered = ctx.triggered_id

    if not triggered:
        raise PreventUpdate

    if triggered["type"] == "btn-desativar-categoria":
        index = next(
            (i for i, item in enumerate(ids_desativar or []) if item["index"] == triggered["index"]),
            None
        )

        if index is None or not n_desativar[index]:
            raise PreventUpdate

    if triggered["type"] == "btn-reativar-categoria":
        index = next(
            (i for i, item in enumerate(ids_reativar or []) if item["index"] == triggered["index"]),
            None
        )

        if index is None or not n_reativar[index]:
            raise PreventUpdate

    user_id = obter_user_id_logado()
    id_cat = triggered["index"]

    try:
        if triggered["type"] == "btn-desativar-categoria":
            excluir_categoria(id_cat, user_id)
            mensagem = "Categoria desativada com sucesso."
        else:
            reativar_categoria(id_cat, user_id)
            mensagem = "Categoria reativada com sucesso."

        categorias = listar_categorias().data

        return (
            dbc.Alert(mensagem, color="success"),
            categorias,
            "",
            None,
            "Criar Categoria"
        )

    except Exception as e:
        return (
            dbc.Alert(str(e), color="danger"),
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update
        )


@callback(
    Output("store-transacoes", "data", allow_duplicate=True),
    Output("msg-transacao", "children", allow_duplicate=True),
    Output("store-transacao-pendente", "data", allow_duplicate=True),
    Output("acoes-transacao-duplicada", "style", allow_duplicate=True),
    Output("modal-transacao", "is_open", allow_duplicate=True),
    Input("btn-salvar", "n_clicks"),
    State("store-transacao-editando", "data"),
    State("form-descricao", "value"),
    State("form-data", "value"),
    State("form-tipo", "value"),
    State("form-valor", "value"),
    State("form-situacao", "value"),
    State("form-conta", "value"),
    State("form-categoria", "value"),
    State("form-forma-pagamento", "value"),
    State("form-numero-parcela", "value"),
    State("form-total-parcelas", "value"),
    State("form-subcategoria", "value"),
    State("form-identificacao", "value"),
    State("store-categorias", "data"),
    prevent_initial_call=True
)

def salvar_transacao(
    n_salvar,
    edit_id,
    desc,
    data_val,
    tipo,
    val_num,
    situacao,
    conta,
    cat,
    fp,
    num_parc,
    tot_parc,
    subcat,
    ident,
    categorias
):
    if not n_salvar:
        raise PreventUpdate

    user_id = obter_user_id_logado()

    if not desc or not data_val or not val_num or not conta or not tipo:
        return (
            dash.no_update,
            dbc.Alert("Preencha descrição, data, valor, conta e tipo.", color="warning"),
            dash.no_update,
            {"display": "none"},
            True
        )

    valor = abs(float(val_num))

    if tipo == "SAIDA":
        valor = -valor

    if not cat:
        cat = next(
        (
            c["id_categoria"]
            for c in (categorias or [])
            if c["nome"].upper() == "PENDENTE"
        ),
        None
    )
    
    dados = {
        "descricao": desc,
        "data": data_val,
        "tipo": tipo,
        "valor": valor,
        "situacao": situacao or "Pago",
        "id_conta": conta,
        "id_categoria": cat,
        "id_forma_pagamento": fp,
        "numero_parcela": num_parc,
        "total_parcelas": tot_parc,
        "subcategoria": subcat or "PENDENTE",
        "identificacao": ident,
        "id_importacao": None
    }

    if edit_id:
        editar_transacao(edit_id, dados, user_id)

        return (
            listar_transacoes(user_id).data,
            dbc.Alert("Transação atualizada com sucesso.", color="success"),
            None,
            {"display": "none"},
        )

    resultado = criar_transacao(dados, user_id)

    if isinstance(resultado, dict) and resultado.get("status") == "duplicatas_encontradas":
        return (
            dash.no_update,
            dbc.Alert(resultado["mensagem"], color="warning"),
            dados,
            {"display": "block"},
            True
        )

    return (
        listar_transacoes(user_id).data,
        dbc.Alert("Transação criada com sucesso.", color="success"),
        None,
        {"display": "none"},
        False
    )

@callback(
    Output("store-transacoes", "data", allow_duplicate=True),
    Output("msg-transacao", "children", allow_duplicate=True),
    Output("store-transacao-pendente", "data", allow_duplicate=True),
    Output("acoes-transacao-duplicada", "style", allow_duplicate=True),
    Output("modal-transacao", "is_open", allow_duplicate=True),
    Input("btn-confirmar-transacao-duplicada", "n_clicks"),
    State("store-transacao-pendente", "data"),
    prevent_initial_call=True
)

def confirmar_transacao_duplicada(n_clicks, dados):
    if not dados:
        return (
            dash.no_update,
            dbc.Alert("Nenhuma transação pendente.", color="warning"),
            dash.no_update,
            {"display": "none"}
        )

    user_id = obter_user_id_logado()

    criar_transacao(
        dados,
        user_id,
        confirmar_duplicata=True
    )

    return (
        listar_transacoes(user_id).data,
        dbc.Alert("Transação criada mesmo com duplicata.", color="success"),
        None,
        {"display": "none"},
        False
    )


@callback(
    Output("msg-transacao", "children", allow_duplicate=True),
    Output("store-transacao-pendente", "data", allow_duplicate=True),
    Output("acoes-transacao-duplicada", "style", allow_duplicate=True),
    Input("btn-cancelar-transacao-duplicada", "n_clicks"),
    prevent_initial_call=True
)

def cancelar_transacao_duplicada(n_clicks):
    return (
        dbc.Alert("Criação da transação cancelada.", color="secondary"),
        None,
        {"display": "none"}
    )

@callback(
    Output("modal-transacao", "is_open"),
    Output("modal-titulo", "children"),
    Output("form-descricao", "value"),
    Output("form-data", "value"),
    Output("form-tipo", "value"),
    Output("form-valor", "value"),
    Output("form-situacao", "value"),
    Output("form-conta", "value"),
    Output("form-categoria", "value"),
    Output("form-forma-pagamento", "value"),
    Output("form-numero-parcela", "value"),
    Output("form-total-parcelas", "value"),
    Output("form-subcategoria", "value"),
    Output("form-identificacao", "value"),
    Output("store-transacao-editando", "data"),
    Output("msg-transacao", "children", allow_duplicate=True),
    Output("store-modal-files", "data", allow_duplicate=True),
    [
        Input("btn-nova-transacao", "n_clicks"),
        Input("btn-editar", "n_clicks"),
        Input("btn-cancelar", "n_clicks"),
    ],
    [
        State("modal-transacao", "is_open"),
        State({"type": "checkbox-transacao", "index": ALL}, "value"),
        State({"type": "checkbox-transacao", "index": ALL}, "id"),
        State("store-transacoes", "data"),
        State("store-categorias", "data")
    ],
    prevent_initial_call=True
)
def gerenciar_modal(n_nova, n_editar, n_cancelar, is_open, check_values, check_ids, store_data, categorias):
    triggered = ctx.triggered_id
    no_change = [dash.no_update] * _N_MODAL_OUTPUTS

    categoria_pendente = next(
    (
        c["id_categoria"]
        for c in (categorias or [])
        if c["nome"].upper() == "PENDENTE"
    ),
    None
)

    if triggered == "btn-nova-transacao":
        return (
            True, "Criar Nova Transação",
            "", "", "SAIDA", None, "A Pagar",
            None, categoria_pendente, None,
            None, None, "PENDENTE", "",
            None, [],
            ""
        )

    if triggered == "btn-editar":
        selected_id = next(
            (cid["index"] for val, cid in zip(check_values or [], check_ids or []) if val),
            None
        )

        if not selected_id:
            return no_change

        t = next(
            (t for t in (store_data or []) if t["id_transacao"] == selected_id),
            None
        )

        if not t:
            return no_change

        return (
            True, "Editar Transação",
            t.get("descricao", ""),
            t.get("data", ""),
            t.get("tipo", "SAIDA"),
            abs(float(t.get("valor") or 0)),
            t.get("situacao", "A Pagar"),
            t.get("id_conta"),
            t.get("id_categoria"),
            t.get("id_forma_pagamento"),
            t.get("numero_parcela"),
            t.get("total_parcelas"),
            t.get("subcategoria", "PENDENTE"),
            t.get("identificacao", ""),
            selected_id,
            t.get("files", []),
            ""
        )

    if triggered in ("btn-cancelar"):
        return [False] + [dash.no_update] * (_N_MODAL_OUTPUTS - 1)

    return no_change


@callback(
    Output("store-transacoes", "data", allow_duplicate=True),
    Input("btn-excluir", "n_clicks"),
    State({"type": "checkbox-transacao", "index": ALL}, "value"),
    State({"type": "checkbox-transacao", "index": ALL}, "id"),
    prevent_initial_call=True
)
def excluir_transacoes_selecionadas(n_clicks, check_values, check_ids):
    if not n_clicks or not check_values:
        raise PreventUpdate

    ids_to_delete = {
        cid["index"]
        for val, cid in zip(check_values, check_ids)
        if val
    }

    if not ids_to_delete:
        raise PreventUpdate

    user_id = obter_user_id_logado()

    for id_transacao in ids_to_delete:
        try:
            excluir_transacao(id_transacao, user_id)
        except Exception as e:
            print(f"Erro ao excluir transação {id_transacao}: {e}")

    return listar_transacoes(user_id).data