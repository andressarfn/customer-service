# customer-service

Serviço de clientes e produtos favoritos, dividido em duas aplicações:

| Pasta                    | Conteúdo                                                   |
|--------------------------|------------------------------------------------------------|
| [`backend/`](backend/)   | API em FastAPI + PostgreSQL, com autenticação JWT          |
| [`frontend/`](frontend/) | Interface web (em construção)                              |

## Rodando

Com o Docker Desktop aberto, a partir da raiz do repositório:

```sh
docker compose up --build
```

A API sobe na porta `8081` e o Swagger fica em `http://localhost:8081/docs`.

Antes da primeira execução, crie o `.env` do backend:

```sh
cd backend && make create-env
```

Instruções detalhadas (variáveis de ambiente, execução sem Docker, testes, autenticação e endpoints) estão no [README do backend](backend/README.md).
