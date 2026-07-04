import os
import re
from datetime import datetime, timezone
import pandas as pd
from supabase_client import supabase
from services.usuario import buscar_perfil, eh_financeiro
from services.conta import criar_conta
from services.forma_pagamento import criar_forma_pagamento
from services.transacao import verificar_duplicatas, salvar_transacoes_importadas
from zoneinfo import ZoneInfo


COLUNAS_CORA = {
    "DATA",
    "DESCRIÇÃO",
    "TIPO TRANSAÇÃO",
    "IDENTIFICAÇÃO",
    "VALOR"
}

COLUNAS_MOBILLS = {
    "DATA",
    "DESCRIÇÃO",
    "VALOR",
    "CONTA",
    "SITUAÇÃO",
    "CATEGORIA",
    "SUBCATEGORIA"
}


def normalizar_coluna(nome):
    return str(nome).strip().upper()


def normalizar_texto(texto):
    if pd.isna(texto):
        return None

    texto = str(texto).strip()

    if not texto:
        return None

    return " ".join(texto.split())


def normalizar_forma_pagamento(nome):
    nome = normalizar_texto(nome)

    if not nome:
        return None

    nome = nome.upper()

    if "CREDITO" in nome or "CRÉDITO" in nome:
        return "CRÉDITO"

    if "DEBITO" in nome or "DÉBITO" in nome:
        return "DÉBITO"

    if "PIX" in nome:
        return "PIX"

    return nome


def extrair_parcelamento(tipo_transacao):
    texto = normalizar_texto(tipo_transacao)

    if not texto:
        return None, None, None

    texto_upper = texto.upper()

    if "CRÉDITO" not in texto_upper and "CREDITO" not in texto_upper:
        return texto, None, None

    if "À VISTA" in texto_upper or "A VISTA" in texto_upper:
        return "CRÉDITO", 1, 1

    match = re.search(r"\((\d+)\/(\d+)\)", texto_upper)

    if match:
        numero_parcela = int(match.group(1))
        total_parcelas = int(match.group(2))

        if numero_parcela > total_parcelas:
            raise Exception(f"Parcelamento inválido: {tipo_transacao}")

        return "CRÉDITO", numero_parcela, total_parcelas

    return "CRÉDITO", None, None


def ler_csv_pandas(caminho_arquivo):
    df = pd.read_csv(caminho_arquivo, sep=",")

    if len(df.columns) == 1:
        df = pd.read_csv(caminho_arquivo, sep=";")

    return df


def colunas_normalizadas(df):
    return {normalizar_coluna(coluna) for coluna in df.columns}


def eh_cora(df):
    return COLUNAS_CORA.issubset(colunas_normalizadas(df))


def eh_mobills(df):
    return COLUNAS_MOBILLS.issubset(colunas_normalizadas(df))


def renomear_colunas_normalizadas(df):
    df = df.copy()
    df.columns = [normalizar_coluna(coluna) for coluna in df.columns]
    return df


def converter_valor(valor):
    if pd.isna(valor):
        raise Exception("Valor vazio encontrado no arquivo")

    valor = str(valor).strip()
    valor = valor.replace("R$", "").replace(" ", "")

    if "," in valor:
        valor = valor.replace(".", "").replace(",", ".")

    return float(valor)


def converter_data(data):
    if pd.isna(data):
        raise Exception("Data vazia encontrada no arquivo")

    data_convertida = pd.to_datetime(data, dayfirst=True, errors="coerce")

    if pd.isna(data_convertida):
        raise Exception(f"Data inválida: {data}")

    return data_convertida.date().isoformat()


def definir_situacao(valor):
    if valor < 0:
        return "Pago"

    return "Recebido"


def normalizar_situacao(situacao, valor):
    situacao = normalizar_texto(situacao)

    if not situacao:
        return definir_situacao(valor)

    mapa = {
        "PAGO": "Pago",
        "RECEBIDO": "Recebido",
        "A PAGAR": "A Pagar",
        "A RECEBER": "A Receber",
    }

    return mapa.get(situacao.upper(), situacao)


def definir_tipo(valor):
    if valor < 0:
        return "SAIDA"

    return "ENTRADA"


def normalizar_subcategoria(subcategoria):
    subcategoria = normalizar_texto(subcategoria)

    if not subcategoria:
        return "PENDENTE"

    return subcategoria.upper().replace(" ", "_")


def buscar_categoria_ou_pendente(nome_categoria):
    nome_categoria = normalizar_texto(nome_categoria)

    if nome_categoria:
        categoria = (
            supabase.table("categoria")
            .select("id_categoria")
            .eq("nome", nome_categoria)
            .is_("deletado", None)
            .execute()
        )

        if categoria.data:
            return categoria.data[0]["id_categoria"]

    pendente = (
        supabase.table("categoria")
        .select("id_categoria")
        .eq("nome", "Pendente")
        .is_("deletado", None)
        .execute()
    )

    if not pendente.data:
        raise Exception("Categoria Pendente não encontrada no banco")

    return pendente.data[0]["id_categoria"]


def buscar_ou_criar_conta(nome, user_id):
    nome = normalizar_texto(nome)

    if not nome:
        raise Exception("Conta vazia encontrada no arquivo")

    conta = (
        supabase.table("conta")
        .select("id_conta")
        .eq("nome", nome)
        .execute()
    )

    if conta.data:
        return conta.data[0]["id_conta"]

    nova_conta = criar_conta(nome, user_id)
    return nova_conta.data[0]["id_conta"]


