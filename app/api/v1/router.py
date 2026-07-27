"""
app/api/v1/router.py
--------------------
Central v1 API router.
"""

from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.auth.router import router as auth_router
from app.api.v1.projects import router as projects_router
from app.api.v1.competitors import router as competitors_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.reports import router as reports_router
from app.api.v1.company import router as company_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(projects_router)
api_v1_router.include_router(competitors_router)
api_v1_router.include_router(alerts_router, prefix="/alerts")
api_v1_router.include_router(dashboard_router, prefix="/dashboard")
api_v1_router.include_router(reports_router, prefix="/reports")
api_v1_router.include_router(company_router)
