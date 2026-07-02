import dash
from dash import html, dcc, Input, Output, State, callback, MATCH, ALL, ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import uuid

dash.register_page(__name__, path='/transacoes', name='Transações')

# mock uuids
user_id_mock = str(uuid.uuid4())
conta_1 = str(uuid.uuid4())
conta_2 = str(uuid.uuid4())
conta_3 = str(uuid.uuid4())
cat_servicos = str(uuid.uuid4())
cat_hardware = str(uuid.uuid4())
cat_ferramentas = str(uuid.uuid4())
fp_pix = str(uuid.uuid4())
fp_cartao = str(uuid.uuid4())

mock_contas = [
    {"label": "Bradesco", "value": conta_1},
    {"label": "Nubank", "value": conta_2},
    {"label": "Cora", "value": conta_3},
]
mock_categorias = [
    {"label": "Serviços", "value": cat_servicos},
    {"label": "Hardware", "value": cat_hardware},
    {"label": "Ferramentas", "value": cat_ferramentas},
]
mock_formas_pagamento = [
    {"label": "Pix", "value": fp_pix},
    {"label": "Cartão de Crédito", "value": fp_cartao},
]

# mock data das transações
mock_transacoes = [
    {
        "id_transacao": str(uuid.uuid4()),
        "id_usuario": user_id_mock,
        "id_categoria": cat_servicos,
        "id_importacao": None,
        "valor": 9000.00,
        "data": "2026-06-18",
        "descricao": "WebApp de Gerenciamento Financeiro",
        "tipo": "RECEITA",
        "situacao": "RECEBIDO",
        "identificacao": "Projeto completo incluindo frontend, backend e integração. Pagamento cliente Focus Consultoria.",
        "numero_parcela": 1,
        "total_parcelas": 1,
        "id_conta": conta_1,
        "id_forma_pagamento": fp_pix,
        "subcategoria": "PENDENTE",
        "files": [],
        "incompleta": False
    },
    {
        "id_transacao": str(uuid.uuid4()),
        "id_usuario": user_id_mock,
        "id_categoria": cat_hardware,
        "id_importacao": None,
        "valor": 4500.00,
        "data": "2026-06-24",
        "descricao": "Compra de Equipamentos",
        "tipo": "DESPESA",
        "situacao": "PENDENTE",
        "identificacao": "Faltam informações sobre o valor da parcela e notas fiscais.",
        "numero_parcela": 1,
        "total_parcelas": 12,
        "id_conta": conta_2,
        "id_forma_pagamento": fp_cartao,
        "subcategoria": "PENDENTE",
        "files": [],
        "incompleta": True
    }
]


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
    if tipo == "DESPESA":
        return f"- {valor_str}", "text-danger"
    return valor_str, "text-success"

def cor_situacao(situacao):
    if situacao in ("PAGO", "RECEBIDO"):
        return "success"
    if situacao == "PENDENTE":
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
_N_MODAL_OUTPUTS = 16


# modal para nova / editar transação
transacao_modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Transação", id="modal-titulo")),
    dbc.ModalBody(
        dbc.Form([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Descrição *"),
                    dbc.Input(type="text", placeholder="Ex: Pagamento Cliente X", id="form-descricao")
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
                        {"label": "Receita", "value": "RECEITA"},
                        {"label": "Despesa", "value": "DESPESA"},
                    ], id="form-tipo")
                ], md=4),
                dbc.Col([
                    dbc.Label("Valor (R$) *"),
                    dbc.Input(type="number", placeholder="0.00", id="form-valor", step="0.01")
                ], md=4),
                dbc.Col([
                    dbc.Label("Situação"),
                    dbc.Select(options=[
                        {"label": "Pago/Recebido", "value": "PAGO"},
                        {"label": "Pendente", "value": "PENDENTE"},
                        {"label": "Cancelado", "value": "CANCELADO"},
                    ], id="form-situacao")
                ], md=4),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Conta *"),
                    dbc.Select(options=mock_contas, id="form-conta", placeholder="Selecione a Conta...")
                ], md=4),
                dbc.Col([
                    dbc.Label("Categoria"),
                    dbc.Select(options=mock_categorias, id="form-categoria", placeholder="Opcional...")
                ], md=4),
                dbc.Col([
                    dbc.Label("Forma de Pagamento"),
                    dbc.Select(options=mock_formas_pagamento, id="form-forma-pagamento", placeholder="Opcional...")
                ], md=4),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Parcela Atual"),
                    dbc.Input(type="number", placeholder="Ex: 1", id="form-numero-parcela", step=1, min=1)
                ], md=3),
                dbc.Col([
                    dbc.Label("Total de Parcelas"),
                    dbc.Input(type="number", placeholder="Ex: 12", id="form-total-parcelas", step=1, min=1)
                ], md=3),
                dbc.Col([
                    dbc.Label("Subcategoria"),
                    dbc.Select(options=[
                        {"label": "Pendente", "value": "PENDENTE"},
                        {"label": "Fixa", "value": "FIXA"},
                        {"label": "Variável", "value": "VARIAVEL"},
                    ], id="form-subcategoria", value="PENDENTE")
                ], md=6),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Identificação / Observações"),
                    dbc.Textarea(placeholder="Adicione informações adicionais sobre esta transação...", id="form-identificacao", rows=3)
                ])
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Arquivos Anexados"),
                    html.Div(id="modal-files-preview", className="d-flex flex-wrap gap-2 mb-2"),
                ])
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Adicionar Arquivos"),
                    dcc.Upload(
                        id='upload-pdf',
                        children=html.Div([
                            html.I(className="bi bi-cloud-arrow-up me-2"),
                            'Arraste ou ',
                            html.A('selecione arquivos', className="text-primary fw-bold")
                        ]),
                        style={
                            'width': '100%', 'height': '60px', 'lineHeight': '60px',
                            'borderWidth': '2px', 'borderStyle': 'dashed', 'borderRadius': '8px',
                            'textAlign': 'center', 'cursor': 'pointer', 'borderColor': '#ccc'
                        },
                        multiple=True
                    ),
                ])
            ])
        ])
    ),
    dbc.ModalFooter([
        dbc.Button("Cancelar", id="btn-cancelar", color="secondary", outline=True, className="ms-auto"),
        dbc.Button("Salvar Transação", id="btn-salvar", color="primary")
    ]),
], id="modal-transacao", is_open=False, size="lg")


