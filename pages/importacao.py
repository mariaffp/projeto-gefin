import base64
import os
import tempfile
from datetime import datetime
import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from supabase_client import supabase, get_supabase_client_com_sessao
from services.importacao import ler_csv, listar_importacoes


dash.register_page(__name__, path="/importacao", name="Importação")


def obter_user_id_logado():
    #session = supabase.auth.get_session()
    client = get_supabase_client_com_sessao()
    session = client.auth.get_session()

    if session is None:
        raise Exception("Usuário não autenticado")

    return session.user.id


layout = dbc.Container([
    dcc.Store(id="arquivo-pendente-store"),

    html.H2("Importação de Extratos", className="text-dark mt-4 mb-4 ml-4 fw-bold"),

    dbc.Card([
        dbc.CardBody([
            html.H5("Importar Novo Arquivo", className="card-title"),
            html.P(
                "Selecione ou arraste o arquivo do extrato para importar os dados.",
                className="card-text text-muted"
            ),

            dcc.Upload(
                id="upload-dados",
                children=html.Div([
                    "Arraste e solte ou ",
                    html.A("Selecione um Arquivo", className="fw-bold text-primary")
                ]),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "2px",
                    "borderStyle": "dashed",
                    "borderRadius": "8px",
                    "textAlign": "center",
                    "backgroundColor": "#f8f9fa",
                    "cursor": "pointer"
                },
                multiple=False
            ),

            html.Div(
                "Nenhum arquivo selecionado.",
                id="arquivo-selecionado",
                className="mt-2 text-muted"
            ),

            dbc.Button(
                "Importar",
                id="btn-importar",
                color="primary",
                className="mt-3",
                disabled=True
            ),

            html.Div(id="resultado-importacao", className="mt-3"),

            html.Div(
                [
                    dbc.Button(
                        "Importar mesmo assim",
                        id="btn-confirmar-duplicatas",
                        color="primary",
                        className="me-2"
                    ),
                    dbc.Button(
                        "Cancelar",
                        id="btn-cancelar-duplicatas",
                        color="danger"
                    )
                ],
                id="acoes-duplicatas",
                className="mt-2",
                style={"display": "none"}
            )
        ])
    ], className="mb-4 shadow-sm"),

    dbc.Card([
        dbc.CardHeader("Histórico de Importações", className="fw-bold"),
        dbc.ListGroup(id="lista-importacoes", flush=True)
    ], className="shadow-sm")

], fluid=True, className="p-4")


@callback(
    Output("arquivo-selecionado", "children"),
    Output("btn-importar", "disabled"),
    Input("upload-dados", "filename")
)
def atualizar_feedback_arquivo(filename):
    if not filename:
        return "Nenhum arquivo selecionado.", True

    return html.Span([
        "Arquivo selecionado: ",
        html.Strong(filename)
    ]), False


@callback(
    Output("resultado-importacao", "children"),
    Output("lista-importacoes", "children"),
    Output("arquivo-pendente-store", "data"),
    Output("acoes-duplicatas", "style"),
    Input("btn-importar", "n_clicks"),
    State("upload-dados", "contents"),
    State("upload-dados", "filename"),
    prevent_initial_call=True
)
def importar_arquivo(n_clicks, contents, filename):
    if not contents:
        return (
            dbc.Alert("Selecione um arquivo CSV primeiro.", color="warning"),
            dash.no_update,
            dash.no_update,
            {"display": "none"}
        )

    if not filename.lower().endswith(".csv"):
        return (
            dbc.Alert("O arquivo precisa ser CSV.", color="warning"),
            dash.no_update,
            dash.no_update,
            {"display": "none"}
        )

    caminho_temp = None

    try:
        user_id = obter_user_id_logado()

        _, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp:
            temp.write(decoded)
            caminho_temp = temp.name

        resultado = ler_csv(
            caminho_temp,
            user_id,
            nome_arquivo_original=filename
        )

        historico = montar_lista_importacoes(user_id)

        if resultado["status"] == "duplicatas_encontradas":
            return (
                dbc.Alert(resultado["mensagem"], color="warning"),
                historico,
                {
                    "contents": contents,
                    "filename": filename
                },
                {"display": "block"}
            )

        return (
            dbc.Alert(resultado["mensagem"], color="success"),
            historico,
            None,
            {"display": "none"}
        )

    except Exception as e:
        return (
            dbc.Alert(f"Erro ao importar arquivo: {e}", color="danger"),
            dash.no_update,
            dash.no_update,
            {"display": "none"}
        )

    finally:
        if caminho_temp and os.path.exists(caminho_temp):
            os.remove(caminho_temp)


