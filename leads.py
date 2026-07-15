import csv
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_LEADS = os.path.join(BASE_DIR, "leads.csv")

# Mantive os campos originais e acrescentei apenas campos do funil.
CAMPOS = [
    "data",
    "titulo",
    "categorias",
    "potencial",
    "chance_venda",
    "acao",
    "monetizacao",
    "proximo_passo",
    "link",
    "proposta",
    "status",
    "abordagem_publica",
    "isca_gratis",
    "link_whatsapp_dor",
    "venda_privada",
    "ultima_acao"
]

STATUS_FUNIL = [
    "novo",
    "comentado",
    "respondeu",
    "link_whatsapp_enviado",
    "chamou_whatsapp",
    "modelo_enviado",
    "oferta_enviada",
    "fechado",
    "perdido"
]

def _linha_padrao(dados):
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "data": dados.get("data", agora),
        "titulo": dados.get("titulo", ""),
        "categorias": dados.get("categorias", ""),
        "potencial": dados.get("potencial", ""),
        "chance_venda": dados.get("chance_venda", ""),
        "acao": dados.get("acao", ""),
        "monetizacao": dados.get("monetizacao", ""),
        "proximo_passo": dados.get("proximo_passo", ""),
        "link": dados.get("link", ""),
        "proposta": dados.get("proposta", ""),
        "status": dados.get("status", "novo"),
        "abordagem_publica": dados.get("abordagem_publica", ""),
        "isca_gratis": dados.get("isca_gratis", ""),
        "link_whatsapp_dor": dados.get("link_whatsapp_dor", ""),
        "venda_privada": dados.get("venda_privada", ""),
        "ultima_acao": dados.get("ultima_acao", agora)
    }

def salvar_lead(dados):
    novo = not os.path.exists(ARQUIVO_LEADS)

    with open(ARQUIVO_LEADS, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS, extrasaction="ignore")

        if novo:
            writer.writeheader()

        writer.writerow(_linha_padrao(dados))

    return True

def listar_leads():
    if not os.path.exists(ARQUIVO_LEADS):
        return []

    with open(ARQUIVO_LEADS, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)

def atualizar_status(link, status, dados_extras=None):
    """Atualiza o status de um lead pelo link. Se ainda não existir, cria um registro mínimo."""
    if status not in STATUS_FUNIL:
        status = "novo"

    dados_extras = dados_extras or {}
    linhas = listar_leads()
    encontrou = False
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for linha in linhas:
        if linha.get("link", "") == link:
            linha.update({k: v for k, v in dados_extras.items() if v is not None})
            linha["status"] = status
            linha["ultima_acao"] = agora
            encontrou = True

    if not encontrou:
        dados_extras["link"] = link
        dados_extras["status"] = status
        dados_extras["ultima_acao"] = agora
        salvar_lead(dados_extras)
        return True

    with open(ARQUIVO_LEADS, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS, extrasaction="ignore")
        writer.writeheader()
        for linha in linhas:
            writer.writerow(_linha_padrao(linha))

    return True
