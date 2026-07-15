import csv
import os
from datetime import datetime
from urllib.parse import quote_plus

try:
    import requests
except Exception:
    requests = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_ALERTAS = os.path.join(BASE_DIR, "alertas_respostas.csv")
ARQUIVO_NUMERO = os.path.join(BASE_DIR, "meu_numero.txt")
ARQUIVO_CALLMEBOT = os.path.join(BASE_DIR, "callmebot_apikey.txt")

CAMPOS_ALERTAS = [
    "data", "origem", "titulo", "link", "usuario", "comentario", "acao_sugerida",
    "status", "id_externo", "notificado_whatsapp"
]

PALAVRAS_INTERESSE = [
    "yes", "sure", "send", "share", "interested", "model", "template", "structure",
    "quero", "manda", "envia", "interesse", "modelo", "estrutura", "pode mandar"
]


def ler_numero():
    try:
        with open(ARQUIVO_NUMERO, "r", encoding="utf-8") as f:
            return "".join(ch for ch in f.read().strip() if ch.isdigit())
    except Exception:
        return ""


def ler_callmebot_key():
    try:
        with open(ARQUIVO_CALLMEBOT, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""


def listar_alertas():
    if not os.path.exists(ARQUIVO_ALERTAS):
        return []
    with open(ARQUIVO_ALERTAS, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def alerta_existe(id_externo):
    return any(a.get("id_externo") == id_externo for a in listar_alertas())


def salvar_alerta(dados):
    novo = not os.path.exists(ARQUIVO_ALERTAS)
    linha = {campo: dados.get(campo, "") for campo in CAMPOS_ALERTAS}
    linha["data"] = linha.get("data") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha["status"] = linha.get("status") or "novo"
    linha["notificado_whatsapp"] = linha.get("notificado_whatsapp") or "nao"
    with open(ARQUIVO_ALERTAS, "a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_ALERTAS, extrasaction="ignore")
        if novo:
            writer.writeheader()
        writer.writerow(linha)
    return True


def montar_mensagem_alerta(alerta):
    return (
        "🚨 Resposta detectada no Demand Hunter\n\n"
        f"Oportunidade: {alerta.get('titulo','')}\n"
        f"Usuário: {alerta.get('usuario','')}\n\n"
        f"Resposta: {alerta.get('comentario','')}\n\n"
        f"Ação sugerida: {alerta.get('acao_sugerida','Responder e puxar para o funil.')}\n\n"
        f"Link: {alerta.get('link','')}"
    )


def gerar_link_whatsapp_alerta(alerta):
    numero = ler_numero()
    if not numero:
        return ""
    return "https://wa.me/" + numero + "?text=" + quote_plus(montar_mensagem_alerta(alerta))


def tentar_notificar_whatsapp(alerta):
    """Envio automático opcional via CallMeBot. Se não estiver configurado, apenas retorna False."""
    numero = ler_numero()
    key = ler_callmebot_key()
    if not numero or not key or requests is None:
        return False
    try:
        url = "https://api.callmebot.com/whatsapp.php"
        params = {"phone": "+" + numero, "text": montar_mensagem_alerta(alerta), "apikey": key}
        r = requests.get(url, params=params, timeout=15)
        return r.status_code == 200
    except Exception:
        return False


def _reddit_json_url(link):
    if not link or "reddit.com" not in link:
        return ""
    base = link.split("?")[0].rstrip("/")
    if not base.endswith(".json"):
        base += ".json"
    return base


def _extrair_comentarios_reddit(obj, saida=None):
    saida = saida or []
    if isinstance(obj, dict):
        data = obj.get("data", {}) if isinstance(obj.get("data"), dict) else {}
        kind = obj.get("kind", "")
        if kind == "t1" and data:
            saida.append({
                "id": data.get("id", ""),
                "author": data.get("author", ""),
                "body": data.get("body", ""),
                "created_utc": data.get("created_utc", 0),
                "parent_id": data.get("parent_id", "")
            })
        for v in obj.values():
            _extrair_comentarios_reddit(v, saida)
    elif isinstance(obj, list):
        for v in obj:
            _extrair_comentarios_reddit(v, saida)
    return saida


def monitorar_reddit_lead(lead):
    if requests is None:
        return []
    link = lead.get("link", "")
    url = _reddit_json_url(link)
    if not url:
        return []
    try:
        r = requests.get(url, headers={"User-Agent": "DemandHunterLocal/1.0"}, timeout=20)
        if r.status_code != 200:
            return []
        comentarios = _extrair_comentarios_reddit(r.json())
    except Exception:
        return []

    alertas = []
    titulo = lead.get("titulo", "")
    for c in comentarios:
        corpo = (c.get("body") or "").strip()
        if not corpo:
            continue
        texto = corpo.lower()
        tem_interesse = any(p in texto for p in PALAVRAS_INTERESSE)
        # Sem login/API, usamos detecção leve: respostas com intenção de receber modelo/estrutura.
        if not tem_interesse:
            continue
        id_externo = "reddit:" + link + ":" + c.get("id", "")
        if alerta_existe(id_externo):
            continue
        alerta = {
            "origem": "reddit",
            "titulo": titulo,
            "link": link,
            "usuario": c.get("author", ""),
            "comentario": corpo[:900],
            "acao_sugerida": "Responder oferecendo o modelo base e puxar para WhatsApp quando fizer sentido.",
            "status": "novo",
            "id_externo": id_externo,
        }
        enviado = tentar_notificar_whatsapp(alerta)
        alerta["notificado_whatsapp"] = "sim" if enviado else "nao"
        salvar_alerta(alerta)
        alertas.append(alerta)
    return alertas


def monitorar_respostas(leads):
    novos = []
    for lead in leads:
        status = (lead.get("status") or "").lower()
        if status not in ["comentado", "respondeu", "link_whatsapp_enviado", "aguardando_resposta"]:
            continue
        if "reddit.com" in (lead.get("link") or ""):
            novos.extend(monitorar_reddit_lead(lead))
    return novos
