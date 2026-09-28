# customer-service

Esta documentação reúne instruções detalhadas para rodar, configurar e depurar o serviço `customer-service`.

## Sumário
- Requisitos
- Rodando com Docker (recomendado)
- Rodando localmente (sem Docker)
- Variáveis de ambiente (`.env`)
- Makefile (atalhos)
- Testes
- Porta / endpoints
- Swagger / OpenAPI
- Autenticação
- Endpoints da aplicação

## Requisitos
- Docker e docker-compose (ou Docker Desktop)
- Python 3.12 (para executar localmente)
- Make (opcional)
- Poetry (opcional, se for instalar dependências localmente)

## Rodando com Docker (recomendado)
O serviço foi projetado para rodar em container. Para subir o ambiente com Docker Compose:

```sh
docker compose up --build
```

Ou use o atalho do Makefile:

```sh
make start-containers
```

Isso irá construir as imagens e iniciar os containers configurados no `docker-compose.yaml`.

## Rodando localmente (sem Docker)

1. Instale dependências e deixe o ambiente pronto usando Poetry. O Poetry cria e gerencia o virtual environment automaticamente:

```sh
poetry install
```

2. (Opcional) Abra um shell dentro do ambiente gerenciado pelo Poetry:

```sh
poetry shell
```

Ou execute comandos diretamente com `poetry run` sem ativar o shell:

```sh
poetry run uvicorn src.main:app --port 8081 --loop uvloop --reload
```

3. Crie um arquivo `.env` baseado no template (opcional):

```sh
make create-env
```

4. Inicie a aplicação (se não estiver usando `poetry run` diretamente):

```sh
make start
# ou
uvicorn src.main:app --port 8081 --loop uvloop --reload
```

> Observação: o `Makefile` valida a existência do `.env` antes de executar `start` e `start-containers`. Se ele não existir, o `make` exibirá o conteúdo de `.env.example` e abortará.

## Variáveis de ambiente (`.env`)
O projeto carrega variáveis usando `pydantic` em `src/infrastructure/config/settings.py`.
Por padrão, a configuração procura por `ENV_FILE` (se definida) ou `.env`.

Exemplo mínimo (valores de exemplo — não comitar segredos):

```env
PROJECT_NAME="customer-service"
DESCRIPTION="Customer Service API"
VERSION=1.0.0
DEBUG=false

ROOT_PATH=/customer-service

DATABASE_URL=postgresql+asyncpg://customer_service_user:customer_service_password@localhost:5432/customer_service_db
DATABASE_SCHEMA=favorites

PRODUCT_CLIENT_URL=https://fakestoreapi.com/

SERIALIZE_LOGS=true
LOG_LEVEL=INFO

JWT_SECRET_KEY=troque-por-uma-chave-secreta-longa
JWT_ALGORITHM=HS256
JWT_EXPIRES_MINUTES=60
```

As credenciais do `DATABASE_URL` são as criadas por `scripts/database/init.sql` no container do Postgres.

`JWT_SECRET_KEY` é obrigatória: sem ela a aplicação não inicia. Gere uma chave aleatória, por exemplo:

```sh
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Makefile (atalhos)
Os alvos úteis encontrados no `Makefile` são:

- `deps`: instala dependências via Poetry e instala pre-commit.
- `lint`: checa formatação e lint (black, flake8, isort, ruff).
- `format`: aplica formatação (isort, black, ruff --fix).
- `start`: roda a aplicação localmente (uvicorn) — valida `.env` antes.
- `start-containers`: sobe os containers com `docker compose up --build` — valida `.env` antes.
- `reload-volumes`: derruba os containers e remove volumes (`docker compose down --volumes`).
- `create-env`: copia `.env.example` para `.env` e pede revisão.

Use `make <target>` para executar qualquer um deles.

## Testes

Os testes ficam em `tests/` e rodam com pytest:

```sh
poetry run pytest
# com cobertura
poetry run pytest --cov=src
```

## Porta / Endpoints
- Porta padrão: `8081`.
- Health check: `GET /ready`.
- Rotas concretas em `src/interfaces/api`.

### Swagger / OpenAPI

A aplicação expõe a UI interativa do Swagger (FastAPI docs) e o JSON OpenAPI padrão:

- Swagger UI (interativo): `http://localhost:8081/docs`
- OpenAPI JSON: `http://localhost:8081/documentation`

Se você estiver usando `root_path` (definido em `settings.py` como `ROOT_PATH`), os caminhos podem incluir esse prefixo. Exemplo com `ROOT_PATH=/customer-service`:

- Swagger UI (com root_path): `http://localhost:8081/customer-service/docs`
- OpenAPI JSON (com root_path): `http://localhost:8081/customer-service/documentation`

Abra o Swagger para testar endpoints, ver schemas e experimentar requisições diretamente do navegador. Para as rotas `/v1`, clique em **Authorize** e cole o `access_token` obtido no login.

## Autenticação

Todas as rotas `/v1` exigem um token JWT no header `Authorization: Bearer <token>`. As rotas `/ready` e `/auth/login` são públicas.

O login usa um usuário fixo de demonstração, definido em `src/interfaces/api/auth/controller.py`:

- email: `user@example.com`
- senha: `senha123`

Exemplo:

```sh
TOKEN=$(curl -s -X POST http://localhost:8081/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "senha123"}' | jq -r .access_token)

curl http://localhost:8081/v1/customer/1 -H "Authorization: Bearer $TOKEN"
```

O token expira após `JWT_EXPIRES_MINUTES` (o campo `expires_in` da resposta vem em segundos). Requisições sem token, com token inválido ou expirado retornam `401 Unauthorized`.

### Endpoints da aplicação

Base path: `/`

Health Check (público)
 - GET /ready
	 - Response: `HealthCheckResponseSchema` { status_code: int, message: str }

Auth (público)
 - POST /auth/login
	 - Request: `LoginRequest` { email: string, password: string }
	 - Response: `TokenResponse` { access_token: string, token_type: string = "bearer", expires_in: int }
	 - Erro: 401 com credenciais inválidas

Customer (prefix `/v1`, requer token)
 - POST /v1/customer
	 - Description: Create a new customer
	 - Request: `CustomerRequestSchema` { name: string, email: string }
	 - Response: `CustomerResponseSchema` { customer_id: int, name?, email?, created_at?, updated_at? }

 - GET /v1/customer/{customer_id}
	 - Description: Get a customer by ID
	 - Path param: `customer_id` (int)
	 - Response: `CustomerResponseSchema`

 - PATCH /v1/customer/{customer_id}
	 - Description: Update a customer by ID
	 - Request: `CustomerRequestSchema`
	 - Response: `CustomerResponseSchema`

 - DELETE /v1/customer/{customer_id}
	 - Description: Delete a customer by ID
	 - Response: 204 No Content

Favorite (prefix `/v1`, requer token)
 - POST /v1/customer/{customer_id}/favorite
	 - Description: Add a favorite item for a customer
	 - Request: `FavoriteRequestSchema` { product_id: int }
	 - Response: `FavoriteResponseSchema` { message: "Favorite item added successfully" }

 - GET /v1/customer/{customer_id}/favorites
	 - Description: Get all favorite items for a customer
	 - Response: `FavoritesResponseSchema` { customer_id: int, favorites: list[ProductFavoriteSchema] }
