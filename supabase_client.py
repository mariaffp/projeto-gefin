from supabase import create_client
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase.lib.client_options import ClientOptions
from flask import g, session as flask_session
from werkzeug.local import LocalProxy

load_dotenv(Path(__file__).resolve().parent / ".env")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
admin_key = os.getenv("SUPABASE_SERVICE_KEY")

#supabase = create_client(url, key)
supabase_admin = create_client(url, admin_key)


class FlaskSessionStorage:
    def get_item(self, key):
        return flask_session.get(key)
    def set_item(self, key, value):
        flask_session[key] = value
    def remove_item(self, key):
        if key in flask_session:
            del flask_session[key]
def criar_client_oauth():
    options = ClientOptions(storage=FlaskSessionStorage())
    return create_client(url, key, options=options)


def get_supabase_client_com_sessao():
    """Cria um client Supabase novo, carregado com a sessão da pessoa que está fazendo a requisição atual."""
    client = create_client(url, key)
    access_token = flask_session.get("access_token")
    refresh_token = flask_session.get("refresh_token")
    if access_token and refresh_token:
        try:
            resultado = client.auth.set_session(access_token, refresh_token)
            #client.auth.set_session(access_token, refresh_token)
            if resultado and resultado.session:
                flask_session["access_token"] = resultado.session.access_token
                flask_session["refresh_token"] = resultado.session.refresh_token
        except Exception as e:
            print("ERRO ao restaurar sessão:", e)
            flask_session.clear() #token corrompido/expirado
    return client

def _client_da_requisicao_atual():
    if "supabase_sessao" not in g:
        g.supabase_sessao = get_supabase_client_com_sessao()
    return g.supabase_sessao

supabase = LocalProxy(_client_da_requisicao_atual)
