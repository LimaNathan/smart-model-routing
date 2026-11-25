# Context Handoff do Projeto

> Documento vivo de continuidade lido no início de cada sessão de engenharia com IA e atualizado sempre que o estado técnico evoluir.

- **Projeto**: `<nome-do-projeto>`
- **Última Atualização**: `YYYY-MM-DD`
- **Branch / Marco Ativo**: `<branch-ou-release>`

---

## 1. Decisões Arquiteturais (Architecture Decisions)

Registre escolhas técnicas, trade-offs e invariantes para evitar retrabalho ou rediscussão de decisões já consolidadas.

- **[ADR-001]** `<Título da decisão>` — `<Contexto, abordagem escolhida e justificativa>`
- **[ADR-002]** `<Título da decisão>` — `<Contexto, abordagem escolhida e justificativa>`

---

## 2. Estado Atual (Current State)

Fotografia objetiva do que está funcionando, publicado ou em andamento.

- **Stack / Runtime Principal**: `<ex.: Python 3.12 + FastAPI / React 19 / PostgreSQL 16>`
- **Saúde de Build & Testes**: `<ex.: Testes unitários passando (142/142); E2E aguardando atualização de seed>`
- **Marcos Recentes**:
  - `<Feature ou refatoração concluída>`

---

## 3. Modelos e Serviços Ativos (Active Models & Services)

Acompanhe serviços em execução, workers, pipelines de dados ou modelos e suas versões atuais.

| Componente | Versão / Tag | Status | Notas |
| :--- | :--- | :--- | :--- |
| `<api-service>` | `v1.x.y` | `Saudável` | `<Nota de porta, config ou dependência>` |
| `<worker-queue>` | `v1.x.y` | `Ativo` | `<Nota de concorrência ou agendamento>` |

---

## 4. Tarefas Pendentes (Pending Tasks)

Backlog priorizado para as próximas sessões.

- [ ] `<Próxima tarefa prioritária com ponteiro exato de arquivo/módulo>`
- [ ] `<Tarefa complementar>`
- [ ] `<Item de validação ou documentação>`

---

## 5. Bloqueios e Riscos Conhecidos (Known Blockers & Risks)

Documente peculiaridades de ambiente, dependências externas ou casos de borda que exigem atenção.

- **Bloqueio / Risco**: `<Descrição>` — **Mitigação / Responsável**: `<Próximo passo>`

---

## 6. Log da Última Sessão (Last Session Log)

- **Data**: `YYYY-MM-DD`
- **Resumo das Alterações**:
  - `<O que foi implementado, corrigido ou validado>`
- **Validações Executadas**:
  - `<Comando exato de teste/lint e resultado observado>`
- **Próximo Passo Imediato**:
  - `<Ponto de partida mais claro para a próxima sessão>`
