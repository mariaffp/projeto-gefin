from services.usuario import buscar_perfil,eh_financeiro
from supabase_client import supabase


def criar_conta(nome, user_id):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuario sem permissão para criar conta")

    conta_existe = (supabase.table("conta").select("*").eq("nome", nome).execute())

    if not conta_existe.data:
        return (supabase.table("conta").insert({"nome": nome, "id_usuario": user_id}).execute())
    else:
        raise Exception("Conta já existe")


def editar_conta(user_id, novo_nome, id_conta):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuario sem permissão para editar conta")

    conta_existe = (supabase.table("conta").select("*").eq("id_conta", id_conta).execute())

    if conta_existe.data:
        return (supabase.table("conta").update({"nome": novo_nome}).eq("id_conta", id_conta).execute())
    else:
        raise Exception("Conta não existe")

def deletar_conta(user_id, id_conta):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuario sem permissão para apagar conta")

    conta_existe = (supabase.table("conta").select("*").eq("id_conta", id_conta).execute())

    if conta_existe.data:
        return (supabase.table("conta").delete().eq("id_conta", id_conta).execute())
    else:
        raise Exception("Conta não existe")


def listar_contas():
    return (supabase.table("conta").select("*").execute())

