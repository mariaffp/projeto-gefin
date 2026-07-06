import time

def executar_com_retry(funcao, tentativas=3, espera=1):
    for tentativa in range(tentativas):
        try:
            return funcao()
        except Exception as e:
            erro = str(e)
            # Não tenta de novo se for erro de permissão ou dados
            if "permission denied" in erro or "42501" in erro:
                raise
            print(f"Tentativa {tentativa + 1} de {tentativas} falhou: {e}")
            if tentativa < tentativas - 1:
                time.sleep(espera)
            else:
                raise