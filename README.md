# E-commerce_backend

E-commerce backend using FastAPI & MongoDB.

## APIs Implemented
- POST /products → Create a product
- GET /products → List products (filters: name, size, limit, offset)
- POST /orders → Create an order
- GET /orders/{user_id} → Get user orders

## Tech Stack
- FastAPI
- MongoDB (Atlas)
- Pymongo

## Deployment
App deployed at: [https://e-commerce-backend-5qka.onrender.com](https://e-commerce-backend-5qka.onrender.com)

## Run Locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload
