# CLAUDE.md — sig-barbershop

## Contexto do Projeto

Sistema de gestão de barbearia — projeto acadêmico DIM0125 Banco de Dados, UFRN.
Apresentação: 08/07/2026. Time: 3 pessoas.
Monorepo: pasta raiz sig-barbershop com api/ e frontend/.

## Stack

- Backend: Python + FastAPI + Poetry, SQL puro (zero ORM)
- Frontend: Next.js 14+ (App Router) + TypeScript + Tailwind + shadcn/ui
- Banco: MySQL 8.0
- Infra: Docker + docker-compose
- Testes: pytest (backend) + Cypress (E2E frontend)
- CI: GitHub Actions

## Estrutura de Pastas

sig-barbershop/
├── CLAUDE.md
├── .github/
│ └── workflows/
│ ├── ci-api.yml
│ └── ci-frontend.yml
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
├── .gitignore
│
├── api/ ← FastAPI + Poetry (já iniciado)
│ ├── pyproject.toml ← já existe
│ ├── poetry.lock
│ ├── Dockerfile
│ ├── app/
│ │ ├── init.py
│ │ ├── main.py
│ │ ├── database.py ← pool de conexões MySQL
│ │ ├── dependencies.py ← get_db, auth
│ │ ├── routers/
│ │ ├── services/
│ │ ├── repositories/
│ │ ├── schemas/ ← Pydantic
│ │ └── db/
│ │ ├── schema.sql ← DDL completo
│ │ └── seed.sql
│ └── tests/
│ ├── conftest.py
│ ├── routers/
│ ├── services/
│ └── repositories/
│
└── frontend/ ← Next.js (App Router)
├── src/
│ ├── app/           ← rotas (App Router, Server Components por padrão)
│ ├── components/    ← componentes reutilizáveis e shadcn/ui
│ ├── services/      ← funções axios puras (sem React, sem hooks)
│ ├── hooks/         ← React Query hooks (useXxx wrapping services)
│ ├── lib/           ← axios.ts, queryClient.ts, utils.ts
│ └── types/         ← interfaces TypeScript
├── cypress/
│ ├── e2e/           ← testes E2E por módulo (clientes.cy.ts, etc.)
│ ├── support/       ← comandos customizados e configuração
│ └── fixtures/      ← dados estáticos para testes
├── Dockerfile
└── package.json

## Arquitetura em 3 Camadas (INVIOLÁVEL)

Router → Service → Repository

- **Router**: zero lógica. Recebe request, valida schema Pydantic, chama service, retorna.
- **Service**: regras de negócio, transações (commit/rollback), HTTPException, chama repository.
- **Repository**: SQL puro, cursor, fetchall/fetchone. Nunca lança HTTPException. Nunca controla transação.

## Regras que NUNCA quebram

- SQL no router → PROIBIDO
- HTTPException no repository → PROIBIDO
- Lógica de negócio no repository → PROIBIDO
- ORM de qualquer tipo → PROIBIDO
- Commit sem testes passando → PROIBIDO
- Novo endpoint sem teste → PROIBIDO
- Nova feature de frontend sem teste E2E Cypress → PROIBIDO
- Lógica de requisição HTTP dentro de componente React → PROIBIDO
- `useQuery` / `useMutation` direto no componente (sem hook customizado) → PROIBIDO

## Dependências Python (adicionar via Poetry)

- fastapi
- uvicorn[standard]
- mysql-connector-python
- pydantic
- python-dotenv
- pytest
- pytest-asyncio
- httpx (para testes de routers)
- ruff (linting)

## Banco de Dados — 16 Tabelas

PESSOA, TELEFONE, CLIENTE, CAIXA, BARBEIRO,
DISPONIBILIDADE, SERVICO, HISTORICO_SERVICO,
ATENDIMENTO, ATENDIMENTO_SERVICO,
PRODUTO, HISTORICO_PRODUTO,
VENDA, VENDA_PRODUTO, FIDELIDADE, HISTORICO_PONTOS

## ENUMs

- DISPONIBILIDADE.dia_semana: segunda|terca|quarta|quinta|sexta|sabado|domingo
- ATENDIMENTO.status: agendado|em_andamento|concluido|cancelado
- VENDA.status: pendente|concluida|cancelada
- VENDA.forma_pagamento: dinheiro|cartao_debito|cartao_credito|pix
- HISTORICO_PONTOS.tipo_movimentacao: acumulo|resgate

## Pontos de Atenção no Banco

- FIDELIDADE: categoria/union type de PRODUTO e SERVICO (feedback professor)
  → XOR entre PRODUTO_id_produto e SERVICO_id_servico no relacional
  → validar em fidelidade_service.py antes de qualquer INSERT
  → TRIGGER BEFORE INSERT/UPDATE garante no banco também
- HISTORICO_SERVICO e HISTORICO_PRODUTO possuem atributo `ativo` (feedback professor)
- VENDA_PRODUTO possui `preco_unitario` (feedback professor)
- COMPRA removida do modelo (feedback professor)
- ATENDIMENTO.valor_total e VENDA.valor_total são derivados
  → calculados e gravados pelo service, nunca pelo banco diretamente

