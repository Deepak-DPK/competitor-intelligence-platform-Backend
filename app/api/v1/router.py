"""
app/api/v1/router.py
--------------------
Central v1 API router.

All feature routers are registered here.  Import and include this single
router in app/main.py.  This keeps main.py clean and makes it trivial
to add new feature modules in future phases.
"""

from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.auth.router import router as auth_router
from app.api.v1.projects import router as projects_router
from app.api.v1.competitors import router as competitors_router

# ------------------------------------------------------------------ #
# v1 parent router
# ------------------------------------------------------------------ #
api_v1_router = APIRouter()

# ------------------------------------------------------------------ #
# Registered routers
# Phase 1: health
# Phase 3: auth
# Phase 4: projects, competitors
#
# Future phases:
#   from app.api.v1.monitoring  import router as monitoring_router
#   from app.api.v1.dashboard   import router as dashboard_router
#   from app.api.v1.reports     import router as reports_router
#   from app.api.v1.alerts      import router as alerts_router
#   from app.api.v1.settings    import router as settings_router
# ------------------------------------------------------------------ #

api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(projects_router)
api_v1_router.include_router(competitors_router)
