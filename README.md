# Modelo de uma Aplicação Web com FastAPI

Template FastAPI seguindo princípios de Clean Architecture, SOLID e Programação Funcional.

## 🏗️ Arquitetura

Este projeto segue **Clean Architecture** com separação clara de responsabilidades:

- **`domain/`**: Entidades de negócio e regras empresariais
- **`application/`**: Casos de uso e lógica de aplicação
- **`infrastructure/`**: Frameworks, banco de dados e APIs
- **`shared/`**: Utilitários compartilhados (logging, funcional, middleware)

Para mais detalhes, veja [ARCHITECTURE.md](./ARCHITECTURE.md).

## ✨ Características

- ✅ **Clean Architecture**: Separação clara de camadas e responsabilidades
- ✅ **SOLID Principles**: Código manutenível e extensível
- ✅ **Dependency Injection**: Uso extensivo de DI do FastAPI
- ✅ **Pydantic**: Validação em todas as camadas
- ✅ **Functional Programming**: Either/Result monads para tratamento de erros
- ✅ **Type Hints**: Tipagem completa em todo o código
- ✅ **Structured Logging**: Logs estruturados com structlog
- ✅ **FastAPI**: Framework moderno e rápido
- ✅ **SQLAlchemy**: ORM poderoso para banco de dados
- ✅ **Alembic**: Migrações de banco de dados

## 📋 Requisitos

- Python >= 3.13
- PostgreSQL
- Poetry ou uv para gerenciamento de dependências

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

## 📁 Estrutura do Projeto

```
app/
├── domain/                          # Regras de Negócio Empresariais
│   ├── entities/                    # Entidades de domínio
│   ├── value_objects/               # Objetos de valor imutáveis
│   └── exceptions/                  # Exceções específicas do domínio
├── application/                     # Regras de Negócio da Aplicação
│   ├── use_cases/                   # Implementação de casos de uso
│   ├── ports/                       # Interfaces/Protocolos (DIP)
│   └── dtos/                        # Data Transfer Objects
├── infrastructure/                  # Frameworks & Drivers
│   ├── database/
│   │   ├── models.py                # Modelos SQLAlchemy
│   │   ├── session.py               # Gerenciamento de sessão
│   │   └── repositories/            # Implementações de repositórios
│   ├── api/                         # Adaptadores de Interface
│   │   ├── dependencies.py          # Injeção de dependências FastAPI
│   │   ├── routes/                  # Rotas da API
│   │   └── schemas/                 # Schemas Pydantic para API
│   └── config/
│       └── settings.py              # Configurações
├── shared/                          # Utilitários Compartilhados
│   ├── logging.py                   # Utilitários de logging
│   ├── middleware.py                # Middleware customizado
│   └── functional/                  # Utilitários de programação funcional
│       ├── either.py                # Result/Either monad
│       └── option.py                # Option/Maybe monad
└── core/                            # Constantes e enums
    └── constants.py
```

## 🚀 Exemplo de Uso

### Criar um Usuário

```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe"
  }'
```

### Listar Usuários

```bash
curl "http://localhost:8000/api/v1/users/"
```

### Buscar Usuário por ID

```bash
curl "http://localhost:8000/api/v1/users/{user_id}"
```

## 📚 Documentação da API

Após iniciar a aplicação, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testes

O projeto inclui testes para:
- Entidades de domínio
- Casos de uso
- Endpoints da API

Execute os testes com:

```bash
make test
```

## 🔧 Desenvolvimento

### Adicionar Nova Funcionalidade

1. **Domínio**: Crie entidades e value objects em `domain/`
2. **Aplicação**: Crie DTOs, portas e casos de uso em `application/`
3. **Infraestrutura**: Implemente repositórios e rotas em `infrastructure/`
4. **Testes**: Adicione testes para cada camada

Veja [ARCHITECTURE.md](./ARCHITECTURE.md) para detalhes completos.

### Princípios SOLID

- **S**ingle Responsibility: Cada classe tem uma única responsabilidade
- **O**pen/Closed: Aberto para extensão, fechado para modificação
- **L**iskov Substitution: Interfaces podem ser substituídas por implementações
- **I**nterface Segregation: Interfaces pequenas e focadas
- **D**ependency Inversion: Dependa de abstrações, não de concretude

### Programação Funcional

O projeto usa monads para tratamento de erros:

```python
# Either monad para operações que podem falhar
result = use_case.execute(dto)
if isinstance(result, Success):
    user = result.unwrap()
elif isinstance(result, Failure):
    error = result.failure()

# Option monad para valores opcionais
user_option = repository.find_by_id(user_id)
if user_option == Nothing:
    # Usuário não encontrado
```

## 📝 Migrações de Banco de Dados

### Criar uma migração

```bash
make migration m="descrição da migração"
```

### Aplicar migrações

```bash
make migrate
```

### Reverter última migração

```bash
make migrate-down
```

## Endpoints

- [x] `/healthcheck` - Retorna uma mensagem se a aplicação está funcionando
- [x] `/api/v1/users/` - CRUD de usuários (POST, GET, GET by ID)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

## 📚 Recursos Adicionais

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [returns Library](https://returns.readthedocs.io/)