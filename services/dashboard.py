from supabase_client import supabase
from datetime import date, datetime
import calendar
from services.utils import executar_com_retry


def calcular_saldo_ate(ano, mes):
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    data_limite = date(ano, mes, ultimo_dia).isoformat()

    resposta = executar_com_retry(lambda: supabase.table("transacao").select("valor, tipo").lte("data", data_limite).execute())

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

    resposta = executar_com_retry(lambda: supabase.table("transacao").select("valor").eq("tipo", "SAIDA").gte("data", primeiro_dia).lte("data", ultimo_dia).execute())

    return sum(abs(t["valor"]) for t in resposta.data)


def calcular_entradas_mes(ano, mes):
    primeiro_dia = date(ano, mes, 1).isoformat()
    ultimo_dia = date(ano, mes, calendar.monthrange(ano, mes)[1]).isoformat()

    resposta = executar_com_retry(lambda: supabase.table("transacao").select("valor").eq("tipo", "ENTRADA").gte("data", primeiro_dia).lte("data", ultimo_dia).execute())

    return sum(abs(t["valor"]) for t in resposta.data)


def calcular_previsao_caixa(ano, mes):
    hoje = date.today()
    ultimo_dia_mes = calendar.monthrange(ano, mes)[1]
    saldo_atual = calcular_saldo_ate(ano, mes)

    if date(ano, mes, ultimo_dia_mes) < hoje:
        return saldo_atual

    dias_passados = max(hoje.day, 1) if (hoje.year == ano and hoje.month == mes) else ultimo_dia_mes
    dias_restantes = ultimo_dia_mes - dias_passados

    entradas_mes = calcular_entradas_mes(ano, mes)
    despesas_mes = calcular_despesas_mes(ano, mes)

    media_entrada = entradas_mes / dias_passados if dias_passados > 0 else 0
    media_saida = despesas_mes / dias_passados if dias_passados > 0 else 0

    return saldo_atual + (media_entrada - media_saida) * dias_restantes


def tem_movimentacao_no_mes(ano, mes):
    primeiro_dia = date(ano, mes, 1).isoformat()
    ultimo_dia = date(ano, mes, calendar.monthrange(ano, mes)[1]).isoformat()

    resposta = executar_com_retry(lambda: supabase.table("transacao").select("id_transacao").gte("data", primeiro_dia).lte("data", ultimo_dia).limit(1).execute())
    return len(resposta.data) > 0


MESES_ABREV = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}

def dados_entradas_saidas_por_periodo(data_inicio, data_fim):
    
    #Retorna entradas e saídas agrupadas por mês/ano para o período informado.
    
    resposta = executar_com_retry(lambda: supabase.table("transacao").select("valor, tipo, data").gte("data", data_inicio).lte("data", data_fim).execute())

    resultado = {}

    for t in resposta.data:
        ano_mes = t["data"][:7]  # "YYYY-MM"  Pegando somente o ano e o mes nesse formato
        
        if ano_mes not in resultado: 
            resultado[ano_mes] = {"entrada": 0, "saida": 0} #se o ano e o mes ainda nao estiverem no dicionario, eu adiciono, mas zerados

        valor = abs(t["valor"])
        
        if t["tipo"] == "ENTRADA":
            resultado[ano_mes]["entrada"] += valor
        else:
            resultado[ano_mes]["saida"] += valor

    # Ordena cronologicamente
    chaves = sorted(resultado.keys())
    labels = []
    entradas = []
    saidas = []

    for chave in chaves:
        ano, mes = chave.split("-") #divido o ano e o mes da chave
        labels.append(f"{MESES_ABREV[int(mes)]}/{ano[2:]}")
        entradas.append(resultado[chave]["entrada"])
        saidas.append(resultado[chave]["saida"])

    return labels, entradas, saidas


def dados_despesas_por_categoria_periodo(data_inicio, data_fim):
    
    #Retorna despesas por categoria para o período informado.
    
    resposta = executar_com_retry(lambda: supabase.table("transacao").select("valor, categoria(nome)").eq("tipo", "SAIDA").gte("data", data_inicio).lte("data", data_fim).execute())

    categorias = {}

    for t in resposta.data:
        nome = t["categoria"]["nome"] if t.get("categoria") else "Sem categoria"
        categorias[nome] = categorias.get(nome, 0) + abs(t["valor"]) #pego o valor que esta armazenado em categoria e adiciono o novo que chegou, se nao tiver nenhum valor em categoria, adiciono zero

    return categorias


def dados_evolucao_saldo_periodo(data_inicio, data_fim):
    
    #Retorna evolução do saldo mês a mês para o período informado.
    
    dt_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
    dt_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()

    # Saldo acumulado até o mês anterior ao início
    if dt_inicio.month == 1:
        saldo_base = calcular_saldo_ate(dt_inicio.year - 1, 12)
    else:
        saldo_base = calcular_saldo_ate(dt_inicio.year, dt_inicio.month - 1)

    resposta = executar_com_retry(lambda: supabase.table("transacao").select("valor, tipo, data").gte("data", data_inicio).lte("data", data_fim).execute())
    transacoes = resposta.data

    # Agrupa por mês/ano
    resultado = {}

    for t in transacoes:
        ano_mes = t["data"][:7]
    
        if ano_mes not in resultado:
            resultado[ano_mes] = 0
    
        valor = abs(t["valor"])
    
        if t["tipo"] == "ENTRADA":
            resultado[ano_mes] += valor
        else:
            resultado[ano_mes] -= valor

    chaves = sorted(resultado.keys())
    labels = []
    saldos = []
    saldo_acumulado = saldo_base

    for chave in chaves:
        saldo_acumulado += resultado[chave]
        ano, mes = chave.split("-")
        labels.append(f"{MESES_ABREV[int(mes)]}/{ano[2:]}")
        saldos.append(saldo_acumulado)

    return labels, saldos


