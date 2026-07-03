from supabase_client import supabase
from datetime import date
import calendar

def calcular_saldo_ate(ano, mes):

    ultimo_dia = calendar.monthrange(ano, mes)[1]
    data_limite = date(ano, mes, ultimo_dia).isoformat()

    resposta = supabase.table("transacao").select("valor, tipo").lte("data", data_limite).execute()

    saldo = 0

    for t in resposta.data:
        valor = abs(t["valor"])
        if t["tipo"] == "ENTRADA":
            saldo += valor
        else:
            saldo -= valor

    return saldo


def calcular_despesas_mes(ano, mes):

    primeiro_dia = date(ano, mes, 1).isoformat()
    ultimo_dia = date(ano, mes, calendar.monthrange(ano, mes)[1]).isoformat()

    resposta = supabase.table("transacao").select("valor").eq( "tipo", "SAIDA").gte("data", primeiro_dia).lte("data", ultimo_dia).execute()

    soma = 0
    for t in resposta.data:
        valor = abs(t["valor"])
        soma += valor

    return soma

def calcular_entradas_mes(ano, mes):

    primeiro_dia = date(ano, mes, 1).isoformat()
    ultimo_dia = date(ano, mes, calendar.monthrange(ano, mes)[1]).isoformat()

    resposta = supabase.table("transacao").select("valor").eq( "tipo", "ENTRADA").gte("data", primeiro_dia).lte("data", ultimo_dia).execute()

    soma = 0
    for t in resposta.data:
        valor = abs(t["valor"])
        soma += valor

    return soma

def calcular_previsao_caixa(ano, mes):
   
    hoje = date.today()
    ultimo_dia_mes = calendar.monthrange(ano, mes)[1]

    saldo_atual = calcular_saldo_ate(ano, mes)

    # Se o mês já passou, a previsão é o próprio saldo final real
    if date(ano, mes, ultimo_dia_mes) < hoje:
        return saldo_atual

    # Quantos dias já se passaram no mês (mínimo 1 para evitar divisão por zero)

    if hoje.year == ano and hoje.month == mes:
        dias_passados = max(hoje.day, 1)
    else:
        dias_passados = ultimo_dia_mes
    
    dias_restantes = ultimo_dia_mes - dias_passados

    entradas_mes = calcular_entradas_mes(ano, mes)
    despesas_mes = calcular_despesas_mes(ano, mes)

    if dias_passados > 0:
        media_entrada_diaria = entradas_mes / dias_passados
        media_saida_diaria = despesas_mes / dias_passados
    else:
        media_entrada_diaria = 0
        media_saida_diaria = 0


    previsao = saldo_atual + (media_entrada_diaria - media_saida_diaria) * dias_restantes

    return previsao


def tem_movimentacao_no_mes(ano, mes):

    #Verifica se existe pelo menos uma transação no mês/ano informado.
    primeiro_dia = date(ano, mes, 1).isoformat()
    ultimo_dia = date(ano, mes, calendar.monthrange(ano, mes)[1]).isoformat()
    resposta = supabase.table("transacao").select("id_transacao").gte("data", primeiro_dia).lte("data", ultimo_dia).limit(1).execute()

    return len(resposta.data) > 0
