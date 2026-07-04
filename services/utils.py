import time

def executar_com_retry(funcao, tentativas=3, espera=1):
    for tentativa in range(tentativas):
        try:
            return funcao()
        except Exception as e:
            print(f"Tentativa {tentativa + 1} falhou: {e}")
            if tentativa < tentativas - 1:
                time.sleep(espera)
            else:
                raise