def buscar_ou_criar_forma_pagamento(nome, user_id):
    nome = normalizar_forma_pagamento(nome)

    if not nome:
        return None

    forma_pagamento = (
        supabase.table("forma_pagamento")
        .select("id_forma_pagamento")
        .eq("nome", nome)
        .execute()
    )

    if forma_pagamento.data:
        return forma_pagamento.data[0]["id_forma_pagamento"]

    nova_forma_pagamento = criar_forma_pagamento(nome, user_id)
    return nova_forma_pagamento.data[0]["id_forma_pagamento"]


def registrar_importacao(caminho_arquivo, origem, user_id, nome_arquivo_original=None):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuário sem permissão para registrar importação")

    nome_arquivo = (
        nome_arquivo_original
        if nome_arquivo_original
        else os.path.basename(caminho_arquivo)
    )

    resposta = (
        supabase.table("importacao")
        .insert({
            "id_usuario": user_id,
            "nome_arquivo": nome_arquivo,
            "formato": "CSV",
            "origem": origem,
            "data_importacao": datetime.now(ZoneInfo("America/Sao_Paulo")
            ).isoformat()
        })
        .execute()
    )

    return resposta.data[0]["id_importacao"]


def mapear_cora(df, user_id):
    df = renomear_colunas_normalizadas(df)

    id_conta = buscar_ou_criar_conta("Cora", user_id)
    id_categoria_pendente = buscar_categoria_ou_pendente(None)

    transacoes = []

    for _, row in df.iterrows():
        valor = converter_valor(row["VALOR"])

        forma_pagamento, numero_parcela, total_parcelas = extrair_parcelamento(
            row["TIPO TRANSAÇÃO"]
        )

        transacoes.append({
            "data": converter_data(row["DATA"]),
            "descricao": normalizar_texto(row["DESCRIÇÃO"]),
            "valor": valor,
            "id_conta": id_conta,
            "id_forma_pagamento": buscar_ou_criar_forma_pagamento(forma_pagamento, user_id),
            "situacao": definir_situacao(valor),
            "subcategoria": "PENDENTE",
            "id_categoria": id_categoria_pendente,
            "id_usuario": user_id,
            "id_importacao": None,
            "numero_parcela": numero_parcela,
            "total_parcelas": total_parcelas,
            "tipo": definir_tipo(valor),
            "identificacao": normalizar_texto(row["IDENTIFICAÇÃO"])
        })

    return transacoes


def mapear_mobills(df, user_id):
    df = renomear_colunas_normalizadas(df)

    transacoes = []

    for _, row in df.iterrows():
        valor = converter_valor(row["VALOR"])

        transacoes.append({
            "data": converter_data(row["DATA"]),
            "descricao": normalizar_texto(row["DESCRIÇÃO"]),
            "valor": valor,
            "id_conta": buscar_ou_criar_conta(row["CONTA"], user_id),
            "id_forma_pagamento": None,
            "situacao": normalizar_situacao(row["SITUAÇÃO"], valor),
            "subcategoria": normalizar_subcategoria(row["SUBCATEGORIA"]),
            "id_categoria": buscar_categoria_ou_pendente(row["CATEGORIA"]),
            "id_usuario": user_id,
            "id_importacao": None,
            "numero_parcela": None,
            "total_parcelas": None,
            "tipo": definir_tipo(valor),
            "identificacao": None
        })

    return transacoes


def listar_importacoes(user_id):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuário sem permissão para listar importações")

    return (
        supabase.table("importacao")
        .select("*")
        .order("data_importacao", desc=True)
        .execute()
    )


def buscar_importacao(id_importacao, user_id):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuário sem permissão para buscar importação")

    importacao = (
        supabase.table("importacao")
        .select("*")
        .eq("id_importacao", id_importacao)
        .execute()
    )

    if not importacao.data:
        raise Exception("Importação não encontrada")

    return importacao.data[0]


def ler_csv(caminho_arquivo, user_id, confirmar_duplicatas=False, nome_arquivo_original=None):
    perfil = buscar_perfil(user_id)

    if not eh_financeiro(perfil):
        raise Exception("Usuário sem permissão para importar CSV")

    df = ler_csv_pandas(caminho_arquivo)

    if eh_cora(df):
        origem = "CORA"
        transacoes = mapear_cora(df, user_id)

    elif eh_mobills(df):
        origem = "MOBILLS"
        transacoes = mapear_mobills(df, user_id)

    else:
        raise Exception("Formato de CSV não reconhecido")

    duplicatas = verificar_duplicatas(transacoes, user_id)

    if duplicatas and not confirmar_duplicatas:
        return {
            "status": "duplicatas_encontradas",
            "mensagem": f"Foram encontradas {len(duplicatas)} possíveis transações duplicadas.",
            "duplicatas": duplicatas
        }

    id_importacao = registrar_importacao(
        caminho_arquivo,
        origem,
        user_id,
        nome_arquivo_original
    )

    salvar_transacoes_importadas(
        transacoes=transacoes,
        id_importacao=id_importacao,
        user_id=user_id
    )

    registrar_log(user_id, "IMPORTACAO_EXTRATO", f"Arquivo '{nome_arquivo}' importado com {len(transacoes)} transações")


    return {
        "status": "sucesso",
        "mensagem": "Importação concluída com sucesso.",
        "origem": origem,
        "quantidade": len(transacoes),
        "id_importacao": id_importacao
    }