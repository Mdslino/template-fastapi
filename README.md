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
- [x] GET `/api/v1/auth/users` - Retorna todos os usuários cadastrados caso quem esteja requisitando seja um super usuário.
- [x] POST `/api/v1/auth/users` - Cria um novo usuário.
- [x] GET `/api/v1/auth/users/me` - Retorna os dados do usuário que está requisitando.
- [x] PATCH `/api/v1/auth/users/me` - Atualiza os dados do usuário que está requisitando.
- [x] PATCH `/api/v1/auth/users/{user_id}` - Atualiza os dados de um usuário específico.
- [x] POST `/api/v1/auth/token` - Gera um novo token de acesso.