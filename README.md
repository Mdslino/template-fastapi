# Modelo de uma Aplicação Web com FastAPI

## Como executar

### Instalar dependências

```bash
make install
```

### Executar a aplicação
- Certifique-se de que o arquivo `.example.env` esteja configurado corretamente.
- Execute o banco de dados com o comando `make run-db`.

```bash
make run
```

### Executar em Docker

```bash
make docker-run
```

### Executar os testes

Os testes utilizam [testcontainers](https://testcontainers.com/) para gerenciar automaticamente um container PostgreSQL. Isso significa que você não precisa ter um banco de dados rodando localmente - o testcontainer cuidará disso para você.

**Requisitos:**
- Docker deve estar instalado e rodando

```bash
make test
```

### Executar o linter

```bash
make lint
```

### Executar o formatter

```bash
make format-code
```

### Endpoints
- [x] `/healthcheck` - Retorna uma mensagem se a aplicação está funcionando.