@callback(
    Output("resultado-importacao", "children", allow_duplicate=True),
    Output("lista-importacoes", "children", allow_duplicate=True),
    Output("arquivo-pendente-store", "data", allow_duplicate=True),
    Output("acoes-duplicatas", "style", allow_duplicate=True),
    Input("btn-confirmar-duplicatas", "n_clicks"),
    State("arquivo-pendente-store", "data"),
    prevent_initial_call=True
)
def confirmar_importacao_duplicada(n_clicks, dados_arquivo):
    if not dados_arquivo:
        return (
            dbc.Alert("Nenhum arquivo pendente para importar.", color="warning"),
            dash.no_update,
            dash.no_update,
            {"display": "none"}
        )

    caminho_temp = None

    try:
        user_id = obter_user_id_logado()

        _, content_string = dados_arquivo["contents"].split(",")
        decoded = base64.b64decode(content_string)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp:
            temp.write(decoded)
            caminho_temp = temp.name

        resultado = ler_csv(
            caminho_temp,
            user_id,
            confirmar_duplicatas=True,
            nome_arquivo_original=dados_arquivo["filename"]
        )

        historico = montar_lista_importacoes(user_id)

        return (
            dbc.Alert(resultado["mensagem"], color="success"),
            historico,
            None,
            {"display": "none"}
        )

    except Exception as e:
        return (
            dbc.Alert(f"Erro ao importar arquivo: {e}", color="danger"),
            dash.no_update,
            dash.no_update,
            {"display": "none"}
        )

    finally:
        if caminho_temp and os.path.exists(caminho_temp):
            os.remove(caminho_temp)


@callback(
    Output("resultado-importacao", "children", allow_duplicate=True),
    Output("arquivo-pendente-store", "data", allow_duplicate=True),
    Output("acoes-duplicatas", "style", allow_duplicate=True),
    Input("btn-cancelar-duplicatas", "n_clicks"),
    prevent_initial_call=True
)
def cancelar_importacao_duplicada(n_clicks):
    return (
        dbc.Alert("Importação cancelada.", color="secondary"),
        None,
        {"display": "none"}
    )


@callback(
    Output("lista-importacoes", "children", allow_duplicate=True),
    Input("lista-importacoes", "id"),
    prevent_initial_call="initial_duplicate"
)
def carregar_historico(_):
    return montar_lista_importacoes(obter_user_id_logado())


def montar_lista_importacoes(user_id):
    try:
        resultado = listar_importacoes(user_id)
        importacoes = resultado.data

        if not importacoes:
            return [
                dbc.ListGroupItem("Nenhuma importação encontrada.")
            ]

        itens = []

        for imp in importacoes:
            data_formatada = (
                datetime.fromisoformat(imp["data_importacao"])
                .strftime("%d/%m/%Y - %H:%M")
            )

            itens.append(
                dbc.ListGroupItem([
                    html.Div([
                        html.H6(
                            imp["nome_arquivo"],
                            className="mb-1"
                        ),
                        html.Small(
                            data_formatada,
                            className="text-muted"
                        ),
                    ],
                    className="d-flex w-100 justify-content-between"),

                    html.Small(
                        f"Origem: {imp.get('origem', '-')}",
                        className="text-success fw-bold"
                    )
                ])
            )

        return itens

    except Exception as e:
        return [
            dbc.ListGroupItem(
                f"Erro ao carregar histórico: {e}"
            )
        ]