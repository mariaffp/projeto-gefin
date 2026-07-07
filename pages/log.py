import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from datetime import datetime
from zoneinfo import ZoneInfo
from supabase_client import supabase
from services.log import listar_logs


dash.register_page(__name__, path="/logs", name="Logs")


def obter_user_id_logado():
    session = supabase.auth.get_session()

    if session is None:
        raise Exception("Usuário não autenticado")

    return session.user.id


def formatar_data(data_iso):
    if not data_iso:
        return "-"

    try:
        data = datetime.fromisoformat(data_iso.replace("Z", "+00:00"))

        if data.tzinfo is None:
            data = data.replace(tzinfo=ZoneInfo("UTC"))

        data = data.astimezone(ZoneInfo("America/Sao_Paulo"))

        return data.strftime("%d/%m/%Y - %H:%M")

    except Exception:
        return data_iso

def formatar_acao(acao):
    if not acao:
        return "-"

    mapa = {
        "CATEGORIA_CRIADA": "Categoria Criada",
        "CATEGORIA_EDITADA": "Categoria Editada",
        "CATEGORIA_DELETADA": "Categoria Desativada",
        "CATEGORIA_REATIVADA": "Categoria Reativada",
        "TRANSACAO_CRIADA": "Transação Criada",
        "TRANSACAO_EDITADA": "Transação Editada",
        "TRANSACAO_DELETADA": "Transação Deletada",
        "IMPORTACAO_EXTRATO": "Importação de Extrato",
        "CONTA_CRIADA": "Conta Criada",
        "CONTA_EDITADA": "Conta Editada",
        "CONTA_DELETADA": "Conta Desativada",
        "CONTA_REATIVADA": "Conta Reativada",    
        "FORMA_PAGAMENTO_CRIADA": "Forma de Pagamento Criada",
        "FORMA_PAGAMENTO_EDITADA": "Forma de Pagamento Editada",
        "FORMA_PAGAMENTO_DELETADA": "Forma de Pagamento Deletada",
        "USUARIO_CRIADO": "Usuário Criado",
        "USUARIO_PERFIL_ALTERADO": "Perfil Alterado",
        "USUARIO_DELETADO": "Usuário Deletado",
    }

    return mapa.get(acao, acao.replace("_", " ").title())


def cor_acao(acao):
    if not acao:
        return "secondary"

    if "CRIADA" in acao or "CRIADO" in acao or "REATIVADA" in acao:
        return "success"

    if "EDITADA" in acao or "EDITADO" in acao or "ALTERADO" in acao:
        return "warning"

    if "DELETADA" in acao or "DELETADO" in acao:
        return "danger"

    if "IMPORTACAO" in acao:
        return "primary"

    return "secondary"


layout = dbc.Container([
    html.H2("Logs do Sistema", className="mt-4 mb-4"),

    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Buscar na descrição"),
                    dbc.Input(
                        id="filtro-log-descricao",
                        type="text",
                        placeholder="Ex: categoria, transação, importação..."
                    )
                ], md=4),

                dbc.Col([
                    dbc.Label("Ação"),
                    dbc.Select(
                        id="filtro-log-acao",
                        options=[
                            {"label": "Todas", "value": "todas"},
                            {"label": "Categoria criada", "value": "CATEGORIA_CRIADA"},
                            {"label": "Categoria editada", "value": "CATEGORIA_EDITADA"},
                            {"label": "Categoria desativada", "value": "CATEGORIA_DELETADA"},
                            {"label": "Categoria reativada", "value": "CATEGORIA_REATIVADA"},
                            {"label": "Transação criada", "value": "TRANSACAO_CRIADA"},
                            {"label": "Transação editada", "value": "TRANSACAO_EDITADA"},
                            {"label": "Transação deletada", "value": "TRANSACAO_DELETADA"},
                            {"label": "Importação de extrato", "value": "IMPORTACAO_EXTRATO"},
                            {"label": "Conta criada", "value": "CONTA_CRIADA"},
                            {"label": "Conta editada", "value": "CONTA_EDITADA"},
                            {"label": "Conta deletada", "value": "CONTA_DELETADA"},
                            {"label": "Forma de pagamento criada", "value": "FORMA_PAGAMENTO_CRIADA"},
                            {"label": "Forma de pagamento editada", "value": "FORMA_PAGAMENTO_EDITADA"},
                            {"label": "Forma de pagamento deletada", "value": "FORMA_PAGAMENTO_DELETADA"},
                            {"label": "Usuário criado", "value": "USUARIO_CRIADO"},
                            {"label": "Perfil alterado", "value": "USUARIO_PERFIL_ALTERADO"},
                            {"label": "Usuário deletado", "value": "USUARIO_DELETADO"},
                        ],
                        value="todas"
                    )
                ], md=4),

                dbc.Col([
                    dbc.Label("Data inicial"),
                    dbc.Input(id="filtro-log-data-inicial", type="date")
                ], md=2),

                dbc.Col([
                    dbc.Label("Data final"),
                    dbc.Input(id="filtro-log-data-final", type="date")
                ], md=2),
            ], className="g-3")
        ])
    ], className="mb-4 shadow-sm"),

    dbc.Card([
        dbc.CardHeader("Histórico de Ações", className="fw-bold"),
        dbc.Table([
            html.Thead(html.Tr([
                html.Th("Data/Hora"),
                html.Th("Usuário"),
                html.Th("Ação"),
                html.Th("Descrição"),
            ])),
            html.Tbody(id="tbody-logs")
        ], striped=True, hover=True, responsive=True, className="mb-0")
    ], className="shadow-sm")

], fluid=True, className="p-4")


@callback(
    Output("tbody-logs", "children"),
    Input("filtro-log-descricao", "value"),
    Input("filtro-log-acao", "value"),
    Input("filtro-log-data-inicial", "value"),
    Input("filtro-log-data-final", "value")
)
def carregar_logs(filtro_descricao, filtro_acao, data_inicial, data_final):
    try:
        user_id = obter_user_id_logado()
        logs = listar_logs(user_id)

        if filtro_descricao:
            logs = [
                log for log in logs
                if filtro_descricao.lower() in (log.get("descricao") or "").lower()
            ]

        if filtro_acao and filtro_acao != "todas":
            logs = [
                log for log in logs
                if log.get("acao") == filtro_acao
            ]

        if data_inicial:
            logs = [
                log for log in logs
                if (log.get("created_at") or "")[:10] >= data_inicial
            ]

        if data_final:
            logs = [
                log for log in logs
                if (log.get("created_at") or "")[:10] <= data_final
            ]

        if not logs:
            return [
                html.Tr([
                    html.Td(
                        "Nenhum log encontrado.",
                        colSpan=4,
                        className="text-center text-muted"
                    )
                ])
            ]

        linhas = []

        for log in logs:
            usuario = log.get("usuario") or {}
            acao = log.get("acao")

            linhas.append(
                html.Tr([
                    html.Td(formatar_data(log.get("created_at"))),
                    html.Td(usuario.get("nome", "Usuário não encontrado")),
                    html.Td(
                        dbc.Badge(
                            formatar_acao(acao),
                            color=cor_acao(acao),
                            pill=True
                        )
                    ),
                    html.Td(log.get("descricao") or "-"),
                ])
            )

        return linhas

    except Exception as e:
        return [
            html.Tr([
                html.Td(
                    f"Erro ao carregar logs: {e}",
                    colSpan=4,
                    className="text-danger"
                )
            ])
        ]