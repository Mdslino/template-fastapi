# Practical Usage Examples - Auth0 Authentication

This document provides practical examples of how to use the authentication module in different scenarios.

## Scenario 1: Public and Protected Endpoints

```python
from fastapi import APIRouter
from app.auth.dependencies import CurrentUserDep

router = APIRouter(prefix='/products', tags=['products'])

@router.get('/')
def list_products():
    """Public endpoint - anyone can access."""
    return {'products': ['Product 1', 'Product 2']}

@router.get('/{product_id}')
def get_product(product_id: int, user: CurrentUserDep):
    """Protected endpoint - requires authentication."""
    return {
        'product_id': product_id,
        'accessed_by': user.user_id
    }
```

## Scenario 2: CRUD with Different Permission Levels

```python
from typing import Annotated
from fastapi import APIRouter, Depends
from app.auth.dependencies import CurrentUserDep, RequirePermissions
from app.auth.schemas import AuthenticatedUser

router = APIRouter(prefix='/articles', tags=['articles'])

# Permissions
require_read = RequirePermissions(['read:articles'])
require_write = RequirePermissions(['write:articles'])
require_delete = RequirePermissions(['delete:articles'])

@router.get('/')
def list_articles(user: Annotated[AuthenticatedUser, Depends(require_read)]):
    """List articles - requires read permission."""
    return {'articles': []}

@router.post('/')
def create_article(
    data: dict,
    user: Annotated[AuthenticatedUser, Depends(require_write)]
):
    """Create article - requires write permission."""
    return {'message': 'Article created', 'author': user.user_id}

@router.delete('/{article_id}')
def delete_article(
    article_id: int,
    user: Annotated[AuthenticatedUser, Depends(require_delete)]
):
    """Delete article - requires delete permission."""
    return {'message': 'Article deleted'}
```

## Scenario 3: Conditional Permissions

```python
from fastapi import APIRouter, HTTPException
from app.auth.dependencies import CurrentUserDep

router = APIRouter(prefix='/posts', tags=['posts'])

@router.patch('/{post_id}')
def update_post(post_id: int, data: dict, user: CurrentUserDep):
    """
    Update post - user can edit their own posts
    or any post if they have admin permission.
    """
    # Fetch post from database
    post = get_post_from_db(post_id)  # dummy function

    # Check if user is author or has admin permission
    is_author = post.author_id == user.user_id
    is_admin = user.has_permission('admin:write')

    if not (is_author or is_admin):
        raise HTTPException(
            status_code=403,
            detail='You can only edit your own posts'
        )

    # Update post
    return {'message': 'Post updated'}
```

## Scenario 4: Hierarchical Permissions

```python
from fastapi import APIRouter
from app.auth.dependencies import CurrentUserDep

router = APIRouter(prefix='/users', tags=['users'])

@router.get('/{user_id}/profile')
def get_user_profile(user_id: str, current_user: CurrentUserDep):
    """
    View profile - different access levels
    based on permissions.
    """
    profile = get_profile_from_db(user_id)  # dummy function

    # Admin sees everything
    if current_user.has_permission('admin:read'):
        return profile  # Complete profile

    # User sees their own complete profile
    if current_user.user_id == user_id:
        return profile

    # Others see public profile
    return {
        'name': profile['name'],
        'bio': profile['bio']
    }
```

## Scenario 5: Multiple Permissions (AND)

```python
from typing import Annotated
from fastapi import APIRouter, Depends
from app.auth.dependencies import RequirePermissions
from app.auth.schemas import AuthenticatedUser

router = APIRouter(prefix='/reports', tags=['reports'])

# Requires ALL listed permissions
require_full_access = RequirePermissions([
    'read:reports',
    'export:reports',
    'sensitive:data'
])

@router.get('/financial')
def get_financial_report(
    user: Annotated[AuthenticatedUser, Depends(require_full_access)]
):
    """
    Financial report - requires multiple permissions.
    """
    return {'report': 'Financial data...'}
```

## Scenario 6: Alternative Permissions (OR)

```python
from fastapi import APIRouter, HTTPException
from app.auth.dependencies import CurrentUserDep

router = APIRouter(prefix='/content', tags=['content'])

@router.post('/{content_id}/approve')
def approve_content(content_id: int, user: CurrentUserDep):
    """
    Approve content - can be done by editor or admin.
    """
    # User needs AT LEAST ONE of the permissions
    if not user.has_any_permission(['editor:approve', 'admin:write']):
        raise HTTPException(
            status_code=403,
            detail='Only editors and admins can approve content'
        )

    return {'message': 'Content approved'}
```

## Scenario 7: Integration with Services

```python
# app/articles/services/create_article.py
from sqlalchemy.orm import Session
from app.articles.models import Article
from app.articles.schemas import ArticleCreate
from app.auth.schemas import AuthenticatedUser

class CreateArticleService:
    def __init__(self, db: Session):
        self.db = db

    def execute(
        self,
        data: ArticleCreate,
        author: AuthenticatedUser
    ) -> Article:
        """Create article with author information."""
        article = Article(
            **data.model_dump(),
            author_id=author.user_id
        )
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article

# app/articles/routes.py
from app.articles.dependencies import CreateArticleServiceDep
from app.auth.dependencies import CurrentUserDep, RequirePermissions

@router.post('/')
def create_article(
    data: ArticleCreate,
    user: Annotated[AuthenticatedUser, Depends(RequirePermissions(['write:articles']))],
    service: CreateArticleServiceDep
):
    """Create article with authenticated author."""
    article = service.execute(data, author=user)
    return ArticleResponse.model_validate(article)
```

