import dash
from dash import html, Input, Output, callback, dcc, State, ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from services.usuario import listar_usuarios, atualizar_perfil_usuario, deletar_usuario
from supabase_client import supabase

dash.register_page(__name__, path="/admin/usuarios")

COR_BOTAO = "#0067EC"

_PERFIL_INFO = {
    "ADMIN":      {"label": "Administradores", "cor": "#dc3545"},
    "FINANCEIRO": {"label": "Financeiro",      "cor": "#0067EC"},
    "NORMAL":     {"label": "Normal",          "cor": "#6c757d"},
}
_PERFIL_ORDEM = ["ADMIN", "FINANCEIRO", "NORMAL"]


def _obter_user_id_logado():
    session = supabase.auth.get_session()
    if session is None:
        raise Exception("Usuário não autenticado")
    return session.user.id


def _iniciais(nome):
    partes = (nome or "?").strip().split()
    if len(partes) >= 2:
        return (partes[0][0] + partes[1][0]).upper()
    return (partes[0][:2] if partes else "?").upper()


def _avatar(nome, perfil):
    cor = _PERFIL_INFO.get(perfil, _PERFIL_INFO["NORMAL"])["cor"]
    return html.Div(_iniciais(nome), className="user-avatar", style={"backgroundColor": cor})


def _badge_perfil(perfil):
    cor = _PERFIL_INFO.get(perfil, _PERFIL_INFO["NORMAL"])["cor"]
    return dbc.Badge(perfil, className="ms-2", style={
        "backgroundColor": cor, "fontSize": "0.65rem", "fontWeight": "600",
    })


def _linha_usuario(u):
    return html.Div([
        _avatar(u.get("nome", "?"), u.get("perfil", "NORMAL")),
        html.Div([
            html.Div([
                html.Span(u.get("nome", "?"), className="fw-semibold"),
                _badge_perfil(u.get("perfil", "NORMAL")),
            ], className="d-flex align-items-center flex-wrap"),
        ], className="flex-grow-1", style={"minWidth": "0"}),
        html.Div([
            dbc.Select(
                id={"type": "select-perfil", "index": u["id"]},
                options=[
                    {"label": "Normal", "value": "NORMAL"},
                    {"label": "Financeiro", "value": "FINANCEIRO"},
                    {"label": "Admin", "value": "ADMIN"},
                ],
                value=u.get("perfil", "NORMAL"),
                className="select-perfil-usuario",
            ),
            dbc.Button(
                html.I(className="bi bi-trash"),
                id={"type": "btn-deletar-usuario", "index": u["id"]},
                color="danger", size="sm", outline=True,
                className="btn-deletar-usuario",
            ),
        ], className="d-flex align-items-center gap-2 user-acoes"),
    ], className="user-linha")


def _grupo_perfil(perfil, usuarios):
    if not usuarios:
        return None
    info = _PERFIL_INFO[perfil]
    return html.Div([
        html.Div([
            html.H6(info["label"], className="mb-0 fw-bold", style={"color": info["cor"]}),
            dbc.Badge(len(usuarios), color="secondary", className="ms-2", style={"fontSize": "0.7rem"}),
        ], className="d-flex align-items-center mb-3"),
        html.Hr(className="mb-3", style={"borderColor": info["cor"], "opacity": "0.3"}),
        html.Div([_linha_usuario(u) for u in usuarios], className="mb-4"),
    ])


layout = dbc.Container([
    dcc.Location(id="url-admin-usuarios", refresh=False),
    dcc.Store(id="store-user-to-delete"),
    dcc.Store(id="store-perfis-iniciais"),

    dbc.Row([
        dbc.Col([
            dcc.Link(
                dbc.Button(
                    [html.I(className="bi bi-arrow-left me-2"), "Voltar ao painel"],
                    color="secondary", outline=True, size="sm",
                ),
                href="/admin",
                style={"textDecoration": "none"},
            ),
        ], width=12, className="mb-3"),
    ]),

    html.H2("Gerenciar Usuários", className="text-dark mt-4 mb-4 ml-4 fw-bold"),

    html.Div(id="msg-erro-usuarios", className="mb-3"),

    dbc.Card([
        dbc.CardBody([
            html.Div(id="lista-usuarios"),
        ]),
    ], className="shadow-sm"),

    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Confirmar exclusão")),
        dbc.ModalBody("Tem certeza que deseja remover este usuário? Esta ação não pode ser desfeita."),
        dbc.ModalFooter([
            dbc.Button("Cancelar", id="btn-cancelar-delete", color="secondary", outline=True, className="me-2"),
            dbc.Button("Confirmar exclusão", id="btn-confirmar-delete", color="danger"),
        ]),
    ], id="modal-confirm-delete", is_open=False, centered=True),

], fluid=True, className="py-2")


