from services.usuario import buscar_perfil, eh_financeiro
from services.log import registrar_log
from supabase_client import supabase
from services.utils import executar_com_retry


def criar_conta(nome, user_id):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuario sem permissão para criar conta")

    conta_existe = supabase.table("conta").select("*").eq("nome", nome).execute()

    if not conta_existe.data:
        resultado = supabase.table("conta").insert({"nome": nome, "id_usuario": user_id}).execute()
        registrar_log(user_id, "CONTA_CRIADA", f"Conta '{nome}' criada")
        return resultado
    else:
        raise Exception("Conta já existe")


def editar_conta(user_id, novo_nome, id_conta):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuario sem permissão para editar conta")

    conta_existe = supabase.table("conta").select("*").eq("id_conta", id_conta).execute()

    if conta_existe.data:
        nome_antigo = conta_existe.data[0]["nome"]
        resultado = supabase.table("conta").update({"nome": novo_nome}).eq("id_conta", id_conta).execute()
        registrar_log(user_id, "CONTA_EDITADA", f"Conta '{nome_antigo}' renomeada para '{novo_nome}'")
        return resultado
    else:
        raise Exception("Conta não existe")


def deletar_conta(user_id, id_conta):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuario sem permissão para apagar conta")

    conta_existe = supabase.table("conta").select("*").eq("id_conta", id_conta).execute()

    if conta_existe.data:
        nome = conta_existe.data[0]["nome"]
        resultado = supabase.table("conta").delete().eq("id_conta", id_conta).execute()
        registrar_log(user_id, "CONTA_DELETADA", f"Conta '{nome}' deletada")
        return resultado
    else:
        raise Exception("Conta não existe")


def listar_contas():
    return executar_com_retry(lambda: supabase.table("conta").select("*").execute())

    