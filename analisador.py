def interpretar_oportunidade(categorias, score, titulo):

    potencial = "BAIXO"
    acao = "Monitorar"
    monetizacao = "Indefinida"
    chance_venda = "BAIXA"
    proximo_passo = "Acompanhar e esperar mais sinais."

    titulo_lower = titulo.lower()
    cats = " ".join(categorias).lower()

    if score >= 3:
        potencial = "ALTO"
        chance_venda = "ALTA"
    elif score == 2:
        potencial = "MÉDIO"
        chance_venda = "MÉDIA"

    if "saas" in categorias:
        acao = "Criar micro SaaS simples/barato"
        monetizacao = "Assinatura mensal"
        proximo_passo = "Validar dor, oferecer versão simples e coletar interesse."

    elif "freela" in categorias:
        acao = "Oferecer automação ou serviço remoto"
        monetizacao = "Serviço recorrente"
        proximo_passo = "Oferecer ajuda prática e rápida com baixo custo inicial."

    elif "automação" in categorias:
        acao = "Criar ferramenta automática"
        monetizacao = "Venda da ferramenta"
        proximo_passo = "Criar protótipo simples para resolver tarefa repetitiva."

    if "expensive" in titulo_lower or "pay for" in titulo_lower or "rob" in titulo_lower:
        chance_venda = "ALTA"
        proximo_passo = "Abordar destacando economia de custo."

    return {
        "potencial": potencial,
        "acao": acao,
        "monetizacao": monetizacao,
        "chance_venda": chance_venda,
        "proximo_passo": proximo_passo,
        "titulo": titulo
    }