## Padrões do Frontend

### Arquitetura em 3 Camadas (INVIOLÁVEL)

Service → Hook → Component

- **Service** (`services/`): função async pura que chama axios. Recebe parâmetros, retorna dado tipado. Zero React, zero hooks.
- **Hook** (`hooks/`): wrapper React Query sobre o service. Exporta `useXxx` com `useQuery` ou `useMutation`. Zero JSX.
- **Component**: consome o hook. Zero chamadas axios ou `useQuery` direta.

```
// services/clienteService.ts
export const getClientes = () => api.get<Cliente[]>('/clientes').then(r => r.data)

// hooks/useClientes.ts
export const useClientes = () => useQuery({ queryKey: ['clientes'], queryFn: getClientes })

// components/ClientesList.tsx
const { data, isLoading } = useClientes()
```

### Axios

- Instância única em `src/lib/axios.ts` com `baseURL = process.env.NEXT_PUBLIC_API_URL`
- Interceptor de response: erros 4xx/5xx normalizados antes de chegar ao hook
- Nunca importar axios diretamente nos componentes ou hooks — só nos services

### Formulários

- react-hook-form + zod em todos os formulários
- Schema zod define tipo e validação num único lugar
- Usar componentes `<Form>` do shadcn/ui (integração nativa com react-hook-form)

### Server vs Client Components

- Server Component por padrão (sem `'use client'`)
- `'use client'` apenas quando: usa hooks, event handlers, ou componentes shadcn com estado
- Nunca colocar chamadas de API diretamente em Server Components — usar hooks nos Client Components

### Cypress E2E

- Um arquivo `cypress/e2e/<modulo>.cy.ts` por módulo (ex: `clientes.cy.ts`, `atendimentos.cy.ts`)
- Testar o fluxo completo: renderizar página → interagir → verificar resultado
- Usar `cy.intercept()` para mockar respostas da API nos testes
- Comandos reutilizáveis em `cypress/support/commands.ts`
- Rodar com `pnpm cypress run` no CI

### Naming Conventions

- Componentes: PascalCase (`ClienteCard.tsx`)
- Hooks: `useXxx` (`useClientes.ts`)
- Services: camelCase com sufixo Service (`clienteService.ts`)
- Tipos: PascalCase interface (`Cliente`, `Atendimento`)

## Dependências npm (frontend)

- `@tanstack/react-query` — data fetching e cache
- `axios` — cliente HTTP
- `react-hook-form` — gerenciamento de formulários
- `zod` — validação de schemas
- `shadcn/ui` — componentes de UI (instalado via CLI: `npx shadcn@latest init`)
- `cypress` — testes E2E
- `prettier` — formatação de código

## Padrões de Código Python

- cursor(dictionary=True) em todos os SELECTs
- conn.start_transaction() sempre no service, nunca no repository
- repository recebe conn como parâmetro (nunca abre conexão própria)
- Erros de negócio → HTTPException no service
- Erros de banco → capturar no service, conn.rollback(), re-raise

## Processo (XP com IA — lição do Akita)

- Small releases: cada commit passa no CI antes de mergear
- TDD: testes junto com implementação, nunca depois
- Refactoring contínuo: sem funções > 30 linhas, sem arquivos > 200 linhas
- Humano decide o quê e o porquê. Claude decide o como.
- Ao fim de cada sessão: atualizar a seção Hurdles abaixo

## Git Workflow

- Nunca commitar direto na `main` → PROIBIDO
- Uma branch nova por issue, a partir da `main`: `feature/<numero-da-issue>-<slug>` (ex: `feature/12-historico-produto`)
- Ao concluir a implementação: abrir PR (`gh pr create`) referenciando a issue (`Closes #N`)
- Merge na `main` só depois do PR aberto e do CI passando

## Divisão do Time

- Pessoa A: PESSOA / CLIENTE / BARBEIRO / CAIXA / DISPONIBILIDADE
- Pessoa B: ATENDIMENTO / ATENDIMENTO_SERVICO / SERVICO / HISTORICO_SERVICO
- Pessoa C: VENDA / VENDA_PRODUTO / PRODUTO / HISTORICO_PRODUTO / FIDELIDADE / HISTORICO_PONTOS

## Ordem de Execução

1. [x] Scaffold Poetry (api/) — feito
2. [ ] Adicionar dependências via Poetry
3. [ ] schema.sql — DDL completo + ENUMs + TRIGGERs
4. [ ] docker-compose.yml — MySQL + api + frontend
5. [ ] Inicializar Next.js em frontend/
6. [ ] conftest.py — fixture de conexão de teste
7. [ ] GitHub repo + CI configurado
8. [ ] Issues criadas por módulo
9. [ ] Módulo CLIENTE completo com TDD (referência para os demais)

## Hurdles Conhecidos

(preencher conforme o desenvolvimento avança)
