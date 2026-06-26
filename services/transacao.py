from supabase_client import supabase 
from services.usuario import buscar_perfil, eh_financeiro


def criar_transacao(dados, user_id):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuário sem permissão para criar transação")

    dados["id_usuario"] = user_id

    return (
        supabase.table("transacao")
        .insert(dados)
        .execute()
    )


def listar_transacoes(user_id):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuário sem permissão para listar transações")

    return (
        supabase.table("transacao")
        .select("*")
        .eq("id_usuario", user_id)
        .order("data", desc=True)
        .execute()
    )


def buscar_transacao(id_transacao, user_id):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuário sem permissão para buscar transação")

    transacao = (
        supabase.table("transacao")
        .select("*")
        .eq("id_transacao", id_transacao)
        .eq("id_usuario", user_id)
        .execute()
    )

    if not transacao.data:
        raise Exception("Transação não encontrada")

    return transacao.data[0]


def editar_transacao(id_transacao, dados, user_id):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuário sem permissão para editar transação")

    buscar_transacao(id_transacao, user_id)

    return (
        supabase.table("transacao")
        .update(dados)
        .eq("id_transacao", id_transacao)
        .eq("id_usuario", user_id)
        .execute()
    )


def excluir_transacao(id_transacao, user_id):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuário sem permissão para excluir transação")

    buscar_transacao(id_transacao, user_id)

    return (
        supabase.table("transacao")
        .delete()
        .eq("id_transacao", id_transacao)
        .eq("id_usuario", user_id)
        .execute()
    )


def salvar_transacoes_importadas(transacoes, id_importacao, user_id):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuário sem permissão para salvar transações importadas")

    for transacao in transacoes:
        transacao["id_usuario"] = user_id
        transacao["id_importacao"] = id_importacao

    return (
        supabase.table("transacao")
        .insert(transacoes)
        .execute()
    )


def listar_transacoes_por_importacao(id_importacao, user_id):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuário sem permissão para listar transações da importação")

    return (
        supabase.table("transacao")
        .select("*")
        .eq("id_importacao", id_importacao)
        .eq("id_usuario", user_id)
        .order("data", desc=True)
        .execute()
    )


def verificar_duplicatas(transacoes, user_id):
    duplicatas = []

    for transacao in transacoes:
        consulta = (
            supabase.table("transacao")
            .select("*")
            .eq("id_usuario", user_id)
            .eq("data", transacao["data"])
            .eq("valor", transacao["valor"])
            .eq("descricao", transacao["descricao"])
            .eq("id_conta", transacao["id_conta"])
            .execute()
        )

        if consulta.data:
            duplicatas.append(transacao)

    return duplicatas