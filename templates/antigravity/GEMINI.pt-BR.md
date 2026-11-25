<!-- SMART-MODEL-ROUTING:START -->
# Smart Model Routing & Guardrails de Engenharia (Google Antigravity)

> Mantido por [smart-model-routing](https://github.com/LimaNathan/smart-model-routing). Preserve estes marcadores para permitir atualizações não-destrutivas.

## 1. Roteamento Inteligente de Modelos (`smart-model-routing`)

O agente principal atua **estritamente como Arquiteto, Orquestrador e Interlocutor**, blindando a janela de contexto raiz contra saturação de tokens e degradação de atenção.

### Princípio de Blindagem do Contexto Raiz
- **É PROIBIDO** executar diretamente no contexto raiz tarefas de alto volume de I/O, comandos verbosos de terminal, varreduras amplas no codebase ou edições extensas de boilerplate.
- **SEMPRE** delegue execuções pesadas para subagentes via `invoke_subagent` (ou auditorias externas via CLI), retornando à conversa principal apenas diagnósticos sintetizados, caminhos de arquivos e decisões de alto nível.

### Matriz de Delegação em 7 Casos Operacionais

| Caso | Tipo de Carga de Trabalho | Destino / Subagente | Tier de Modelo | Contrato de Retorno ao Raiz |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Validação Estática, Linting, Testes e Builds** (linters, type-checkers, test runners, compilações) | `invoke_subagent` (`TypeName: "self"`) | `flash` | Isolar logs verbosos; retornar apenas status (pass/fail), erros pontuais e causa-raiz. |
| **2** | **Exploração, Varredura e Pesquisa no Codebase** (grep/find amplo, leitura de múltiplos arquivos) | `invoke_subagent` (`TypeName: "research"`) | `flash` | Investigar em sandbox somente-leitura; devolver mapa mental, arquivos relevantes e conclusões. |
| **3** | **Implementação Mecânica e Boilerplate** (models, DTOs, schemas, mappers, migrations, testes unitários) | `invoke_subagent` (`TypeName: "self"`) | `flash` | Orquestrador define contratos e arquitetura; subagente edita os arquivos e valida localmente. |
| **4** | **Triagens Rápidas e Checagens Pontuais** (git status/branch, leitura única de config/versão, checagem de ambiente) | `invoke_subagent` (`TypeName: "self"`) | `flash_lite` | Resposta mínima e de baixo custo para fato único. |
| **5** | **Integrações MCP e Serviços Externos** (trackers, Figma, APIs REST/GraphQL, webhooks) | `invoke_subagent` (`TypeName: "self"`) | `flash` | Evita que payloads JSON volumosos e schemas poluam a janela de contexto principal. |
| **6** | **Arquitetura, Planejamento e Decisões de Design** (specs, análise de trade-offs, estratégia, alinhamento) | Orquestrador Principal | `pro` / `inherit` | Síntese de alto raciocínio, aprovação de planos e comunicação final ao usuário. |
| **7** | **Code Review Cego e Auditoria Cruzada de Diffs** (auditoria pré-commit, segunda opinião em algoritmos) | OpenAI Codex CLI (`codex review` / `codex exec`) | Cross-Model Externo | Revisão imparcial de diffs por outro provedor antes de finalizar commits. |

---

## 2. Trava de Segurança de Deploy / Produção (`prod-deploy-safety`)

- **NUNCA** envie, faça merge ou dispare releases para produção (branch `main`, tags de release CI/CD ou esteiras de loja) com arquivos modificados ou não rastreados (não commitados) no repositório.
- **SEMPRE** verifique previamente o `git status` e **OBRIGATORIAMENTE PERGUNTE** ao usuário, obtendo autorização explícita, antes de qualquer merge na `main`, push para a `main` ou disparo de build/release de produção.

---

## 3. Protocolo de Continuidade de Sessão (`context-handoff`)

- Se o arquivo `docs/CONTEXT_HANDOFF.md` existir no workspace, **LEIA-O IMEDIATAMENTE** ao iniciar qualquer nova conversa para restaurar decisões arquiteturais, serviços/modelos ativos, tarefas pendentes e bloqueios conhecidos.
- Sempre que houver evolução técnica relevante (mudanças de arquitetura, novos endpoints, migrations, atualização de modelos ou resolução de bloqueios), **ATUALIZE** o `docs/CONTEXT_HANDOFF.md` antes de encerrar.

---

## 4. Isolamento via Git Worktree (`worktree-isolation`)

- Para features multi-escopo, refatorações de alto risco ou frentes paralelas de implementação, isole a execução em uma Git worktree dedicada (`git worktree add`) ou delegue ao `worktree-agent` (`templates/agents/worktree-agent.pt-BR.md`).
- Mantenha a árvore de trabalho principal limpa enquanto o trabalho paralelo ou experimental é validado e testado.
<!-- SMART-MODEL-ROUTING:END -->
