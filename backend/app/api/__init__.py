"""API router — all 11 modules."""

from fastapi import APIRouter

from app.api.endpoints import (
    documents,
    change_controls,
    capas,
    risks,
    trainings,
    nonconformances,
    deviations,
    equipment,
    calibrations,
    complaints,
    suppliers,
    auth,
)

api_router = APIRouter()

# Auth
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])

# 11 Discovery modules
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(change_controls.router, prefix="/change-controls", tags=["Change Control"])
api_router.include_router(capas.router, prefix="/capas", tags=["CAPAs"])
api_router.include_router(risks.router, prefix="/risks", tags=["Risks"])
api_router.include_router(trainings.router, prefix="/trainings", tags=["Training"])
api_router.include_router(nonconformances.router, prefix="/nonconformances", tags=["Non-Conformances"])
api_router.include_router(deviations.router, prefix="/deviations", tags=["Deviations"])
api_router.include_router(equipment.router, prefix="/equipment", tags=["Equipment"])
api_router.include_router(calibrations.router, prefix="/calibrations", tags=["Calibration"])
api_router.include_router(complaints.router, prefix="/complaints", tags=["Complaints"])
api_router.include_router(suppliers.router, prefix="/suppliers", tags=["Suppliers"])
