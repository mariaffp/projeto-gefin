from supabase_client import supabase 
from services.usuario import buscar_perfil, eh_financeiro
from services.log import registrar_log
from services.utils import executar_com_retry


def verificar_duplicatas(transacoes, user_id):
    duplicatas = []

    for transacao in transacoes:
        consulta = (
            supabase.table("transacao")
            .select("*")
            #.eq("id_usuario", user_id)
            .eq("data", transacao["data"])
            .eq("valor", transacao["valor"])
            .eq("descricao", transacao["descricao"])
            .eq("id_conta", transacao["id_conta"])
            .execute()
        )

        if consulta.data:
            duplicatas.append(transacao)

    return duplicatas

def criar_transacao(dados, user_id, confirmar_duplicata=False):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuário sem permissão para criar transação")

    duplicatas = verificar_duplicatas([dados], user_id)

    if duplicatas and not confirmar_duplicata:
        return {
            "status": "duplicatas_encontradas",
            "mensagem": "Já existe uma transação semelhante. Deseja criar mesmo assim?",
            "duplicatas": duplicatas
        }

    dados["id_usuario"] = user_id

    resposta = (
        supabase.table("transacao")
        .insert(dados)
        .execute()
    )

    registrar_log(user_id, "TRANSACAO_CRIADA", f"Transação '{dados.get('descricao', '')}' criada")

    return {
        "status": "sucesso",
        "mensagem": "Transação criada com sucesso.",
        "data": resposta.data
    }

def listar_transacoes(user_id):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuário sem permissão para listar transações")

    return executar_com_retry( lambda:
        supabase.table("transacao")
        .select("*")
        #.eq("id_usuario", user_id)
        .order("data", desc=True)
        .execute()
    )


def buscar_transacao(id_transacao, user_id):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuário sem permissão para buscar transação")

    transacao = executar_com_retry (lambda:
        supabase.table("transacao")
        .select("*")
        .eq("id_transacao", id_transacao)
        #.eq("id_usuario", user_id)
        .execute()
    )

    if not transacao.data:
        raise Exception("Transação não encontrada")

    return transacao.data[0]


def editar_transacao(id_transacao, dados, user_id):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuário sem permissão para editar transação")

    transacao_antiga = buscar_transacao(id_transacao, user_id)
    descricao_antiga = transacao_antiga.get("descricao", "")
    descricao_nova = dados.get("descricao", descricao_antiga)

    resultado = (
        supabase.table("transacao")
        .update(dados)
        .eq("id_transacao", id_transacao)
        #.eq("id_usuario", user_id)
        .execute()
    )

    registrar_log(
        user_id,
        "TRANSACAO_EDITADA",
        f"Transação '{descricao_antiga}' editada"
    )

    return resultado


def excluir_transacao(id_transacao, user_id):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuário sem permissão para excluir transação")

    transacao = buscar_transacao(id_transacao, user_id)
    descricao = transacao.get("descricao", "")

    resultado = (
        supabase.table("transacao")
        .delete()
        .eq("id_transacao", id_transacao)
        #.eq("id_usuario", user_id)
        .execute()
    )

    registrar_log(
        user_id,
        "TRANSACAO_DELETADA",
        f"Transação '{descricao}' deletada"
    )

    return resultado

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

    return executar_com_retry( lambda:
        supabase.table("transacao")
        .select("*")
        .eq("id_importacao", id_importacao)
        #.eq("id_usuario", user_id)
        .order("data", desc=True)
        .execute()
    )


def listar_transacoes_relatorio(id_categoria=None, tipo=None, periodo=None, id_conta=None, data_inicio=None, data_fim=None):
    
    #Busca transações aplicando filtros opcionais, qualquer filtro que não for informado (None) é ignorado.
    query = supabase.table("transacao").select("*, categoria(nome), conta(nome), forma_pagamento(nome)")

    if id_categoria:
        query = query.eq("id_categoria", id_categoria)

    if tipo:
        query = query.eq("tipo", tipo)

    if id_conta:
        query = query.eq("id_conta", id_conta)

    if data_inicio:
        query = query.gte("data", data_inicio)

    if data_fim:
        query = query.lte("data", data_fim)

    resposta = executar_com_retry( lambda: query.order("data", desc=True).execute())
    return resposta.data

