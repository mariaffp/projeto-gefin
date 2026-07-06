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

        supabase.table("usuario") \
            .update({"nome": nome}) \
            .eq("id", resposta.user.id) \
            .execute()

        if perfil != 'NORMAL':
            supabase.table("usuario") \
                .update({"perfil": perfil}) \
                .eq("id", resposta.user.id) \
                .execute()

        # Usa o próprio id do usuário criado como referência no log
        registrar_log(
            resposta.user.id,
            "USUARIO_CRIADO",
            f"Usuário '{nome}' ({email}) criado com perfil {perfil}"
        )

        return True
    except Exception as e:
        print("ERRO ao cadastrar usuário:", e)
        return False


def listar_usuarios():
    registro = executar_com_retry( lambda: supabase_admin.table("usuario").select("id, nome, perfil").order("nome").execute())
    return registro.data if registro.data else []


def atualizar_perfil_usuario(user_id, novo_perfil, admin_id=None):
    try:
        usuario = buscar_usuario(user_id)
        nome = usuario["nome"] if usuario else user_id

        supabase_admin.table("usuario").update({"perfil": novo_perfil}).eq("id", user_id).execute()

        # Se soubermos quem fez a alteração, registra no log
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
        # Busca o nome antes de deletar
        usuario = buscar_usuario(user_id)
        nome = usuario["nome"] if usuario else user_id

        # Registra o log ANTES de deletar
        registrar_log(user_id, "USUARIO_DELETADO", f"Usuário '{nome}' deletado")

        
        supabase_admin.auth.admin.delete_user(user_id)
        return True
    except Exception as e:
        print("ERRO ao deletar usuário:", e)
        return False