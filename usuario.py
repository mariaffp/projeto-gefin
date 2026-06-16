from supabase_client import supabase, supabase_admin


def buscar_perfil(user_id):
    # select: quais colunas eu quero | eq: uma das colunas deve respeitar a seguinte igualdade | single: retorna só um registro | executa: para executar a consulta
    try:

        registro = supabase.table("usuario").select("perfil").eq("id", user_id).single().execute()
        #registro.data é um dicionario de dados, estou verificando se ele é null
        if registro.data:
            return registro.data['perfil'] #retornando o valor do campo de perfil que pode ser normal, financeiro ou admin
        return None #Se não existe usuario com aquele id, retorno nada
    except Exception as e:
        print("ERRO no buscar_perfil:", e)  # ← vai mostrar o erro exato
        return None


def eh_admin(perfil):
    return perfil =='ADMIN' #Vai retornar True se perfil for admin e False se nao for

def eh_financeiro(perfil):
    return perfil in ['FINANCEIRO', 'ADMIN'] #Vai retornar True se perfil for admin ou financeiro e False se nao for

#Função para tentar conectar a tabela do auth.user com a do usuario
def cadastrar_usuario(email, senha, nome, perfil):
    try:
        # Cria o usuário no auth.users com o nome nos metadados
        resposta = supabase_admin.auth.admin.create_user({
            "email": email,
            "password": senha,
            "user_metadata": {
                "full_name": nome  # trigger vai pegar esse nome
            },
            "email_confirm": True  # já confirma o email automaticamente, podemos tirar talvez
        })
        
        # Atualiza o perfil se não for NORMAL
        if perfil != 'NORMAL':
            supabase.table("usuario") \
                .update({"perfil": perfil}) \
                .eq("id", resposta.user.id) \
                .execute()

        return True
    except Exception as e:
        print("ERRO ao cadastrar usuário:", e)
        return False