# layout

layout = dbc.Container([
    dcc.Store(id="store-transacoes", data=mock_transacoes),
    dcc.Store(id="store-transacao-editando", data=None),
    dcc.Store(id="store-modal-files", data=[]),

    transacao_modal,

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
                        {"label": "Receita", "value": "RECEITA"},
                        {"label": "Despesa", "value": "DESPESA"},
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
            dbc.Button("Excluir Selecionadas", id="btn-excluir", color="danger", className="mb-2 shadow-sm fw-bold"),
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
    Output("tbody-transacoes", "children"),
    Input("store-transacoes", "data"),
    Input("filtro-descricao", "value"),
    Input("filtro-tipo", "value"),
    Input("filtro-data-inicial", "value"),
    Input("filtro-data-final", "value")
)
def render_table_rows(store_data, f_desc, f_tipo, f_data_ini, f_data_fim):
    if not store_data:
        return []

    lookup_cat = _build_lookup(mock_categorias)
    lookup_conta = _build_lookup(mock_contas)
    lookup_fp = _build_lookup(mock_formas_pagamento)

    rows = []
    for t in store_data:
        # filtros
        if f_desc and f_desc.lower() not in t.get("descricao", "").lower():
            continue
        if f_tipo and f_tipo != "todos" and t.get("tipo") != f_tipo:
            continue
        if f_data_ini and (t.get("data") or "") < f_data_ini:
            continue
        if f_data_fim and (t.get("data") or "") > f_data_fim:
            continue

        tid = t["id_transacao"]
        row_class = "table-warning" if t.get("incompleta") else ""

        # descrição com badges
        desc_content = [html.I(className="bi bi-chevron-down me-2"), t.get("descricao", "")]
        if t.get("incompleta"):
            desc_content.append(dbc.Badge("Incompleta", color="warning", className="ms-2 text-dark"))
        n_files = len(t.get("files", []))
        if n_files > 0:
            desc_content.append(dbc.Badge([html.I(className="bi bi-paperclip me-1"), str(n_files)], color="secondary", className="ms-2"))

        val_num = float(t.get("valor") or 0)
        valor_str, valor_color = formata_valor(val_num, t.get("tipo", ""))
        situacao = t.get("situacao", "PENDENTE")

        main_row = html.Tr([
            html.Td(dbc.Checkbox(value=False, id={"type": "checkbox-transacao", "index": tid})),
            html.Td(formata_data(t.get("data", ""))),
            html.Td(desc_content),
            html.Td(lookup_cat.get(t.get("id_categoria"), "")),
            html.Td(lookup_conta.get(t.get("id_conta"), "")),
            html.Td(valor_str, className=f"fw-bold {valor_color}"),
            html.Td(dbc.Badge(situacao, color=cor_situacao(situacao)))
        ], id={"type": "row", "index": tid}, style={"cursor": "pointer"}, className=row_class)

        # detalhes expandidos
        files = t.get("files", [])
        detail_children = []

        # info textual
        parcela_str = f"{t.get('numero_parcela') or '-'} de {t.get('total_parcelas') or '-'}"
        detail_children.append(html.P([
            html.Strong("Identificação: "), html.Span(t.get("identificacao") or "Nenhuma"), html.Br(),
            html.Strong("Tipo: "), html.Span(t.get("tipo", "")),
            html.Strong(" | Forma de Pagamento: "), html.Span(lookup_fp.get(t.get("id_forma_pagamento"), "—")), html.Br(),
            html.Strong("Parcelas: "), html.Span(parcela_str),
            html.Strong(" | Subcategoria: "), html.Span(t.get("subcategoria", "")),
        ], className="small text-muted"))

        # anexos
        if files:
            detail_children.append(html.H6([html.I(className="bi bi-paperclip me-2"), f"Anexos ({len(files)})"], className="mt-3 fw-bold text-muted"))
            detail_children.append(html.Div([render_file_preview(f) for f in files], className="d-flex flex-wrap gap-3 mt-2"))

        collapse_row = html.Tr([
            html.Td(
                dbc.Collapse(
                    dbc.Card(dbc.CardBody([
                        html.H6("Detalhes da Transação", className="fw-bold"),
                        *detail_children
                    ]), className="border-0 bg-light"),
                    id={"type": "collapse", "index": tid},
                    is_open=False,
                ),
                colSpan=_N_COLS, className="p-0 border-0"
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


@callback(
    Output("store-transacoes", "data"),
    Input("btn-salvar", "n_clicks"),
    [
        State("store-transacoes", "data"),
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
        State("store-modal-files", "data"),
    ],
    prevent_initial_call=True
)
def salvar_transacao(n_salvar, store_data, edit_id, desc, data_val, tipo, val_num, situacao, conta, cat, fp, num_parc, tot_parc, subcat, ident, modal_files):
    if not n_salvar:
        raise PreventUpdate

    store_data = store_data or []
    modal_files = modal_files or []

    try:
        val_f = abs(float(val_num))
    except (TypeError, ValueError):
        val_f = 0.0

    incompleta = not all([desc, val_num, data_val, conta, tipo])

    campos = {
        "descricao": desc or "",
        "data": data_val or "",
        "tipo": tipo or "DESPESA",
        "valor": val_f,
        "situacao": situacao or "PENDENTE",
        "id_conta": conta,
        "id_categoria": cat,
        "id_forma_pagamento": fp,
        "numero_parcela": num_parc,
        "total_parcelas": tot_parc,
        "subcategoria": subcat or "PENDENTE",
        "identificacao": ident or "",
        "incompleta": incompleta,
        "files": modal_files,
    }

    if edit_id:
        for t in store_data:
            if t["id_transacao"] == edit_id:
                t.update(campos)
                break
    else:
        store_data.insert(0, {
            "id_transacao": str(uuid.uuid4()),
            "id_usuario": user_id_mock,
            "id_importacao": None,
            **campos,
        })

    return store_data


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
    Output("store-modal-files", "data", allow_duplicate=True),
    [
        Input("btn-nova-transacao", "n_clicks"),
        Input("btn-editar", "n_clicks"),
        Input("btn-cancelar", "n_clicks"),
        Input("btn-salvar", "n_clicks"),
    ],
    [
        State("modal-transacao", "is_open"),
        State({"type": "checkbox-transacao", "index": ALL}, "value"),
        State({"type": "checkbox-transacao", "index": ALL}, "id"),
        State("store-transacoes", "data")
    ],
    prevent_initial_call=True
)
def gerenciar_modal(n_nova, n_editar, n_cancelar, n_salvar, is_open, check_values, check_ids, store_data):
    triggered = ctx.triggered_id
    no_change = [dash.no_update] * _N_MODAL_OUTPUTS

    if triggered == "btn-nova-transacao":
        return (True, "Criar Nova Transação", "", "", "DESPESA", None, "PENDENTE",
                None, None, None, None, None, "PENDENTE", "", None, [])

    if triggered == "btn-editar":
        selected_id = next(
            (cid["index"] for val, cid in zip(check_values or [], check_ids or []) if val),
            None
        )
        if not selected_id:
            return no_change

        t = next((t for t in (store_data or []) if t["id_transacao"] == selected_id), None)
        if not t:
            return no_change

        return (
            True, "Editar Transação",
            t.get("descricao", ""), t.get("data", ""),
            t.get("tipo", "DESPESA"), t.get("valor", ""),
            t.get("situacao", "PENDENTE"), t.get("id_conta"),
            t.get("id_categoria"), t.get("id_forma_pagamento"),
            t.get("numero_parcela"), t.get("total_parcelas"),
            t.get("subcategoria", "PENDENTE"), t.get("identificacao", ""),
            selected_id, t.get("files", [])
        )

    if triggered in ("btn-cancelar", "btn-salvar"):
        return [False] + [dash.no_update] * (_N_MODAL_OUTPUTS - 1)

    return no_change


@callback(
    Output("store-transacoes", "data", allow_duplicate=True),
    Input("btn-excluir", "n_clicks"),
    State({"type": "checkbox-transacao", "index": ALL}, "value"),
    State({"type": "checkbox-transacao", "index": ALL}, "id"),
    State("store-transacoes", "data"),
    prevent_initial_call=True
)
def excluir_transacao(n_clicks, check_values, check_ids, store_data):
    if not n_clicks or not check_values or not store_data:
        raise PreventUpdate

    ids_to_delete = {cid["index"] for val, cid in zip(check_values, check_ids) if val}
    if not ids_to_delete:
        raise PreventUpdate

    return [t for t in store_data if t["id_transacao"] not in ids_to_delete]