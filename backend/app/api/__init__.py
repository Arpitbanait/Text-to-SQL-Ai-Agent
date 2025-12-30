from fastapi import APIRouter
from app.api.routes import query, schema, health

api_router = APIRouter(prefix="/api/v1")

# Include all route modules
api_router.include_router(query.router)
api_router.include_router(schema.router)
api_router.include_router(health.router)
