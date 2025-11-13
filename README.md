# Modelo de uma Aplicação Web com FastAPI

Template FastAPI seguindo princípios de Clean Architecture, SOLID e Programação Funcional com **Autenticação OAuth2 Agnóstica**.

## 🏗️ Arquitetura

Este projeto segue **Clean Architecture** com separação clara de responsabilidades:

- **`domain/`**: Entidades de negócio e regras empresariais (AuthenticatedUser, Token)
- **`application/`**: Casos de uso e lógica de aplicação (AuthenticationService, OAuth2Provider interface)
- **`infrastructure/`**: Frameworks, banco de dados e APIs (JWT provider, routes, dependencies)
- **`shared/`**: Utilitários compartilhados (logging, funcional, middleware)

Para mais detalhes, veja [ARCHITECTURE.md](./ARCHITECTURE.md).

## ✨ Características

- ✅ **Clean Architecture**: Separação clara de camadas e responsabilidades
- ✅ **SOLID Principles**: Código manutenível e extensível
- ✅ **OAuth2 Agnostic**: Funciona com qualquer provedor OAuth2 (Supabase, Firebase, Cognito, Auth0)
- ✅ **Dependency Injection**: Uso extensivo de DI do FastAPI
- ✅ **Pydantic**: Validação em todas as camadas
- ✅ **Functional Programming**: Either/Result monads para tratamento de erros
- ✅ **Type Hints**: Tipagem completa em todo o código
- ✅ **Structured Logging**: Logs estruturados com structlog
- ✅ **JWT Verification**: Verificação segura de tokens JWT
- ✅ **Role & Permission Based Access**: Controle de acesso por roles e permissões

## 🔐 Autenticação OAuth2

O template suporta autenticação OAuth2 de forma **agnóstica ao provedor**:

### Provedores Suportados
- Supabase
- Firebase
- AWS Cognito  
- Auth0
- Keycloak
- Qualquer provedor OAuth2 que use JWT

### Configuração

Configure as variáveis de ambiente:

```bash
OAUTH2_JWKS_URL=https://your-provider.com/.well-known/jwks.json
OAUTH2_ISSUER=https://your-provider.com
OAUTH2_AUDIENCE=your-audience  # Opcional
```

Veja [OAUTH2_SETUP.md](./OAUTH2_SETUP.md) para configuração detalhada de cada provedor.

### Endpoints Protegidos

```python
from app.infrastructure.api.dependencies import CurrentUserDep, require_roles

@router.get("/protected")
def protected_route(user: CurrentUserDep):
    return {"user": user.email}

@router.get("/admin")
def admin_route(
    user: CurrentUserDep,
    _: None = Depends(require_roles(['admin']))
):
    return {"message": "Admin only"}
```

## 📋 Requisitos

- Python >= 3.13
- PostgreSQL
- Poetry ou uv para gerenciamento de dependências

## Como executar

### Instalar dependências

```bash
make install
```

### Configurar OAuth2

1. Copie `.example.env` para `.env`
2. Configure as variáveis OAuth2:
   ```bash
   OAUTH2_JWKS_URL=<seu-provider>
   OAUTH2_ISSUER=<seu-issuer>
   ```

### Executar a aplicação
- Certifique-se de que o arquivo `.env` esteja configurado corretamente.
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
│   ├── auth/                        # Autenticação (AuthenticatedUser, Token)
│   ├── entities/                    # Entidades de domínio
│   ├── value_objects/               # Objetos de valor imutáveis
│   └── exceptions/                  # Exceções específicas do domínio
├── application/                     # Regras de Negócio da Aplicação
│   ├── auth/                        # AuthenticationService, OAuth2Provider interface
│   ├── use_cases/                   # Implementação de casos de uso
│   ├── ports/                       # Interfaces/Protocolos (DIP)
│   └── dtos/                        # Data Transfer Objects
├── infrastructure/                  # Frameworks & Drivers
│   ├── auth/                        # JWT provider implementation
│   ├── database/
│   │   ├── models.py                # Modelos SQLAlchemy
│   │   ├── session.py               # Gerenciamento de sessão
│   │   └── repositories/            # Implementações de repositórios
│   ├── api/                         # Adaptadores de Interface
│   │   ├── dependencies.py          # Injeção de dependências FastAPI
│   │   ├── routes/                  # Rotas da API
│   │   └── schemas/                 # Schemas Pydantic para API
│   └── config/
│       └── settings.py              # Configurações (inclui OAuth2)
├── shared/                          # Utilitários Compartilhados
│   ├── logging.py                   # Utilitários de logging
│   ├── middleware.py                # Middleware customizado
│   └── functional/                  # Utilitários de programação funcional
│       ├── either.py                # Result/Either monad
│       └── option.py                # Option/Maybe monad
└── core/                            # Constantes e enums
    └── constants.py
```

## 🚀 Exemplo de Uso com OAuth2

### Obter informações do usuário autenticado

```bash
curl -X GET "http://localhost:8000/api/v1/protected/me" \
  -H "Authorization: Bearer <seu-token-jwt>"
```

### Endpoint protegido por role

```bash
curl -X GET "http://localhost:8000/api/v1/protected/admin" \
  -H "Authorization: Bearer <seu-token-jwt-com-role-admin>"
```

### Endpoint protegido por permissão

```bash
curl -X GET "http://localhost:8000/api/v1/protected/write-data" \
  -H "Authorization: Bearer <seu-token-jwt-com-permissao-write>"
```

## 📚 Documentação da API

Após iniciar a aplicação, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Desenvolvimento

### Adicionar Nova Funcionalidade

1. **Domínio**: Crie entidades e value objects em `domain/`
2. **Aplicação**: Crie DTOs, portas e casos de uso em `application/`
3. **Infraestrutura**: Implemente repositórios e rotas em `infrastructure/`
4. **Testes**: Adicione testes para cada camada

Veja [ARCHITECTURE.md](./ARCHITECTURE.md) para detalhes completos.

### Configurar Provedor OAuth2 Customizado

Se você precisa de recursos específicos do provedor (como refresh de token), veja [OAUTH2_SETUP.md](./OAUTH2_SETUP.md#custom-provider-implementation).

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
result = auth_service.authenticate(token)
if isinstance(result, Success):
    user = result.unwrap()
elif isinstance(result, Failure):
    error = result.failure()
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

- [x] `/healthcheck` - Retorna o status da aplicação e banco de dados
- [x] `/api/v1/protected/me` - Informações do usuário autenticado
- [x] `/api/v1/protected/admin` - Endpoint protegido por role de admin
- [x] `/api/v1/protected/write-data` - Endpoint protegido por permissão

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
- [OAuth 2.0](https://oauth.net/2/)
- [JWT.io](https://jwt.io/)