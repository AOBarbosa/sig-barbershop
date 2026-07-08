# SIG Barbershop

Sistema academico de gestao de barbearia com frontend Next.js, backend FastAPI e banco MySQL.

## Requisitos

- Docker e Docker Compose
- Git
- Node.js e pnpm apenas se for rodar o frontend fora do Docker
- Python 3.14 e Poetry apenas se for rodar a API fora do Docker

## Modo recomendado para apresentacao

Este foi o modo validado localmente para apresentar o projeto:

- MySQL e API pelo Docker
- Frontend em modo producao local

Na raiz do projeto, suba banco e API:

```bash
git checkout main
git pull --ff-only origin main
docker compose -f docker-compose.dev.yml up --build db api
```

Em outro terminal, suba o frontend:

```bash
cd frontend
pnpm install
NEXT_PUBLIC_API_URL=http://localhost:8000 pnpm build
NEXT_PUBLIC_API_URL=http://localhost:8000 pnpm start
```

Depois acesse:

- Pagina publica: `http://localhost:3000`
- Painel interno: `http://localhost:3000/app`
- Login: `http://localhost:3000/login`
- Documentacao da API: `http://localhost:8000/docs`
- Health check da API: `http://localhost:8000/health`

## Rodar tudo com Docker em modo desenvolvimento

Na raiz do projeto:

```bash
git checkout main
git pull --ff-only origin main
docker compose -f docker-compose.dev.yml up --build
```

O Docker sobe:

- MySQL 8.0 em `localhost:3306`
- API FastAPI em `http://localhost:8000`
- Frontend Next.js em `http://localhost:3000`

Observacao: em alguns ambientes macOS, o servidor de desenvolvimento do Next dentro do Docker pode demorar muito para compilar as primeiras rotas por causa do volume montado. Para apresentar, prefira o modo recomendado acima.

URLs principais:

- Pagina publica: `http://localhost:3000`
- Painel interno: `http://localhost:3000/app`
- Login: `http://localhost:3000/login`
- Documentacao da API: `http://localhost:8000/docs`
- Health check da API: `http://localhost:8000/health`

## Credenciais de desenvolvimento

O arquivo `api/app/db/seed.sql` cria usuarios para teste local:

| Perfil | Email | Senha |
| --- | --- | --- |
| Admin | `roberto@email.com` | `admin123` |
| Funcionario | `marcos@email.com` | `func123` |
| Cliente | `carlos@email.com` | `cliente123` |

## Variaveis de ambiente

O projeto possui `.env.example` com os valores padrao:

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=sig_barbershop
DB_USER=barbershop
DB_PASSWORD=barbershop
DB_ROOT_PASSWORD=rootpassword
API_PORT=8000
JWT_SECRET=troque-por-um-segredo-forte-em-producao
JWT_EXPIRE_MINUTES=60
FRONTEND_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Para uso local com Docker, nao e obrigatorio criar `.env`, porque o `docker-compose.dev.yml` ja define valores padrao. Se precisar customizar portas ou senhas:

```bash
cp .env.example .env
```

## Resetar banco de dados

Use este comando quando quiser apagar os dados locais e recriar tudo a partir de `schema.sql` e `seed.sql`:

```bash
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up --build
```

## Rodar testes

Backend:

```bash
cd api
poetry install
poetry run pytest
```

Frontend:

```bash
cd frontend
pnpm install
pnpm lint
pnpm format:check
pnpm build
pnpm cypress:run --config baseUrl=http://localhost:3000
```

## Rodar sem Docker

Banco MySQL:

- Crie o banco `sig_barbershop`.
- Execute `api/app/db/schema.sql`.
- Execute `api/app/db/seed.sql`.
- Configure as variaveis do `.env`.

API:

```bash
cd api
poetry install
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Frontend:

```bash
cd frontend
pnpm install
NEXT_PUBLIC_API_URL=http://localhost:8000 pnpm dev
```

## Portas usadas

- `3000`: frontend
- `8000`: API
- `3306`: MySQL

Se alguma porta estiver ocupada, veja o processo:

```bash
lsof -nP -iTCP:3000 -sTCP:LISTEN
lsof -nP -iTCP:8000 -sTCP:LISTEN
lsof -nP -iTCP:3306 -sTCP:LISTEN
```

Depois encerre o processo pelo PID:

```bash
kill <PID>
```

Se o processo nao encerrar:

```bash
kill -9 <PID>
```


## Arquitetura resumida

Backend:

- FastAPI
- MySQL com SQL puro
- Sem ORM
- Camadas: Router -> Service -> Repository

Frontend:

- Next.js App Router
- TypeScript
- Tailwind CSS e shadcn/ui
- Camadas: Service -> Hook -> Component
