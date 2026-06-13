from supabase_client import supabase


def buscar_perfil(user_id):
    # select: quais colunas eu quero | eq: uma das colunas deve respeitar a seguinte igualdade | single: retorna só um registro | executa: para executar a consulta
    registro = supabase.table("usuario").select("perfil").eq("id", user_id).single().execute()

     #registro.data é um dicionario de dados, estou verificando se ele é null
    if registro.data:
        return registro.data['perfil'] #retornando o valor do campo de perfil que pode ser normal, financeiro ou admin
    return None #Se não existe usuario com aquele id, retorno nada


def eh_admin(perfil):
    return perfil =='ADMIN' #Vai retornar True se perfil for admin e False se nao for

def eh_financeiro(perfil):
    return perfil in ['FINANCEIRO', 'ADMIN'] #Vai retornar True se perfil for admin ou financeiro e False se nao for
