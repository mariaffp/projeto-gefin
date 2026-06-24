from services.usuario import buscar_perfil,eh_financeiro
from supabase_client import supabase


def criar_forma_pagamento(nome, user_id):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuario sem permissão para criar forma de pagamento")

    forma_de_pagamento_existe = (supabase.table("forma_pagamento").select("*").eq("nome", nome).execute())

    if not forma_de_pagamento_existe.data:
        return (supabase.table("forma_pagamento").insert({"nome": nome, "id_usuario": user_id}).execute())
    else:
        raise Exception("Forma de pagamento já existe")


def editar_forma_pagamento(user_id, novo_nome, id_forma_pagamento):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuario sem permissão para editar Forma de pagamento")

    conta_existe = (supabase.table("forma_pagamento").select("*").eq("id_forma_pagamento", id_forma_pagamento).execute())

    if conta_existe.data:
        return (supabase.table("forma_pagamento").update({"nome": novo_nome}).eq("id_forma_pagamento", id_forma_pagamento).execute())
    else:
        raise Exception("Forma de pagamento não existe")

def deletar_forma_pagamento(user_id, id_forma_pagamento):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuario sem permissão para apagar Forma de pagamento")

    conta_existe = (supabase.table("forma_pagamento").select("*").eq("id_forma_pagamento", id_forma_pagamento).execute())

    if conta_existe.data:
        return (supabase.table("forma_pagamento").delete().eq("id_forma_pagamento", id_forma_pagamento).execute())
    else:
        raise Exception("Forma de pagamento não existe")


def listar_forma_pagamento(user_id):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuario sem permissão para listar Forma de pagamento")

    return (supabase.table("forma_pagamento").select("*").execute())
