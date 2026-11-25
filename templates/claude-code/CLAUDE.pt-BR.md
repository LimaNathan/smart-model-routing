<!-- SMART-MODEL-ROUTING:START -->
# Smart Model Routing & Guardrails de Engenharia (Claude Code)

> Mantido por [smart-model-routing](https://github.com/LimaNathan/smart-model-routing). Preserve estes marcadores para permitir atualizações não-destrutivas.

## 1. Roteamento Inteligente de Modelos (`smart-model-routing`)

A sessão raiz do Claude Code atua **estritamente como Arquiteto, Orquestrador e Interlocutor**, protegendo a janela de contexto principal contra saturação de tokens e perda de precisão.

### Princípio de Blindagem do Contexto Raiz
- **NUNCA** execute suítes de testes verbosas, logs extensos de build, buscas amplas ou dumps JSON de MCP diretamente na thread principal quando um subagente puder isolar o I/O.
- **SEMPRE** dispare subagentes via ferramenta `Task` (`model: "haiku"` ou `"sonnet"`), mantendo apenas resumos objetivos e acionáveis na sessão raiz.

### Matriz de Delegação em 7 Casos Operacionais

| Caso | Tipo de Carga de Trabalho | Delegação no Claude Code | Tier de Modelo | Contrato de Retorno ao Raiz |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Validação Estática, Linting, Testes e Builds** (linters, type-checkers, test runners, compilações) | Subagente `Task` (Bash/runner) | `haiku` | Suprimir ruído de sucesso; retornar status, falhas exatas e causa-raiz. |
| **2** | **Exploração, Varredura e Pesquisa no Codebase** (rastreamento multi-arquivo, busca de símbolos) | `Task` (`subagent_type: "Explore"`) | `haiku` | Varredura somente-leitura retornando caminhos de arquivo, relações e conclusões. |
| **3** | **Implementação Mecânica e Boilerplate** (models, DTOs, schemas, mappers, migrations, testes) | `Task` (`subagent_type: "general-purpose"`) | `sonnet` | Raiz define contratos e restrições; subagente implementa e valida localmente. |
| **4** | **Triagens Rápidas e Checagens Pontuais** (git status, branch atual, leitura única de config/versão) | Subagente `Task` | `haiku` | Resposta mínima de fato único e baixíssima latência. |
| **5** | **Integrações MCP e Serviços Externos** (trackers, Figma, APIs REST/GraphQL, webhooks) | Subagente `Task` | `haiku` | Absorver payloads JSON extensos no subagente; retornar apenas fatos estruturados. |
| **6** | **Arquitetura, Planejamento e Decisões de Design** (specs, trade-offs, decomposição, síntese) | Sessão Raiz | `opus` / `sonnet` | Raciocínio profundo, alinhamento de plano e comunicação clara com o usuário. |
| **7** | **Code Review Cego e Auditoria Cruzada de Diffs** (revisão pré-commit, segunda opinião algorítmica) | CLI Externa (`codex review` ou `agy`) | Cross-Model Externo | Auditoria imparcial de outra família de modelos antes de commitar. |

---

## 2. Trava de Segurança de Deploy / Produção (`prod-deploy-safety`)

- **NUNCA** faça merge, push ou dispare releases para produção (branch `main`, tags de release ou esteiras de deploy) enquanto houver arquivos modificados ou não rastreados na árvore de trabalho.
- **SEMPRE** verifique `git status` antes e **PERGUNTE EXPLICITAMENTE** ao usuário por autorização antes de realizar merge na `main`, push para a `main` ou disparo de build/release de produção.

---

## 3. Protocolo de Continuidade de Sessão (`context-handoff`)

- Se `docs/CONTEXT_HANDOFF.md` existir no repositório, **LEIA-O IMEDIATAMENTE** no início da sessão para carregar decisões arquiteturais, serviços ativos, tarefas pendentes e bloqueios.
- Atualize `docs/CONTEXT_HANDOFF.md` sempre que o estado técnico evoluir de forma significativa durante a sessão.

---

## 4. Isolamento via Git Worktree (`worktree-isolation`)

- Para features multi-escopo ou refatorações paralelas arriscadas, delegue via `Task` com `isolation: "worktree"` (ou use `templates/agents/worktree-agent.pt-BR.md`) para que edições e testes rodem em uma worktree isolada sem sujar a branch principal.
<!-- SMART-MODEL-ROUTING:END -->
