<!-- SMART-MODEL-ROUTING:START -->
# Smart Model Routing & Guardrails de Engenharia (Codex CLI / AGENTS.md)

> Mantido por [smart-model-routing](https://github.com/LimaNathan/smart-model-routing). Preserve estes marcadores para permitir atualizações não-destrutivas.

## 1. Roteamento Inteligente de Modelos (`smart-model-routing`)

Opere com **Blindagem Estrita do Contexto Raiz**: mantenha a thread principal focada em arquitetura, especificações e síntese final, delegando execuções ruidosas, varreduras amplas e edições mecânicas para workers leves ou comandos filtrados.

### Princípio de Blindagem do Contexto Raiz
- **EVITE** despejar logs brutos de testes, saídas extensas de build ou payloads JSON volumosos na janela principal. Filtre saídas (`--quiet`, `--tb=short`) ou isole em sub-execuções.
- **SEMPRE** separe planejamento/arquitetura da geração mecânica de código e validação.

### Matriz de Delegação em 7 Casos Operacionais

| Caso | Tipo de Carga de Trabalho | Estratégia Codex / AGENTS.md | Modelo / Modo Recomendado | Contrato de Retorno |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Validação Estática, Linting, Testes e Builds** | Worker isolado / runner silencioso (`-q`, `--tb=short`) | Modelo rápido leve (`mini` / `nano`) | Retornar contagem pass/fail, testes que falharam e causa-raiz. |
| **2** | **Exploração, Varredura e Pesquisa no Codebase** | Worker somente-leitura / buscas direcionadas com `rg` | Modelo rápido leve (`mini`) | Retornar caminhos de arquivos, símbolos e resumo arquitetural. |
| **3** | **Implementação Mecânica e Boilerplate** | Worker de implementação (`codex exec`) | Modelo balanceado de código | Implementar seguindo contratos da raiz e validar localmente. |
| **4** | **Triagens Rápidas e Checagens Pontuais** | Checagem direta mínima (`git status -sb`, leitura única) | Modelo ultra-leve (`nano` / `mini`) | Resposta de fato único sem leituras extras. |
| **5** | **Integrações MCP e Serviços Externos** | Script ou worker de integração isolado | Modelo rápido leve (`mini`) | Filtrar payloads antes de devolver dados estruturados à raiz. |
| **6** | **Arquitetura, Planejamento e Decisões de Design** | Thread Orquestradora Principal | Modelo principal de raciocínio | Análise de trade-offs, design de specs e alinhamento com o usuário. |
| **7** | **Code Review Cego e Auditoria Cruzada de Diffs** | Auditoria cross-provider (`agy` / Claude / `codex review`) | Cross-Model Externo | Revisão imparcial de diffs por outro provedor antes do commit. |

---

## 2. Trava de Segurança de Deploy / Produção (`prod-deploy-safety`)

- **NUNCA** faça merge na `main`, push para a `main` ou dispare esteiras de release de produção com arquivos modificados ou não rastreados no repositório.
- **SEMPRE** execute `git status` antes e **PERGUNTE EXPLICITAMENTE** ao usuário antes de qualquer merge, push ou release em produção.

---

## 3. Protocolo de Continuidade de Sessão (`context-handoff`)

- Se `docs/CONTEXT_HANDOFF.md` existir, **LEIA-O IMEDIATAMENTE** ao iniciar uma nova sessão para restaurar contexto arquitetural, serviços/modelos ativos, tarefas pendentes e bloqueios.
- Atualize `docs/CONTEXT_HANDOFF.md` sempre que concluir evoluções técnicas relevantes.

---

## 4. Isolamento via Git Worktree (`worktree-isolation`)

- Isole features multi-escopo, branches paralelas ou refatorações arriscadas em uma Git worktree dedicada (`git worktree add`), validando os testes lá antes de integrar.
<!-- SMART-MODEL-ROUTING:END -->
