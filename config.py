# CONFIGURAÇÕES DO DEMAND HUNTER PRO

WHATSAPP_NUMERO = ""

try:
    with open("meu_numero.txt", "r", encoding="utf-8") as f:
        WHATSAPP_NUMERO = f.read().strip()
except Exception:
    WHATSAPP_NUMERO = ""

MODO_ALERTAS = True