@callback(
    Output("lista-usuarios", "children"),
    Output("store-perfis-iniciais", "data"),
    Input("url-admin-usuarios", "pathname"),
    Input("msg-erro-usuarios", "children"),
)
def atualizar_lista_usuarios(pathname, msg):
    if pathname != "/admin/usuarios":
        raise PreventUpdate

    usuarios = listar_usuarios()
    if not usuarios:
        return html.P("Nenhum usuário cadastrado.", className="text-muted text-center py-4"), {}

    perfis_iniciais = {u["id"]: u.get("perfil", "NORMAL") for u in usuarios}

    por_perfil = {p: [] for p in _PERFIL_ORDEM}
    for u in usuarios:
        perfil = u.get("perfil", "NORMAL")
        por_perfil.setdefault(perfil, []).append(u)

    grupos = []
    for perfil in _PERFIL_ORDEM:
        lista = sorted(por_perfil.get(perfil, []), key=lambda x: (x.get("nome") or "").lower())
        g = _grupo_perfil(perfil, lista)
        if g:
            grupos.append(g)

    return grupos, perfis_iniciais


@callback(
    Output("msg-erro-usuarios", "children", allow_duplicate=True),
    Input({"type": "select-perfil", "index": dash.ALL}, "value"),
    State("store-perfis-iniciais", "data"),
    prevent_initial_call=True,
)
def editar_perfil(valores, perfis_iniciais):
    if not ctx.triggered:
        return dash.no_update

    id_disparado = ctx.triggered_id["index"]
    novo_valor = ctx.triggered[0]["value"]

    if not novo_valor:
        return dash.no_update

    perfis_iniciais = perfis_iniciais or {}
    if perfis_iniciais.get(id_disparado) == novo_valor:
        return dash.no_update

    try:
        admin_id = _obter_user_id_logado()
        sucesso = atualizar_perfil_usuario(id_disparado, novo_valor, admin_id=admin_id)
        return dash.no_update if sucesso else "Erro ao atualizar perfil."
    except Exception as e:
        print("ERRO ao editar perfil:", e)
        return f"Erro: {e}"


@callback(
    Output("modal-confirm-delete", "is_open"),
    Output("store-user-to-delete", "data"),
    Output("msg-erro-usuarios", "children", allow_duplicate=True),
    Input({"type": "btn-deletar-usuario", "index": dash.ALL}, "n_clicks"),
    Input("btn-cancelar-delete", "n_clicks"),
    Input("btn-confirmar-delete", "n_clicks"),
    State("store-user-to-delete", "data"),
    prevent_initial_call=True,
)
def gerenciar_modal_delete(clicks_trash, click_cancel, click_confirm, user_id_atual):
    triggered = ctx.triggered_id
    triggered_value = ctx.triggered[0]["value"] if ctx.triggered else None

    if isinstance(triggered, dict) and triggered.get("type") == "btn-deletar-usuario":
        if triggered_value and triggered_value > 0:
            return True, triggered["index"], dash.no_update
        return dash.no_update, dash.no_update, dash.no_update

    if triggered == "btn-cancelar-delete":
        return False, None, dash.no_update

    if triggered == "btn-confirmar-delete":
        if user_id_atual:
            try:
                admin_id = _obter_user_id_logado()
                sucesso = deletar_usuario(user_id_atual, admin_id=admin_id)
                msg = "Usuário removido!" if sucesso else "Erro ao remover usuário."
                return False, None, msg
            except Exception as e:
                print("ERRO ao deletar:", e)
                return False, None, f"Erro: {e}"
        return False, None, dash.no_update

    return dash.no_update, dash.no_update, dash.no_update
