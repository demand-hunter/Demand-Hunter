from feeds import coletar_posts
from analisador import interpretar_oportunidade
from tendencias import analisar_tendencias

import pandas as pd
from datetime import datetime

KEYWORDS = [
    "i need",
    "looking for",
    "need help",
    "can someone build",
    "is there a tool",
    "automation",
    "hire",
    "pay for",
    "expensive",
    "software"
]

CATEGORIAS = {
    "automação": ["automation", "automate", "tool"],
    "dinheiro": ["pay", "cost", "expensive"],
    "freela": ["hire", "freelance", "client"],
    "saas": ["software", "platform", "subscription"]
}

resultados = []

print("\nDEMAND HUNTER PRO INICIADO...\n")

posts = coletar_posts()

for post in posts:

    titulo = post["titulo"]
    link = post["link"]
    resumo = post["resumo"]

    texto = f"{titulo} {resumo}".lower()

    score = 0
    encontrados = []

    for kw in KEYWORDS:

        if kw in texto:
            score += 1
            encontrados.append(kw)

    categorias_detectadas = []

    for categoria, palavras in CATEGORIAS.items():

        for palavra in palavras:

            if palavra in texto:
                categorias_detectadas.append(categoria)
                break

    if score >= 2:

        analise = interpretar_oportunidade(
            categorias_detectadas,
            score,
            titulo
        )

        resultados.append({
            "score": score,
            "categorias": ", ".join(categorias_detectadas),
            "keywords": ", ".join(encontrados),
            "potencial": analise["potencial"],
            "acao": analise["acao"],
            "monetizacao": analise["monetizacao"],
            "chance_venda": analise.get("chance_venda", ""),
            "proximo_passo": analise.get("proximo_passo", ""),
            "titulo": titulo,
            "link": link
        })

tendencias = analisar_tendencias(resultados)

print("\nTOP TENDÊNCIAS:\n")

for t in tendencias:

    print(
        f"{t['categoria']} -> {t['ocorrencias']} ocorrências"
    )

if resultados:

    df = pd.DataFrame(resultados)

    nome = "oportunidades.csv"

    df.to_csv(nome, index=False, encoding="utf-8-sig")

    print("\nTOP OPORTUNIDADES:\n")

    print(df.head(10))

    print(f"\nArquivo salvo: {nome}")

else:

    print("Nenhuma oportunidade encontrada.")

print("\nFINALIZADO.\n")