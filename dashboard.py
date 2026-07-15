from flask import Flask, send_from_directory, jsonify, request, redirect, make_response
import subprocess
import pandas as pd
import os
import sys
import hmac
import hashlib
from datetime import datetime
from functools import wraps
from tendencias import analisar_tendencias
from leads import salvar_lead, listar_leads, atualizar_status
from config import WHATSAPP_NUMERO
from crm import salvar_cliente
from notificacoes import listar_alertas, monitorar_respostas, gerar_link_whatsapp_alerta

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PAINEL = os.path.join(BASE_DIR, "painel")
ACCESS_SECRET = os.environ.get("ACCESS_SECRET", "troque-esta-chave-no-render")
BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")
ADMIN_KEY = os.environ.get("ADMIN_KEY", "troque-esta-chave-admin")

# Três liberações por dia: 08h, 14h e 20h (horário de Brasília).
def periodo_atual():
    agora = datetime.now()
    hora = agora.hour
    if hora < 8:
        slot = "20"
        data = agora.date().isoformat()
    elif hora < 14:
        slot = "08"
        data = agora.date().isoformat()
    elif hora < 20:
        slot = "14"
        data = agora.date().isoformat()
    else:
        slot = "20"
        data = agora.date().isoformat()
    return f"{data}-{slot}"


def token_atual():
    bruto = hmac.new(ACCESS_SECRET.encode(), periodo_atual().encode(), hashlib.sha256).hexdigest()
    return bruto[:12]


def acesso_valido():
    return request.cookies.get("demand_access") == token_atual()


def protegido(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not acesso_valido():
            return jsonify({"erro": "Acesso vencido. Consulte o grupo oficial para o novo link."}), 403
        return func(*args, **kwargs)
    return wrapper


@app.route("/")
def home():
    return """
    <!doctype html><html lang='pt-BR'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
    <title>Demand Hunter</title><style>body{font-family:Arial;background:#101827;color:#fff;display:grid;place-items:center;height:100vh;margin:0}.box{max-width:520px;padding:28px;background:#182235;border-radius:18px;text-align:center}a{color:#7dd3fc}</style>
    <div class='box'><h1>Demand Hunter</h1><p>O acesso atual é liberado pelo grupo oficial.</p><p>Use o link mais recente publicado no grupo.</p></div></html>
    """


@app.route("/acesso/<token>")
def acesso(token):
    if not hmac.compare_digest(token, token_atual()):
        return "Link vencido. Consulte o grupo oficial para receber o novo acesso.", 403
    resposta = make_response(redirect("/app"))
    resposta.set_cookie("demand_access", token_atual(), httponly=True, samesite="Lax", secure=True)
    return resposta


@app.route("/app")
def app_usuario():
    if not acesso_valido():
        return redirect("/")
    return send_from_directory(PAINEL, "index.html")


@app.route("/admin/link")
def admin_link():
    if request.args.get("chave") != ADMIN_KEY:
        return "Acesso negado", 403
    base = BASE_URL or request.host_url.rstrip("/")
    link = f"{base}/acesso/{token_atual()}"
    mensagem = f"🔥 Nova atualização do Demand Hunter disponível:\n\n{link}\n\nO link muda na próxima liberação."
    return jsonify({"periodo": periodo_atual(), "link": link, "mensagem": mensagem})


@app.route("/coletar")
@protegido
def coletar():
    subprocess.run([sys.executable, "main.py"], cwd=BASE_DIR, timeout=120)
    arquivo_csv = os.path.join(BASE_DIR, "oportunidades.csv")
    if not os.path.exists(arquivo_csv):
        return jsonify({"tendencias": [], "oportunidades": [], "whatsapp": WHATSAPP_NUMERO})
    df = pd.read_csv(arquivo_csv)
    oportunidades = df.to_dict(orient="records")
    tendencias = analisar_tendencias(oportunidades)
    return jsonify({"tendencias": tendencias, "oportunidades": oportunidades, "whatsapp": WHATSAPP_NUMERO})


@app.route("/salvar_lead", methods=["POST"])
@protegido
def salvar_lead_rota():
    dados = request.get_json(force=True)
    salvar_lead(dados)
    return jsonify({"ok": True, "mensagem": "Lead salvo com sucesso."})


@app.route("/leads")
@protegido
def leads_rota():
    return jsonify({"leads": listar_leads()})


@app.route("/atualizar_status", methods=["POST"])
@protegido
def atualizar_status_rota():
    dados = request.get_json(force=True)
    atualizar_status(dados.get("link", ""), dados.get("status", "novo"), dados)
    return jsonify({"ok": True, "mensagem": "Status atualizado com sucesso."})


@app.route("/config")
@protegido
def config_rota():
    return jsonify({"whatsapp": WHATSAPP_NUMERO})


@app.route("/registrar_interesse", methods=["POST"])
@protegido
def registrar_interesse():
    dados = request.get_json(force=True)
    salvar_cliente(dados.get("usuario", "anonimo"), dados.get("dor", ""), dados.get("nivel_interesse", "medio"), dados.get("origem", "reddit"))
    return jsonify({"ok": True})


@app.route("/alertas")
@protegido
def alertas_rota():
    alertas = listar_alertas()
    for alerta in alertas:
        alerta["link_whatsapp_alerta"] = gerar_link_whatsapp_alerta(alerta)
    return jsonify({"alertas": alertas})


@app.route("/monitorar_respostas")
@protegido
def monitorar_respostas_rota():
    leads = listar_leads()
    novos = monitorar_respostas(leads)
    alertas = listar_alertas()
    for alerta in alertas:
        alerta["link_whatsapp_alerta"] = gerar_link_whatsapp_alerta(alerta)
    return jsonify({"ok": True, "novos": novos, "quantidade_novos": len(novos), "alertas": alertas})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
