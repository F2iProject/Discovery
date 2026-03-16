# CLAUDE.md — Discovery

## What is this?
Discovery is a free, open-source lab organization platform. 11 modules, self-hosted, Apache 2.0.
It is the freeware tier of the BioQMS product line (F2i Partners).

## Stack
- Backend: Python 3.12 / FastAPI / SQLAlchemy 2.0 / PostgreSQL 16 / Redis 7
- Frontend: React / TypeScript / Vite
- Deployment: Docker Compose

## Architecture Rules
- **Multi-tenant**: Every domain model has `tenant_id` (row-level isolation via `TenantMixin`)
- **Soft deletes**: Use `SoftDeleteMixin`, never hard delete
- **Timestamps**: Use `TimestampMixin` on all models
- **UUIDs**: All primary keys are UUID strings (`generate_uuid()`)
- **No compliance features**: No audit trail, no e-signatures, no training gating. Those belong in BioQMS (paid tier).
- **No AI features**: No copilots, no LLM integrations. Those belong in BioQMS.

## 11 Modules
1. Documents — protocols, methods, SOPs (version-controlled)
2. Change Control — track changes to processes/documents
3. CAPAs — corrective and preventive actions
4. Risks — risk identification and assessment
5. Training — who needs to learn what
6. Non-Conformances — when things don't go as planned
7. Deviations — departures from procedures
8. Equipment — lab instrument registry
9. Calibration — calibration schedules and results
10. Complaints — customer feedback intake
11. Suppliers — vendor list

## Conventions
- Endpoint pattern: `GET /api/{module}`, `POST /api/{module}`, `GET /api/{module}/{id}`, `PATCH /api/{module}/{id}`, `DELETE /api/{module}/{id}`
- Models live in `backend/app/models/`
- Endpoints live in `backend/app/api/endpoints/`
- Schemas live in `backend/app/schemas/`
- All modules register in `backend/app/api/__init__.py`

## Positioning
Discovery is marketed as a **lab organization tool**, not a QMS.
- Use: "organize," "track," "manage," "structure"
- Avoid: "compliance," "validated," "21 CFR," "audit-ready"
- The compliance story starts at BioQMS ($15K/yr)
