from services.usuario import buscar_perfil, eh_financeiro
from supabase_client import supabase
from datetime import datetime, timezone


def normalizar_nome(nome):
    nome = " ".join(nome.strip().split())
    nome = nome.title()
    return nome


def validar_financeiro(user_id):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuário sem permissão")


def criar_categoria(nome, user_id):
    nome = normalizar_nome(nome)
    validar_financeiro(user_id)

    categoria_existe = (
        supabase.table("categoria")
        .select("*")
        .eq("nome", nome)
        .execute()
    )

    if not categoria_existe.data:
        return (
            supabase.table("categoria")
            .insert({"nome": nome, "id_usuario": user_id})
            .execute()
        )

    categoria = categoria_existe.data[0]

    if categoria["deletado"] is None:
        raise Exception("Categoria já existe")

    return (
        supabase.table("categoria")
        .update({"deletado": None})
        .eq("id_categoria", categoria["id_categoria"])
        .execute()
    )


def editar_categoria(id_cat, nome, user_id):
    nome = normalizar_nome(nome)
    validar_financeiro(user_id)

    categoria = (
        supabase.table("categoria")
        .select("*")
        .eq("id_categoria", id_cat)
        .execute()
    )

    if not categoria.data:
        raise Exception("Categoria não encontrada")

    categoria_atual = categoria.data[0]

    if categoria_atual["deletado"] is not None:
        raise Exception("Não é possível editar uma categoria desativada")

    if categoria_atual["nome"] == "Pendente":
        raise Exception("A categoria Pendente não pode ser editada")

    categoria_com_mesmo_nome = (
        supabase.table("categoria")
        .select("*")
        .eq("nome", nome)
        .execute()
    )

    if categoria_com_mesmo_nome.data:
        categoria_existente = categoria_com_mesmo_nome.data[0]

        if categoria_existente["id_categoria"] != id_cat:
            if categoria_existente["deletado"] is None:
                raise Exception("Já existe uma categoria ativa com esse nome")

            raise Exception(
                "Essa categoria já existe, mas está desativada. "
                "Reative-a na lista de categorias desativadas."
            )

    return (
        supabase.table("categoria")
        .update({"nome": nome})
        .eq("id_categoria", id_cat)
        .execute()
    )


def listar_categorias():
    return (
        supabase.table("categoria")
        .select("*")
        .is_("deletado", None)
        .order("nome")
        .execute()
    )


def listar_categorias_desativadas(user_id):
    validar_financeiro(user_id)

    return (
        supabase.table("categoria")
        .select("*")
        .not_.is_("deletado", None)
        .order("nome")
        .execute()
    )


def listar_todas_categorias(user_id):
    validar_financeiro(user_id)

    return (
        supabase.table("categoria")
        .select("*")
        .order("nome")
        .execute()
    )


def excluir_categoria(id_cat, user_id):
    validar_financeiro(user_id)

    categoria = (
        supabase.table("categoria")
        .select("*")
        .eq("id_categoria", id_cat)
        .execute()
    )

    if not categoria.data:
        raise Exception("Categoria não encontrada")

    categoria_atual = categoria.data[0]

    if categoria_atual["deletado"] is not None:
        raise Exception("Categoria já está desativada")

    if categoria_atual["nome"] == "Pendente":
        raise Exception("A categoria Pendente não pode ser desativada")

    return (
        supabase.table("categoria")
        .update({"deletado": datetime.now(timezone.utc).isoformat()})
        .eq("id_categoria", id_cat)
        .execute()
    )


def reativar_categoria(id_cat, user_id):
    validar_financeiro(user_id)

    categoria = (
        supabase.table("categoria")
        .select("*")
        .eq("id_categoria", id_cat)
        .execute()
    )

    if not categoria.data:
        raise Exception("Categoria não encontrada")

    categoria_atual = categoria.data[0]

    if categoria_atual["deletado"] is None:
        raise Exception("Categoria já está ativa")

    categoria_ativa_mesmo_nome = (
        supabase.table("categoria")
        .select("*")
        .eq("nome", categoria_atual["nome"])
        .is_("deletado", None)
        .execute()
    )

    if categoria_ativa_mesmo_nome.data:
        raise Exception("Já existe uma categoria ativa com esse nome")

    return (
        supabase.table("categoria")
        .update({"deletado": None})
        .eq("id_categoria", id_cat)
        .execute()
    )