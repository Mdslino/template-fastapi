# Adding New Features Guide

This guide shows how to add new features to the application following Clean Architecture principles.

## Example: Adding a Product Entity

Let's walk through adding a complete Product feature with CRUD operations.

### Step 1: Domain Layer

#### 1.1 Create Value Objects (if needed)

```python
# app/domain/value_objects/price.py
from decimal import Decimal
from pydantic import BaseModel, field_validator
from app.domain.exceptions import ValidationException

class Price(BaseModel):
    value: Decimal
    currency: str = 'USD'
    
    model_config = {'frozen': True}
    
    @field_validator('value')
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValidationException('Price cannot be negative')
        return v
```

#### 1.2 Create Domain Entity

```python
# app/domain/entities/product.py
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from app.domain.value_objects.price import Price

class Product(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str | None = None
    price: Price
    stock: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    model_config = {'arbitrary_types_allowed': True}
    
    @classmethod
    def create(
        cls,
        name: str,
        price: Price,
        description: str | None = None,
        stock: int = 0
    ) -> 'Product':
        """Factory method to create a new product."""
        return cls(
            name=name,
            price=price,
            description=description,
            stock=stock
        )
    
    def update_stock(self, quantity: int) -> None:
        """Update product stock."""
        self.stock += quantity
        self.updated_at = datetime.now()
        
    def update_price(self, new_price: Price) -> None:
        """Update product price."""
        self.price = new_price
        self.updated_at = datetime.now()
```

### Step 2: Application Layer

#### 2.1 Create DTOs

```python
# app/application/dtos/product.py
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field

class CreateProductDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    price: Decimal = Field(..., gt=0)
    currency: str = 'USD'
    stock: int = Field(default=0, ge=0)

class UpdateProductDTO(BaseModel):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    stock: int | None = None

class ProductDTO(BaseModel):
    id: UUID
    name: str
    description: str | None
    price: Decimal
    currency: str
    stock: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {'from_attributes': True}
```

#### 2.2 Create Repository Port

```python
# app/application/ports/repositories.py (add to existing file)
from typing import Protocol
from uuid import UUID
from app.domain.entities.product import Product
from app.shared.functional.either import Either
from app.shared.functional.option import Option

class ProductRepository(Protocol):
    """Product repository interface."""
    
    def save(self, product: Product) -> Either[Product, Exception]:
        """Save or update a product."""
        ...
    
    def find_by_id(self, product_id: UUID) -> Option[Product]:
        """Find a product by ID."""
        ...
    
    def list_all(
        self, skip: int = 0, limit: int = 100
    ) -> Either[list[Product], Exception]:
        """List all products with pagination."""
        ...
    
    def delete(self, product_id: UUID) -> Either[bool, Exception]:
        """Delete a product by ID."""
        ...
```

#### 2.3 Create Use Cases

```python
# app/application/use_cases/product/create_product.py
from app.application.dtos.product import CreateProductDTO, ProductDTO
from app.application.ports.repositories import ProductRepository
from app.domain.entities.product import Product
from app.domain.value_objects.price import Price
from app.shared.functional.either import Either, Failure

class CreateProductUseCase:
    """Use case for creating a new product."""
    
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
    
    def execute(self, dto: CreateProductDTO) -> Either[ProductDTO, Exception]:
        """Execute the create product use case."""
        try:
            # Create value objects
            price = Price(value=dto.price, currency=dto.currency)
            
            # Create domain entity
            product = Product.create(
                name=dto.name,
                price=price,
                description=dto.description,
                stock=dto.stock
            )
            
            # Save to repository
            result = self.product_repository.save(product)
            
            # Map to DTO
            return result.map(self._to_dto)
            
        except Exception as e:
            return Failure(e)
    
    @staticmethod
    def _to_dto(product: Product) -> ProductDTO:
        """Convert domain entity to DTO."""
        return ProductDTO(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price.value,
            currency=product.price.currency,
            stock=product.stock,
            is_active=product.is_active,
            created_at=product.created_at,
            updated_at=product.updated_at
        )
```

### Step 3: Infrastructure Layer

#### 3.1 Create SQLAlchemy Model and Repository

```python
# app/infrastructure/database/repositories/product_repository.py
from uuid import UUID
import structlog
from sqlalchemy import String, Numeric, Integer, select
from sqlalchemy.orm import Mapped, Session, mapped_column
from app.application.ports.repositories import ProductRepository
from app.domain.entities.product import Product
from app.domain.value_objects.price import Price
from app.infrastructure.database.models import Base, BaseModel
from app.shared.functional.either import Either, Failure, Success
from app.shared.functional.option import Nothing, Option, Some

logger = structlog.get_logger(__name__)

class ProductModel(BaseModel, Base):
    """SQLAlchemy ORM model for Product entity."""
    __tablename__ = 'products'
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default='USD')
    stock: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(default=True)

class SQLAlchemyProductRepository(ProductRepository):
    """SQLAlchemy implementation of ProductRepository."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, product: Product) -> Either[Product, Exception]:
        """Save or update a product in the database."""
        try:
            stmt = select(ProductModel).where(
                ProductModel.external_id == product.id
            )
            db_product = self.session.scalar(stmt)
            
            if db_product:
                # Update existing
                db_product.name = product.name
                db_product.description = product.description
                db_product.price = product.price.value
                db_product.currency = product.price.currency
                db_product.stock = product.stock
                db_product.is_active = product.is_active
                db_product.updated_at = product.updated_at
            else:
                # Create new
                db_product = ProductModel(
                    external_id=product.id,
                    name=product.name,
                    description=product.description,
                    price=product.price.value,
                    currency=product.price.currency,
                    stock=product.stock,
                    is_active=product.is_active,
                    created_at=product.created_at,
                    updated_at=product.updated_at
                )
                self.session.add(db_product)
            
            self.session.commit()
            self.session.refresh(db_product)
            
            return Success(self._to_domain(db_product))
            
        except Exception as e:
            self.session.rollback()
            logger.error('Error saving product', exc_info=e)
            return Failure(e)
    
    @staticmethod
    def _to_domain(db_product: ProductModel) -> Product:
        """Convert SQLAlchemy model to domain entity."""
        return Product(
            id=db_product.external_id,
            name=db_product.name,
            description=db_product.description,
            price=Price(value=db_product.price, currency=db_product.currency),
            stock=db_product.stock,
            is_active=db_product.is_active,
            created_at=db_product.created_at,
            updated_at=db_product.updated_at
        )
    
    # Implement other methods: find_by_id, list_all, delete...
```

