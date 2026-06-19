from services.usuario import buscar_perfil,eh_financeiro
from supabase_client import supabase
from datetime import datetime, timezone

def normalizar_nome(nome):
    nome = " ".join(nome.strip().split())
    nome = nome.title()
    return nome


def criar_categoria(nome, user_id):
    
    nome = normalizar_nome(nome)

    perfil =  buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuário sem permissão")


    categoria_existe = (
        supabase.table("categoria")\
            .select("*")\
            .eq("nome", nome)\
            .execute()
    )

    if not categoria_existe.data :
        return (
        supabase.table("categoria")\
            .insert({"nome": nome, "id_usuario": user_id})\
            .execute()
    )
    elif categoria_existe.data[0]["deletado"] is None:
        raise Exception("Categoria já existe")
    
    elif  categoria_existe.data[0]["deletado"] is not None:
        return (
            supabase.table("categoria")\
                .update({"deletado": None})
                .eq("id_categoria", categoria_existe.data[0]["id_categoria"])\
                .execute()            
        )
    

def editar_categoria(id_cat, nome, user_id):

    nome = normalizar_nome(nome)

    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuário sem permissão")

    categoria = (
        supabase.table("categoria")
        .select("*")
        .eq("id_categoria", id_cat)
        .execute()
    )

    if not categoria.data:
        raise Exception("Categoria não encontrada")

    categoria_existente = (
        supabase.table("categoria")
        .select("*")
        .eq("nome", nome)
        .is_("deletado",None)
        .execute()
    )

    if (
        categoria_existente.data
        and categoria_existente.data[0]["id_categoria"] != id_cat
    ):
        raise Exception("Já existe uma categoria com esse nome")

    return (
        supabase.table("categoria")
        .update({"nome": nome})
        .eq("id_categoria", id_cat)
        .execute()
    )


def listar_categorias():
    return (
        supabase.table("categoria")\
            .select("*")\
            .is_("deletado",None)\
            .execute()
    )


def excluir_categoria(id_cat, user_id):

    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuário sem permissão")

    categoria = (
        supabase.table("categoria")
        .select("deletado")
        .eq("id_categoria", id_cat)
        .execute()
    )

    if not categoria.data:
        raise Exception("Categoria não encontrada")

    if categoria.data[0]["deletado"] is not None:
        raise Exception("Categoria já está deletada")

    return (
        supabase.table("categoria")
        .update({"deletado": datetime.now(timezone.utc).isoformat()})
        .eq("id_categoria", id_cat)
        .execute()
    )