## Scenario 8: Audit Logs

```python
import structlog
from fastapi import APIRouter
from app.auth.dependencies import CurrentUserDep

logger = structlog.get_logger()
router = APIRouter(prefix='/admin', tags=['admin'])

@router.delete('/users/{user_id}')
def delete_user(
    user_id: str,
    admin: Annotated[AuthenticatedUser, Depends(RequirePermissions(['admin:delete']))]
):
    """Delete user with audit trail."""
    logger.info(
        'User deletion requested',
        target_user_id=user_id,
        admin_user_id=admin.user_id,
        admin_permissions=admin.permissions
    )

    # Deletion logic
    delete_user_from_db(user_id)

    logger.warning(
        'User deleted',
        deleted_user_id=user_id,
        deleted_by=admin.user_id
    )

    return {'message': 'User deleted successfully'}
```

## Scenario 9: Testing with Authentication

```python
# tests/endpoints/test_articles.py
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from jose import jwt

def create_test_token(permissions):
    """Helper to create test tokens."""
    payload = {
        'sub': 'auth0|test-user',
        'permissions': permissions,
        'iss': 'https://test.auth0.com/',
        'aud': 'https://api.example.com',
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow(),
    }

    # Use test keys
    private_key = get_test_private_key()  # dummy function

    return jwt.encode(
        payload,
        private_key,
        algorithm='RS256',
        headers={'kid': 'test-key-id'}
    )

def test_create_article_with_permission(client, jwks_mock):
    """Test with proper permission."""
    token = create_test_token(['write:articles'])

    with patch('httpx.get') as mock_get:
        mock_get.return_value.json.return_value = jwks_mock

        response = client.post(
            '/api/v1/articles/',
            json={'title': 'Test Article', 'content': '...'},
            headers={'Authorization': f'Bearer {token}'}
        )

    assert response.status_code == 201

def test_create_article_without_permission(client, jwks_mock):
    """Test without proper permission."""
    token = create_test_token(['read:articles'])  # No write

    with patch('httpx.get') as mock_get:
        mock_get.return_value.json.return_value = jwks_mock

        response = client.post(
            '/api/v1/articles/',
            json={'title': 'Test', 'content': '...'},
            headers={'Authorization': f'Bearer {token}'}
        )

    assert response.status_code == 403
```

## Scenario 10: Auth0 Configuration

### Configure Permissions (Scopes) in API

1. Access Auth0 Dashboard
2. Go to **Applications > APIs**
3. Select your API
4. In **Permissions** tab, add:
   - `read:articles` - "Read articles"
   - `write:articles` - "Create and update articles"
   - `delete:articles` - "Delete articles"
   - `admin:write` - "Admin write access"

### Assign Permissions to Users

```javascript
// Auth0 Action (Actions > Flows > Login)
exports.onExecutePostLogin = async (event, api) => {
  // Assign permissions based on user role
  const userRoles = event.user.app_metadata?.roles || [];

  if (userRoles.includes('admin')) {
    api.accessToken.setCustomClaim('permissions', [
      'read:articles',
      'write:articles',
      'delete:articles',
      'admin:write'
    ]);
  } else if (userRoles.includes('editor')) {
    api.accessToken.setCustomClaim('permissions', [
      'read:articles',
      'write:articles'
    ]);
  } else {
    api.accessToken.setCustomClaim('permissions', [
      'read:articles'
    ]);
  }
};
```

## Testing Locally

### Get Token from Auth0

```bash
curl --request POST \
  --url https://YOUR_DOMAIN.auth0.com/oauth/token \
  --header 'content-type: application/json' \
  --data '{
    "client_id":"YOUR_CLIENT_ID",
    "client_secret":"YOUR_CLIENT_SECRET",
    "audience":"YOUR_API_IDENTIFIER",
    "grant_type":"client_credentials"
  }'
```

### Use Token in API

```bash
# Save token
TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."

# Call protected endpoint
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/auth/me

# Create article
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"New Article","content":"..."}' \
  http://localhost:8000/api/v1/articles/
```

## Troubleshooting

### Invalid token

```python
# Check settings
print(f"Domain: {settings.AUTH0_DOMAIN}")
print(f"Audience: {settings.AUTH0_AUDIENCE}")

# Check token claims
import jwt
decoded = jwt.decode(token, options={"verify_signature": False})
print(decoded)
```

### Permissions not recognized

Check if permissions are correct in Auth0 and in the JWT token.

```python
# Debug endpoint (remove in production)
@router.get('/debug/token')
def debug_token(user: CurrentUserDep):
    return {
        'user_id': user.user_id,
        'permissions': user.permissions
    }
```
