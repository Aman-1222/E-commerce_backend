# app/main.py
from fastapi import FastAPI, HTTPException, status, Query
from typing import List, Optional

from app.models import ( # Import all necessary Pydantic models
    ProductCreate, ProductResponse,
    OrderCreate, OrderResponse,
    PaginatedProductsResponse, PaginatedOrdersResponse
)
from app import crud # Import the crud module

app = FastAPI()

# --- API Endpoints ---

# 1. Create Products API
@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate):
    """
    Creates a new product in the database.
    """
    created_product = crud.create_product_db(product)
    if created_product:
        return created_product
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create product")


# 2. List Products API
@app.get("/products", response_model=PaginatedProductsResponse, status_code=status.HTTP_200_OK)
def list_products(
    name: Optional[str] = Query(None, description="Partial or regex search for product name"),
    size: Optional[str] = Query(None, description="Filter products by available size"),
    limit: int = Query(10, ge=1, description="Number of documents to return"),
    offset: int = Query(0, ge=0, description="Number of documents to skip for pagination (sorted by _id)")
):
    """
    Lists products with optional filtering, searching, and pagination.
    """
    products, page_info = crud.get_products_db(name, size, limit, offset)
    return PaginatedProductsResponse(data=products, page=page_info)


# 3. Create Order API
@app.post("/orders", status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate):
    """
    Creates a new order.
    Validates product IDs and calculates total price.
    """
    order_id = crud.create_order_db(order)
    if order_id:
        return {"id": order_id}
    # If create_order_db returns None, it means a product was not found or ID was invalid
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more products in the order not found or invalid product ID format.")


# 4. Get List of Orders API
@app.get("/orders/{user_id}", response_model=PaginatedOrdersResponse, status_code=status.HTTP_200_OK)
def get_list_of_orders(
    user_id: str,
    limit: int = Query(10, ge=1, description="Number of documents to return"),
    offset: int = Query(0, ge=0, description="Number of documents to skip for pagination (sorted by _id)")
):
    """
    Retrieves a list of orders for a specific user with pagination.
    Performs a lookup to include product details for each item in the order.
    """
    orders, page_info = crud.get_orders_by_user_id_db(user_id, limit, offset)
    return {"data": orders, "page": page_info}
