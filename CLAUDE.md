# CLAUDE.md — sig-barbershop

## Contexto do Projeto

Sistema de gestão de barbearia — projeto acadêmico DIM0125 Banco de Dados, UFRN.
Apresentação: 08/07/2026. Time: 3 pessoas.
Monorepo: pasta raiz sig-barbershop com api/ e frontend/.

## Stack

- Backend: Python + FastAPI + Poetry, SQL puro (zero ORM)
- Frontend: Next.js 14+ (App Router) + TypeScript + Tailwind
- Banco: MySQL 8.0
- Infra: Docker + docker-compose
- Testes: pytest (backend)
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
└── frontend/ ← Next.js (ainda vazio)
├── src/
│ ├── app/
│ ├── components/
│ ├── lib/
│ └── types/
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

## Banco de Dados — 17 Tabelas

PESSOA, TELEFONE, CLIENTE, CAIXA, BARBEIRO,
DISPONIBILIDADE, SERVICO, HISTORICO_SERVICO,
ATENDIMENTO, ATENDIMENTO_SERVICO,
PRODUTO, HISTORICO_PRODUTO, COMPRA,
VENDA, VENDA_PRODUTO, FIDELIDADE, HISTORICO_PONTOS

## ENUMs

- DISPONIBILIDADE.dia_semana: segunda|terca|quarta|quinta|sexta|sabado|domingo
- ATENDIMENTO.status: agendado|em_andamento|concluido|cancelado
- VENDA.status: pendente|concluida|cancelada
- VENDA.forma_pagamento: dinheiro|cartao_debito|cartao_credito|pix
- HISTORICO_PONTOS.tipo_movimentacao: acumulo|resgate

## Pontos de Atenção no Banco

- FIDELIDADE: XOR entre PRODUTO_id_produto e SERVICO_id_servico
  → validar em fidelidade_service.py antes de qualquer INSERT
  → TRIGGER BEFORE INSERT/UPDATE garante no banco também
- ATENDIMENTO.valor_total e VENDA.valor_total são derivados
  → calculados e gravados pelo service, nunca pelo banco diretamente

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

## Divisão do Time

- Pessoa A: PESSOA / CLIENTE / BARBEIRO / CAIXA / DISPONIBILIDADE
- Pessoa B: ATENDIMENTO / ATENDIMENTO_SERVICO / SERVICO / HISTORICO_SERVICO
- Pessoa C: VENDA / VENDA_PRODUTO / PRODUTO / HISTORICO_PRODUTO / COMPRA / FIDELIDADE / HISTORICO_PONTOS

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
