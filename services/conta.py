from services.usuario import buscar_perfil, eh_financeiro
from services.log import registrar_log
from supabase_client import supabase
from services.utils import executar_com_retry
from datetime import datetime, timezone


def normalizar_nome(nome):
    nome = " ".join(nome.strip().split())
    nome = nome.title()
    return nome


def validar_financeiro(user_id):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuário sem permissão")


def criar_conta(nome, user_id):
    nome = normalizar_nome(nome)
    validar_financeiro(user_id)

    conta_existe = executar_com_retry(
        lambda: supabase.table("conta")
        .select("*")
        .eq("nome", nome)
        .execute()
    )

    if not conta_existe.data:
        resultado = executar_com_retry(
            lambda: supabase.table("conta")
            .insert({"nome": nome, "id_usuario": user_id})
            .execute()
        )

        registrar_log(user_id, "CONTA_CRIADA", f"Conta '{nome}' criada")
        return resultado

    conta = conta_existe.data[0]

    if conta["deletado"] is None:
        raise Exception("Conta já existe")

    resultado = executar_com_retry(
        lambda: supabase.table("conta")
        .update({"deletado": None})
        .eq("id_conta", conta["id_conta"])
        .execute()
    )

    registrar_log(user_id, "CONTA_REATIVADA", f"Conta '{nome}' reativada via criação")
    return resultado


def editar_conta(user_id, novo_nome, id_conta):
    novo_nome = normalizar_nome(novo_nome)
    validar_financeiro(user_id)

    conta_atual = executar_com_retry(
        lambda: supabase.table("conta")
        .select("*")
        .eq("id_conta", id_conta)
        .execute()
    )

    if not conta_atual.data:
        raise Exception("Conta não encontrada")

    conta = conta_atual.data[0]
    nome_antigo = conta["nome"]

    if conta["deletado"] is not None:
        raise Exception("Não é possível editar uma conta desativada")

    conta_com_mesmo_nome = executar_com_retry(
        lambda: supabase.table("conta")
        .select("*")
        .eq("nome", novo_nome)
        .execute()
    )

    if conta_com_mesmo_nome.data:
        conta_existente = conta_com_mesmo_nome.data[0]

        if conta_existente["id_conta"] != id_conta:
            if conta_existente["deletado"] is None:
                raise Exception("Já existe uma conta ativa com esse nome")

            raise Exception(
                "Essa conta já existe, mas está desativada. "
                "Reative-a na lista de contas desativadas."
            )

    resultado = executar_com_retry(
        lambda: supabase.table("conta")
        .update({"nome": novo_nome})
        .eq("id_conta", id_conta)
        .execute()
    )

    registrar_log(
        user_id,
        "CONTA_EDITADA",
        f"Conta '{nome_antigo}' renomeada para '{novo_nome}'"
    )

    return resultado


def listar_contas():
    return executar_com_retry(
        lambda: supabase.table("conta")
        .select("*")
        .is_("deletado", None)
        .order("nome")
        .execute()
    )


def listar_contas_desativadas(user_id):
    validar_financeiro(user_id)

    return executar_com_retry(
        lambda: supabase.table("conta")
        .select("*")
        .not_.is_("deletado", None)
        .order("nome")
        .execute()
    )


def listar_todas_contas(user_id):
    validar_financeiro(user_id)

    return executar_com_retry(
        lambda: supabase.table("conta")
        .select("*")
        .order("nome")
        .execute()
    )


def deletar_conta(user_id, id_conta):
    validar_financeiro(user_id)

    conta_atual = executar_com_retry(
        lambda: supabase.table("conta")
        .select("*")
        .eq("id_conta", id_conta)
        .execute()
    )

    if not conta_atual.data:
        raise Exception("Conta não encontrada")

    conta = conta_atual.data[0]
    nome = conta["nome"]

    if conta["deletado"] is not None:
        raise Exception("Conta já está desativada")

    resultado = executar_com_retry(
        lambda: supabase.table("conta")
        .update({"deletado": datetime.now(timezone.utc).isoformat()})
        .eq("id_conta", id_conta)
        .execute()
    )

    registrar_log(user_id, "CONTA_DELETADA", f"Conta '{nome}' desativada")
    return resultado


def reativar_conta(id_conta, user_id):
    validar_financeiro(user_id)

    conta_atual = executar_com_retry(
        lambda: supabase.table("conta")
        .select("*")
        .eq("id_conta", id_conta)
        .execute()
    )

    if not conta_atual.data:
        raise Exception("Conta não encontrada")

    conta = conta_atual.data[0]
    nome = conta["nome"]

    if conta["deletado"] is None:
        raise Exception("Conta já está ativa")

    conta_ativa_mesmo_nome = executar_com_retry(
        lambda: supabase.table("conta")
        .select("*")
        .eq("nome", nome)
        .is_("deletado", None)
        .execute()
    )

    if conta_ativa_mesmo_nome.data:
        raise Exception("Já existe uma conta ativa com esse nome")

    resultado = executar_com_retry(
        lambda: supabase.table("conta")
        .update({"deletado": None})
        .eq("id_conta", id_conta)
        .execute()
    )

    registrar_log(user_id, "CONTA_REATIVADA", f"Conta '{nome}' reativada")
    return resultado