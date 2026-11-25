# Post LinkedIn (PT-BR) — Kit de Lançamento

> **Notas de Publicação (Playbook `linkedin-devlog`)**:
> - **NÃO inclua links externos no corpo do post** — poste o link do repositório no primeiro comentário imediatamente após publicar.
> - **Janela recomendada**: Terça, Quarta ou Quinta às `08:30` ou `12:15` BRT.
> - **Acompanhamento visual**: anexe os 6 slides descritos em [CAROUSEL_SLIDES_BRIEF.md](CAROUSEL_SLIDES_BRIEF.md).

---

## Texto do Post (Pronto para Copiar)

Seu modelo frontier não ficou mais burro no meio da sessão.
Você só afogou a janela de contexto dele em 120 mil tokens de log de teste e dump de grep.

A cada turno de conversa com um agente de código, todo o histórico acumulado é reenviado. Quando um stack trace de 15k tokens ou um JSON bruto de MCP entra no chat principal, ele passa a ser cobrado e reprocessado em todos os turnos seguintes.

O custo não cresce linearmente. Cresce de forma quadrática — e o raciocínio arquitetural degrada junto.

Para resolver isso no meu fluxo diário, transformei uma regra que já usava em produção em um CLI open-source sem dependências externas: o Smart Model Routing (`smr`).

A ideia é simples: blindagem estrita do contexto raiz.

1. O modelo principal (`Pro` ou `Opus`) vira apenas arquiteto, orquestrador e interlocutor.
2. Logs de build, testes, buscas amplas, JSONs de MCP e edições repetitivas rodam em subagentes isolados (`Flash` / `Flash-Lite`), devolvendo só a causa-raiz em poucas linhas.
3. Antes do commit final, um revisor externo (`Codex CLI`) faz auditoria cega do diff — garantindo segunda opinião e diversificação de cotas.

Simulando uma sessão real de 15 turnos com o `smr benchmark`, o consumo acumulado no modelo principal caiu de 1,21M para 318k tokens — uma economia de 73,9% no contexto raiz.

O instalador é compatível com Antigravity, Claude Code, Codex CLI e Cursor, injeta regras de forma não-destrutiva com backup automático e ainda traz um comando `doctor` para auditar vazamentos acidentais de credenciais ou caminhos locais.

Deixei o link do repositório nos comentários.

Como vocês costumam separar o que vai para o modelo principal do que pode rodar em subagentes mais baratos no dia a dia?

#EngenhariaDeSoftware #AIAgents #ContextEngineering

---

## Primeiro Comentário (Publicar logo após o post)

Repositório open-source (zero dependências, Python 3.10+ stdlib):
https://github.com/LimaNathan/smart-model-routing

Inclui `smr install`, `smr uninstall`, `smr doctor` e `smr benchmark` para testar o impacto na janela de contexto no seu próprio terminal.
