# app/crud.py
from typing import List, Optional
from bson import ObjectId # Still needed for database interactions
import re

from app.config import products_collection, orders_collection
from app.models import (
    ProductCreate, ProductResponse,
    OrderCreate, OrderResponse,
    PageInfo, OrderItemDetails, ProductDetailsInOrder, Size # Import Size for product creation
)


# --- Product CRUD Operations ---

def create_product_db(product: ProductCreate):
    """Inserts a new product into the database."""
    # Manually prepare the document for MongoDB insertion
    product_doc = {
        "name": product.name,
        "price": product.price,
        "sizes": [s.model_dump() for s in product.sizes] # Convert Size models to dicts
    }
    
    result = products_collection.insert_one(product_doc)
    
    if result.inserted_id:
        return {"id": str(result.inserted_id)}  # Return ID as string in dict
    return None

def get_products_db(name: Optional[str], size: Optional[str], limit: int, offset: int) :
    """Retrieves products from the database with filters and pagination."""
    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if size:
        query["sizes.size"] = size

    total_count = products_collection.count_documents(query)
    
    products_cursor = products_collection.find(query).sort("_id", 1).skip(offset).limit(limit)
    
    products = [
        ProductResponse(
            id=str(product_doc["_id"]),
            name=product_doc["name"],
            price=product_doc["price"]
        )
        for product_doc in products_cursor
    ]

  # Inline pagination logic
    next_offset = offset + limit
    previous_offset = offset - limit if offset - limit >= 0 else -1
    next_page = str(next_offset) if next_offset < total_count else ""

    page_info = PageInfo(
        next=next_page,
        limit=limit,
        previous=previous_offset
    )
    return products, page_info  


# --- Order CRUD Operations ---

def create_order_db(order: OrderCreate):
    """
    Creates a new order in the database.
    Validates product IDs and calculates total price.
    Returns the ID of the created order.
    """
    items_to_store = []
    total_order_price = 0.0

    for item in order.items:
        # Fetch product details to validate and calculate price
        # Ensure productId is converted to ObjectId for lookup
        try:
            product_obj_id = ObjectId(item.productId)
        except Exception:
            return None # Invalid product ID format

        product_doc = products_collection.find_one({"_id": product_obj_id})
        if not product_doc:
            return None # Indicate product not found

        item_price = product_doc["price"] * item.qty
        total_order_price += item_price

        items_to_store.append({
            "productId": str(product_doc["_id"]), # Store as string for consistency
            "qty": item.qty,
        })

    # Manually prepare the order document for MongoDB insertion
    order_doc = {
        "userId": order.userId,
        "items": items_to_store,
        "total": total_order_price
    }
    
    result = orders_collection.insert_one(order_doc)

    if result.inserted_id:
        return str(result.inserted_id)
    return None

def get_orders_by_user_id_db(user_id: str, limit: int, offset: int):
    """
    Retrieves a list of orders for a specific user with pagination,
    including product details lookup.
    """
    query = {"userId": user_id}

    pipeline = [
    {"$match": query},
    {"$sort": {"_id": 1}},
    {"$skip": offset},
    {"$limit": limit},
    {"$unwind": "$items"},
    {
        "$addFields": {
            "items.productIdObj": {
                "$convert": {
                    "input": "$items.productId",
                    "to": "objectId",
                    "onError": None,
                    "onNull": None
                }
            }
        }
    },
    {
        "$lookup": {
            "from": "products",
            "localField": "items.productIdObj",
            "foreignField": "_id",
            "as": "items.productDetails"
        }
    },
    {"$unwind": "$items.productDetails"},
    {
        "$addFields": {
            "items.productDetails.id": {"$toString": "$items.productDetails._id"},
            "items.productDetails.name": "$items.productDetails.name"
        }
    },
    {
        "$group": {
            "_id": "$_id",
            "userId": {"$first": "$userId"},
            "total": {"$first": "$total"},
            "items": {
                "$push": {
                    "qty": "$items.qty",
                    "productDetails": {
                        "id": "$items.productDetails.id",
                        "name": "$items.productDetails.name"
                    }
                }
            }
        }
    },
    {
        "$project": {
            "id": {"$toString": "$_id"},
            "items": 1,
            "total": 1,
            "_id": 0
        }
    }
    ]

    orders_cursor = orders_collection.aggregate(pipeline)

    orders = []
    for order_doc in orders_cursor:
        # No need to use format_order_doc_for_response
        orders.append(OrderResponse(**order_doc))

    # Total matching documents for pagination
    total_count = orders_collection.count_documents(query)

    # Inline pagination info
    next_offset = offset + limit
    previous_offset = offset - limit if offset - limit >= 0 else -1
    next_page = str(next_offset) if next_offset < total_count else ""

    page_info = PageInfo(
        next=next_page,
        limit=limit,
        previous=previous_offset
    )

    return orders, page_info
