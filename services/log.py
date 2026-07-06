from supabase_client import supabase


def registrar_log(id_usuario, acao, descricao=None):
    try:
        supabase.table("log_sistema").insert({
            "id_usuario": id_usuario,
            "acao": acao,
            "descricao": descricao
        }).execute()

    except Exception as e:
        print(f"ERRO ao registrar log: {e}")


def listar_logs(user_id, limite=100):
    from services.usuario import buscar_perfil, eh_financeiro

    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuário sem permissão para visualizar logs")

    resposta = (
        supabase.table("log_sistema")
        .select("*, usuario(nome)")
        .order("created_at", desc=True)
        .limit(limite)
        .execute()
    )

    return resposta.data