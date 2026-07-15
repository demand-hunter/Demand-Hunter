from collections import Counter

def analisar_tendencias(resultados):

    contador = Counter()

    for item in resultados:

        categorias = item["categorias"].split(",")

        for categoria in categorias:

            categoria = categoria.strip()

            if categoria:
                contador[categoria] += 1

    tendencias = []

    for categoria, total in contador.items():

        tendencias.append({
            "categoria": categoria,
            "ocorrencias": total
        })

    tendencias = sorted(
        tendencias,
        key=lambda x: x["ocorrencias"],
        reverse=True
    )

    return tendencias