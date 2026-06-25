import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.models import AdminUser, ChatMessage, Order, OrderItem, Product
from app.migrations import run_lightweight_migrations
from app.routes.auth_routes import router as auth_router
from app.routes.chat_routes import router as chat_router
from app.routes.dashboard_routes import router as dashboard_router
from app.routes.order_routes import router as order_router
from app.routes.product_routes import router as product_router
from app.seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    # For this portfolio version, tables are created automatically.
    # A later improvement can replace this with Alembic migrations.
    Base.metadata.create_all(bind=engine)
    seed_database()
    run_lightweight_migrations()
    yield


app = FastAPI(
    title="Smart Customer Support Chatbot API",
    description="A deployment-ready rule-based customer support chatbot backend built with FastAPI, SQLite, and PostgreSQL support.",
    version="1.4.0",
    lifespan=lifespan,
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Smart Customer Support Chatbot API is running successfully.",
        "project": "Smart Customer Support Chatbot",
        "version": "1.4.0",
        "docs": "Visit /docs to test the API endpoints.",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "api": "running",
    }


@app.get("/api/info")
def api_info():
    return {
        "project_name": "Smart Customer Support Chatbot",
        "description": "A full-stack rule-based customer support chatbot backend built with FastAPI, SQLite, and PostgreSQL support.",
        "features": [
            "Improved rule-based chatbot responses",
            "Database-driven product menu support",
            "Product-specific price replies",
            "Improved product and quantity detection",
            "Cart-style orders with multiple order items",
            "Customer contact and delivery details on orders",
            "Order totals saved in the database",
            "Order confirmation for the full pending cart",
            "Order cancellation for the full pending cart",
            "Session-based chat history",
            "Admin login with signed bearer tokens",
            "Protected admin dashboard, orders, products, and chat history endpoints",
            "Deployment-ready Docker and PostgreSQL configuration",
        ],
        "main_endpoints": [
            "POST /api/chat/",
            "POST /api/auth/login",
            "GET /api/auth/me",
            "GET /api/chat/history/{session_id}",
            "GET /api/chat/sessions/recent",
            "GET /api/products/",
            "GET /api/orders/",
            "GET /api/dashboard/summary",
        ],
    }


app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(dashboard_router)
