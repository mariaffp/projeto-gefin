from supabase_client import supabase, supabase_admin
from services.log import registrar_log
from services.utils import executar_com_retry

def buscar_usuario(user_id):
    try:
        registro = executar_com_retry(
            lambda: supabase.table("usuario")
                .select("nome, perfil, aprovado")
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


def cadastrar_usuario(email, senha, nome, perfil, admin_id=None):
    try:
        #resposta = supabase_admin.auth.admin.create_user({
        dados_usuario = {
            "email": email,
            #"password": senha,
            "user_metadata": {"full_name": nome},
            "email_confirm": True
        }
        if senha:
            dados_usuario["password"] = senha
        
        resposta = supabase_admin.auth.admin.create_user(dados_usuario)
        novo_id = resposta.user.id
        supabase_admin.table("usuario") \
            .update({"nome": nome, "perfil": perfil, "aprovado":True}) \
            .eq("id", novo_id) \
            .execute()

        id_para_log = admin_id if admin_id else resposta.user.id

        tipo = "Google" if not senha else "senha"
        registrar_log(
            id_para_log,
            "USUARIO_CRIADO",
            f"Usuário '{nome}' ({email}) criado via tipo {tipo} com perfil {perfil}"
        )

        return True

    except Exception as e:
        print("ERRO ao cadastrar usuário:", e)
        return False


def listar_usuarios():
    registro = executar_com_retry(lambda: supabase_admin.table("usuario").select("id, nome, perfil").order("nome").execute())
    return registro.data if registro.data else []


def atualizar_perfil_usuario(user_id, novo_perfil, admin_id=None):
    try:
        usuario = (
            supabase_admin.table("usuario")
            .select("nome")
            .eq("id", user_id)
            .single()
            .execute()
        )

        nome = usuario.data["nome"] if usuario.data else user_id

        supabase_admin.table("usuario") \
            .update({"perfil": novo_perfil}) \
            .eq("id", user_id) \
            .execute()

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

def deletar_usuario(user_id, admin_id=None):
    try:
        usuario = (
            supabase_admin.table("usuario")
            .select("nome")
            .eq("id", user_id)
            .single()
            .execute()
        )

        nome = usuario.data["nome"] if usuario.data else user_id

        id_para_log = admin_id if admin_id else user_id

        registrar_log(
            id_para_log,
            "USUARIO_DELETADO",
            f"Usuário '{nome}' deletado"
        )

        # Ordem: logs -> tabela usuario -> auth.users (FKs em cascata reversa)
        supabase_admin.table("log_sistema").delete().eq("id_usuario", user_id).execute()
        supabase_admin.table("usuario").delete().eq("id", user_id).execute()
        #supabase_admin.auth.admin.delete_user(user_id)
        #print(f"Removendo usuário do Authentication: {user_id}")
        resultado = supabase_admin.auth.admin.delete_user(user_id)
        #print("Resultado da exclusão:", resultado)
        return True

    except Exception as e:
        print("ERRO ao deletar usuário:", e)
        return False