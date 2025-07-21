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
- PyMongo

## Deployment
App deployed at: [https://e-commerce-backend-5qka.onrender.com](https://e-commerce-backend-5qka.onrender.com)

## Run Locally

1.  **Create a `.env` file:**
    Create a file named `.env` in the root directory of the project (next to `requirements.txt`).
    Add your MongoDB connection string to it:
    ```
    MONGO_URI="your_mongodb_atlas_connection_string_here"
    ```
    (Replace `your_mongodb_atlas_connection_string_here` with your actual MongoDB Atlas URI).

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The API documentation will be available at `http://127.0.0.1:8000/docs`.