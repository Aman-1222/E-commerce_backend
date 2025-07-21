from pydantic import BaseModel
from typing import List, Optional # Keep Optional for now for `next` in PageInfo, will adjust if needed


# --- Product Models ---

# Model for individual size within a product
class Size(BaseModel):
    size: str
    quantity: int

# Request body for creating a product (POST /products)
class ProductCreate(BaseModel):
    name: str
    price: float
    sizes: List[Size]

# Response body for creating a product (POST /products)
# And for data section in List Products API (GET /products)
class ProductResponse(BaseModel):
    id: str # The response expects "id" as string
    name: str
    price: float


# --- Order Models ---

# Model for individual item within an order request
class OrderItem(BaseModel):
    productId: str
    qty: int

# Request body for creating an an order (POST /orders)
class OrderCreate(BaseModel):
    userId: str # Can be hardcoded as per problem statement
    items: List[OrderItem]

# Model for product details to be embedded in OrderResponse items
class ProductDetailsInOrder(BaseModel):
    id: str
    name: str

# Model for an item within the OrderResponse, including product details
class OrderItemDetails(BaseModel):
    productDetails: ProductDetailsInOrder
    qty: int

# Response body for Get List of Orders API (GET /orders/{user_id})
class OrderResponse(BaseModel):
    id: str # Order ID
    items: List[OrderItemDetails]
    total: float


# --- Pagination Models ---

# Model for pagination metadata
class PageInfo(BaseModel):
    next: str # Next page starting index (will use "" if no next)
    limit: int # Number of records in current page
    previous: int # Previous page starting index (will use -1 if no previous)

# Response model for paginated products list
class PaginatedProductsResponse(BaseModel):
    data: List[ProductResponse]
    page: PageInfo

# Response model for paginated orders list
class PaginatedOrdersResponse(BaseModel):
    data: List[OrderResponse]
    page: PageInfo