#### 3.2 Add Dependencies

```python
# app/infrastructure/api/dependencies.py (add to existing file)
from typing import Annotated
from fastapi import Depends

def get_product_repository(
    db: SessionDep
) -> 'SQLAlchemyProductRepository':
    """Provide ProductRepository dependency."""
    from app.infrastructure.database.repositories.product_repository import (
        SQLAlchemyProductRepository
    )
    return SQLAlchemyProductRepository(db)

ProductRepositoryDep = Annotated[
    'SQLAlchemyProductRepository',
    Depends(get_product_repository)
]

def get_create_product_use_case(
    product_repository: ProductRepositoryDep
) -> 'CreateProductUseCase':
    """Provide CreateProductUseCase dependency."""
    from app.application.use_cases.product.create_product import (
        CreateProductUseCase
    )
    return CreateProductUseCase(product_repository)

CreateProductUseCaseDep = Annotated[
    'CreateProductUseCase',
    Depends(get_create_product_use_case)
]
```

#### 3.3 Create API Schemas

```python
# app/infrastructure/api/schemas/product.py
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field

class ProductCreateRequest(BaseModel):
    """Schema for product creation request."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    price: Decimal = Field(..., gt=0)
    currency: str = Field(default='USD', max_length=3)
    stock: int = Field(default=0, ge=0)

class ProductResponse(BaseModel):
    """Schema for product response."""
    id: UUID
    name: str
    description: str | None
    price: Decimal
    currency: str
    stock: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {'from_attributes': True}
```

#### 3.4 Create API Routes

```python
# app/infrastructure/api/routes/products.py
from uuid import UUID
import structlog
from fastapi import APIRouter, HTTPException, status
from returns.result import Failure, Success

from app.application.dtos.product import CreateProductDTO
from app.infrastructure.api.dependencies import CreateProductUseCaseDep
from app.infrastructure.api.schemas.product import (
    ProductCreateRequest,
    ProductResponse
)

logger = structlog.get_logger(__name__)
router = APIRouter(prefix='/products', tags=['products'])

@router.post(
    '/',
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product(
    request: ProductCreateRequest,
    use_case: CreateProductUseCaseDep
) -> ProductResponse:
    """Create a new product."""
    logger.info('Creating product', name=request.name)
    
    dto = CreateProductDTO(**request.model_dump())
    result = use_case.execute(dto)
    
    if isinstance(result, Success):
        product_dto = result.unwrap()
        logger.info('Product created', product_id=str(product_dto.id))
        return ProductResponse(**product_dto.model_dump())
    elif isinstance(result, Failure):
        error = result.failure()
        logger.error('Failed to create product', error=str(error))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
```

### Step 4: Register Routes

```python
# app/main.py (add to existing file)
from app.infrastructure.api.routes import products

def create_app() -> FastAPI:
    # ... existing code ...
    
    # Include routers
    fastapi_app.include_router(users.router, prefix=settings.API_V1_STR)
    fastapi_app.include_router(products.router, prefix=settings.API_V1_STR)
    
    # ... rest of the code ...
```

### Step 5: Create Migration

```bash
# Create database migration
alembic revision --autogenerate -m "add products table"

# Run migration
alembic upgrade head
```

### Step 6: Add Tests

```python
# tests/domain/test_product.py
def test_create_product():
    price = Price(value=Decimal('99.99'), currency='USD')
    product = Product.create(name='Test Product', price=price)
    
    assert product.id is not None
    assert product.name == 'Test Product'
    assert product.price.value == Decimal('99.99')
    assert product.stock == 0

# tests/application/test_product_use_cases.py
def test_create_product_use_case():
    mock_repo = Mock()
    mock_repo.save.return_value = Success(product)
    
    use_case = CreateProductUseCase(mock_repo)
    dto = CreateProductDTO(name='Test', price=Decimal('99.99'))
    
    result = use_case.execute(dto)
    
    assert isinstance(result, Success)
```

## Summary

Following this pattern ensures:
1. **Separation of concerns**: Each layer has its responsibility
2. **Testability**: Easy to mock and test each component
3. **Maintainability**: Clear structure makes changes easy
4. **Type safety**: Pydantic validation throughout
5. **Dependency injection**: Clean, decoupled code

For more details, see [ARCHITECTURE.md](./ARCHITECTURE.md).
