import dash
from dash import html, Input, Output, State, callback, dcc, ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

from services.usuario import (
    listar_usuarios,
    atualizar_perfil_usuario,
    deletar_usuario,
    buscar_perfil
)
from supabase_client import supabase


dash.register_page(__name__, path="/admin/usuarios")

COR_BOTAO = "#0067EC"


def obter_user_id_logado():
    session = supabase.auth.get_session()

    if session is None:
        raise Exception("Usuário não autenticado")

    return session.user.id


layout = html.Div(
    [
        dcc.Location(id="url-admin-usuarios", refresh=False),

        html.Div(
            style={
                "position": "fixed",
                "top": 0,
                "left": 0,
                "width": "100vw",
                "height": "100vh",
                "background": "linear-gradient(to bottom right, rgba(109, 237, 255, 0.6), rgba(171, 195, 255, 0.6)), url('/assets/focusbackground.png')",
                "backgroundSize": "cover",
                "backgroundPosition": "center",
                "filter": "blur(5px)",
                "transform": "scale(1.1)",
                "zIndex": -1,
            }
        ),

        html.Div(
            [
                html.H2(
                    "Gerenciar Usuários",
                    className="text-center mb-3",
                    style={"color": COR_BOTAO, "fontWeight": "bold"}
                ),

                html.Div(
                    id="msg-erro-usuarios",
                    className="text-danger text-center mb-2"
                ),

                html.Div(id="lista-usuarios")
            ],
            className="glass-box p-4",
            style={
                "backgroundColor": "rgba(228, 228, 228, 0.5)",
                "borderRadius": "12px",
                "boxShadow": "0px 15px 35px rgba(0, 0, 0, 0.5)",
                "width": "100%",
                "maxWidth": "520px",
                "maxHeight": "75vh",
                "overflowY": "auto",
                "margin": "0 auto",
                "position": "relative",
                "zIndex": 2
            }
        )
    ],
    style={
        "minHeight": "calc(100vh - 90px)",
        "display": "flex",
        "alignItems": "center",
        "justifyContent": "center"
    }
)


@callback(
    Output("lista-usuarios", "children"),
    Input("url-admin-usuarios", "pathname")
)
def atualizar_lista_usuarios(pathname):
    if pathname != "/admin/usuarios":
        raise PreventUpdate

    usuarios = listar_usuarios()
    linhas = []

    for u in usuarios:
        linhas.append(
            html.Div(
                [
                    html.Span(
                        u["nome"],
                        style={
                            "fontWeight": "600",
                            "flex": "1"
                        }
                    ),

                    dbc.Select(
                        id={
                            "type": "select-perfil",
                            "index": u["id"]
                        },
                        options=[
                            {"label": "Normal", "value": "NORMAL"},
                            {"label": "Financeiro", "value": "FINANCEIRO"},
                            {"label": "Admin", "value": "ADMIN"},
                        ],
                        value=u["perfil"],
                        style={
                            "width": "130px",
                            "marginRight": "6px"
                        }
                    ),

                    dbc.Button(
                        html.I(className="bi bi-check-lg"),
                        id={
                            "type": "btn-salvar-perfil",
                            "index": u["id"]
                        },
                        color="success",
                        size="sm"
                    ),

                    dbc.Button(
                        html.I(className="bi bi-trash"),
                        id={
                            "type": "btn-deletar-usuario",
                            "index": u["id"]
                        },
                        color="danger",
                        size="sm"
                    )
                ],
                className="d-flex align-items-center mb-2",
                style={"gap": "6px"}
            )
        )

    return linhas


@callback(
    Output("msg-erro-usuarios", "children", allow_duplicate=True),
    Input({"type": "btn-salvar-perfil", "index": dash.ALL}, "n_clicks"),
    State({"type": "select-perfil", "index": dash.ALL}, "value"),
    State({"type": "select-perfil", "index": dash.ALL}, "id"),
    prevent_initial_call=True
)
def editar_perfil(n_clicks_lista, valores, ids_select):
    if not ctx.triggered_id or not any(n_clicks_lista or []):
        raise PreventUpdate

    id_disparado = ctx.triggered_id["index"]

    indice = next(
        (
            i for i, item in enumerate(ids_select or [])
            if item["index"] == id_disparado
        ),
        None
    )

    if indice is None:
        raise PreventUpdate

    novo_valor = valores[indice]
    perfil_atual = buscar_perfil(id_disparado)

    if novo_valor == perfil_atual:
        raise PreventUpdate

    admin_id = obter_user_id_logado()

    sucesso = atualizar_perfil_usuario(
        id_disparado,
        novo_valor,
        admin_id=admin_id
    )

    return "Perfil atualizado!" if sucesso else "Erro ao atualizar perfil."


@callback(
    Output("msg-erro-usuarios", "children", allow_duplicate=True),
    Input({"type": "btn-deletar-usuario", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True
)
def deletar_usuario_callback(n_clicks_lista):
    if not ctx.triggered_id or not any(n_clicks_lista or []):
        raise PreventUpdate

    id_disparado = ctx.triggered_id["index"]
    admin_id = obter_user_id_logado()

    sucesso = deletar_usuario(
        id_disparado,
        admin_id=admin_id
    )

    return "Usuário removido!" if sucesso else "Erro ao remover usuário."