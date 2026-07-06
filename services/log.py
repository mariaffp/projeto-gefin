from supabase_client import supabase
from services.utils import executar_com_retry


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
    from supabase_client import supabase_admin

    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuário sem permissão para visualizar logs")

    resposta = executar_com_retry(
        lambda: supabase.table("log_sistema")
        .select("*")
        .order("created_at", desc=True)
        .limit(limite)
        .execute()
    )

    logs = resposta.data or []

    usuarios = executar_com_retry(
        lambda: supabase_admin.table("usuario")
        .select("id, nome")
        .execute()
    )

    mapa_usuarios = {
        usuario["id"]: usuario["nome"]
        for usuario in (usuarios.data or [])
    }

    for log in logs:
        nome = mapa_usuarios.get(log.get("id_usuario"))
        log["usuario"] = {"nome": nome} if nome else None

    return logs