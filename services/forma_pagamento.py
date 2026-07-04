from services.usuario import buscar_perfil, eh_financeiro
from services.log import registrar_log
from supabase_client import supabase


def criar_forma_pagamento(nome, user_id):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuario sem permissão para criar forma de pagamento")

    forma_existe = supabase.table("forma_pagamento").select("*").eq("nome", nome).execute()

    if not forma_existe.data:
        resultado = supabase.table("forma_pagamento").insert({"nome": nome, "id_usuario": user_id}).execute()
        registrar_log(user_id, "FORMA_PAGAMENTO_CRIADA", f"Forma de pagamento '{nome}' criada")
        return resultado
    else:
        raise Exception("Forma de pagamento já existe")


def editar_forma_pagamento(user_id, novo_nome, id_forma_pagamento):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuario sem permissão para editar Forma de pagamento")

    forma_existe = supabase.table("forma_pagamento").select("*").eq("id_forma_pagamento", id_forma_pagamento).execute()

    if forma_existe.data:
        nome_antigo = forma_existe.data[0]["nome"]
        resultado = supabase.table("forma_pagamento").update({"nome": novo_nome}).eq("id_forma_pagamento", id_forma_pagamento).execute()
        registrar_log(user_id, "FORMA_PAGAMENTO_EDITADA", f"Forma de pagamento '{nome_antigo}' renomeada para '{novo_nome}'")
        return resultado
    else:
        raise Exception("Forma de pagamento não existe")


def deletar_forma_pagamento(user_id, id_forma_pagamento):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuario sem permissão para apagar Forma de pagamento")

    forma_existe = supabase.table("forma_pagamento").select("*").eq("id_forma_pagamento", id_forma_pagamento).execute()

    if forma_existe.data:
        nome = forma_existe.data[0]["nome"]
        resultado = supabase.table("forma_pagamento").delete().eq("id_forma_pagamento", id_forma_pagamento).execute()
        registrar_log(user_id, "FORMA_PAGAMENTO_DELETADA", f"Forma de pagamento '{nome}' deletada")
        return resultado
    else:
        raise Exception("Forma de pagamento não existe")


def listar_forma_pagamento(user_id):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuario sem permissão para listar Forma de pagamento")

    return supabase.table("forma_pagamento").select("*").execute()