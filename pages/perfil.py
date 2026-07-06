import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from supabase_client import supabase
from services.usuario import buscar_usuario


dash.register_page(__name__, path="/perfil", name="Meu Perfil")


def obter_user_logado():
    session = supabase.auth.get_session()

    if session is None:
        raise Exception("Usuário não autenticado")

    return session.user


layout = dbc.Container([
    html.H2("Meu Perfil", className="mt-4 mb-4"),

    dbc.Card([
        dbc.CardHeader("Dados da Conta", className="fw-bold"),
        dbc.CardBody([
            html.Div(id="dados-perfil")
        ])
    ], className="mb-4 shadow-sm"),

    dbc.Card([
        dbc.CardHeader("Alterar Senha", className="fw-bold"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Nova senha"),
                    dbc.Input(
                        id="input-nova-senha",
                        type="password",
                        placeholder="Digite a nova senha"
                    )
                ], md=6),

                dbc.Col([
                    dbc.Label("Confirmar nova senha"),
                    dbc.Input(
                        id="input-confirmar-senha",
                        type="password",
                        placeholder="Confirme a nova senha"
                    )
                ], md=6),
            ], className="mb-3"),

            dbc.Button(
                "Alterar Senha",
                id="btn-alterar-senha",
                color="primary"
            ),

            html.Div(id="msg-alterar-senha", className="mt-3")
        ])
    ], className="shadow-sm")

], fluid=True, className="p-4")


@callback(
    Output("dados-perfil", "children"),
    Input("url", "pathname")
)

def carregar_dados_perfil(pathname):
    if pathname != "/perfil":
        return dash.no_update

    try:
        user = obter_user_logado()
        usuario = buscar_usuario(user.id)

        nome = usuario["nome"] if usuario else "Usuário"
        perfil = usuario["perfil"] if usuario else "-"
        email = user.email or "-"

        return dbc.Row([
            dbc.Col([
                html.Strong("Nome"),
                html.P(nome, className="text-muted")
            ], md=4),

            dbc.Col([
                html.Strong("E-mail"),
                html.P(email, className="text-muted")
            ], md=4),

            dbc.Col([
                html.Strong("Perfil"),
                html.P(perfil, className="text-muted")
            ], md=4),
        ])

    except Exception as e:
        return dbc.Alert(f"Erro ao carregar perfil: {e}", color="danger")


@callback(
    Output("msg-alterar-senha", "children"),
    Output("input-nova-senha", "value"),
    Output("input-confirmar-senha", "value"),
    Input("btn-alterar-senha", "n_clicks"),
    State("input-nova-senha", "value"),
    State("input-confirmar-senha", "value"),
    prevent_initial_call=True
)

def alterar_senha(n_clicks, nova_senha, confirmar_senha):
    if not nova_senha or not confirmar_senha:
        return (
            dbc.Alert("Preencha os dois campos de senha.", color="warning"),
            dash.no_update,
            dash.no_update
        )

    if nova_senha != confirmar_senha:
        return (
            dbc.Alert("As senhas não coincidem.", color="warning"),
            dash.no_update,
            dash.no_update
        )

    if len(nova_senha) < 6:
        return (
            dbc.Alert("A senha deve ter pelo menos 6 caracteres.", color="warning"),
            dash.no_update,
            dash.no_update
        )

    try:
        supabase.auth.update_user({
            "password": nova_senha
        })

        return (
            dbc.Alert("Senha alterada com sucesso.", color="success"),
            "",
            ""
        )

    except Exception as e:
        return (
            dbc.Alert(f"Erro ao alterar senha: {e}", color="danger"),
            dash.no_update,
            dash.no_update
        )