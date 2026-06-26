from supabase_client import supabase


def listar_transacoes(id_categoria=None, tipo=None, periodo=None, id_conta=None,
                       data_inicio=None, data_fim=None):
    """
    Busca transações aplicando filtros opcionais.
    Qualquer filtro que não for informado (None) é ignorado.
    """
    query = supabase.table("transacao").select(
        "*, categoria(nome), conta(nome), forma_pagamento(nome)"
    )

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

    resposta = query.order("data", desc=True).execute()
    return resposta.data