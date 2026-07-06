from supabase_client import supabase, supabase_admin
from services.log import registrar_log
from services.utils import executar_com_retry

def buscar_usuario(user_id):
    try:
        registro = executar_com_retry(
            lambda: supabase.table("usuario")
                .select("nome, perfil")
                .eq("id", user_id)
                .single()
                .execute()
        )
        return registro.data if registro.data else None
    except Exception as e:
        print(f"ERRO no buscar_usuario: {e}")
        return None

def buscar_perfil(user_id):
    try:
        registro = executar_com_retry(
            lambda: supabase.table("usuario")
                .select("perfil")
                .eq("id", user_id)
                .single()
                .execute()
        )
        return registro.data['perfil'] if registro.data else None
    except Exception as e:
        print(f"ERRO no buscar_perfil: {e}")
        return None

def eh_admin(perfil):
    return perfil == 'ADMIN'


def eh_financeiro(perfil):
    return perfil in ['FINANCEIRO', 'ADMIN']


def cadastrar_usuario(email, senha, nome, perfil):
    try:
        resposta = supabase_admin.auth.admin.create_user({
            "email": email,
            "password": senha,
            "user_metadata": {"full_name": nome},
            "email_confirm": True
        })

        novo_id = resposta.user.id
        supabase_admin.table("usuario") \
            .update({"nome": nome, "perfil": perfil}) \
            .eq("id", novo_id) \
            .execute()

        registrar_log(
            novo_id,
            "USUARIO_CRIADO",
            f"Usuário '{nome}' ({email}) criado com perfil {perfil}"
        )

        return True
    except Exception as e:
        print("ERRO ao cadastrar usuário:", e)
        return False


def listar_usuarios():
    registro = supabase_admin.table("usuario").select("id, nome, perfil").order("nome").execute()
    return registro.data if registro.data else []


def atualizar_perfil_usuario(user_id, novo_perfil, admin_id=None):
    try:
        usuario = buscar_usuario(user_id)
        nome = usuario["nome"] if usuario else user_id

        supabase_admin.table("usuario").update({"perfil": novo_perfil}).eq("id", user_id).execute()

        id_para_log = admin_id if admin_id else user_id
        registrar_log(
            id_para_log,
            "USUARIO_PERFIL_ALTERADO",
            f"Perfil de '{nome}' alterado para {novo_perfil}"
        )

        return True
    except Exception as e:
        print("ERRO ao atualizar perfil:", e)
        return False


def deletar_usuario(user_id):
    try:
        usuario = buscar_usuario(user_id)
        nome = usuario["nome"] if usuario else user_id

        registrar_log(user_id, "USUARIO_DELETADO", f"Usuário '{nome}' deletado")

        # Ordem: logs -> tabela usuario -> auth.users (FKs em cascata reversa)
        supabase_admin.table("log_sistema").delete().eq("id_usuario", user_id).execute()
        supabase_admin.table("usuario").delete().eq("id", user_id).execute()
        supabase_admin.auth.admin.delete_user(user_id)
        return True
    except Exception as e:
        print("ERRO ao deletar usuário:", e)
        return False