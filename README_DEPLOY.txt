DEMAND HUNTER DEPLOY 1.0

O que foi preparado:
- Projeto limpo, sem backups e sem cache.
- Compatível com Render.
- Link temporário muda nos períodos de 08h, 14h e 20h.
- O link antigo deixa de abrir o painel quando o período muda.
- Página administrativa gera a mensagem pronta para copiar no grupo.

NO RENDER
1. Envie todos estes arquivos ao GitHub.
2. No Render, crie um Web Service conectado ao repositório.
3. Build Command: pip install -r requirements.txt
4. Start Command: gunicorn dashboard:app
5. Adicione BASE_URL com o endereço recebido no Render, por exemplo:
   https://demand-hunter.onrender.com
6. ACCESS_SECRET e ADMIN_KEY podem ser gerados automaticamente pelo render.yaml.

COMO PEGAR O LINK ATUAL
Abra:
https://SEU-ENDERECO.onrender.com/admin/link?chave=SUA_ADMIN_KEY

A tela devolverá:
- o link temporário atual;
- a mensagem pronta para copiar e colar no grupo.

IMPORTANTE
Guarde ADMIN_KEY somente com você. Não publique essa chave no grupo.
