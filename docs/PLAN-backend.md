# Discovery Backend Implementation Plan

**Generated:** 2026-03-16
**Status:** Ready for implementation

---

## Architecture Summary

**Discovery** has 11 module stubs (all identical: empty CRUD endpoints returning `[]` or `"not implemented"`), 15 SQLAlchemy models already defined, and infrastructure (database.py, config.py, main.py, alembic env.py) in place. No schemas directory contents exist yet; no services directory contents exist yet; no auth dependencies (get_current_user, get_current_tenant) exist yet.

**bioqms-core1** has full working implementations for documents, CAPAs, risks, and training. However, these are heavily loaded with compliance features (trace graphs, audit logging, tenant sharing, optimistic concurrency versioning, status state machines with guards, risk matrix configuration, soft-delete filtering services, document vaults/code generation). Discovery must be a stripped-down freeware version — pure CRUD, no compliance.

---

## Key Decision: Port Pattern, Not Code

The bioqms-core1 code is too compliance-heavy to copy directly. The correct approach is:

1. **Extract the CRUD skeleton pattern** from bioqms-core1 (create/list/get/update/soft-delete shape)
2. **Strip all compliance features**: no trace nodes, no audit events, no optimistic concurrency (row_version), no retention service, no tenant sharing, no context stamping
3. **Simplify auth**: Discovery uses a single-tenant-per-user model (no TenantMembership table, no multi-tenant selection). The JWT carries tenant_id extracted from the User row.
4. **Write a generic base service** that all 11 modules can reuse, since every module follows the identical CRUD + tenant filter + soft delete pattern

---

## Phase 0: Foundation (Auth + Base Service)

**Priority: Must do first. Everything depends on this.**

### 0A. Auth module

**Source:** Adapt from bioqms-core1's `core/security.py` and `auth.py`, heavily simplified.

What to port:
- `verify_password()` and `get_password_hash()` — copy as-is (bcrypt, 6 lines)
- `create_access_token()` — copy as-is (jose JWT, 10 lines)
- `get_current_user()` dependency — simplify: decode JWT, look up user by email, check is_active. No token revocation, no inactivity timeout, no revoked_at check.
- `get_current_tenant()` dependency — new: extract tenant_id from JWT payload, query Tenant table, return it.

What to write fresh:
- `POST /api/auth/register` — create Tenant + User in one transaction (first user = admin). Hash password. Return JWT.
- `POST /api/auth/login` — verify email/password, return JWT with `{sub: email, tenant_id: uuid}`.
- `GET /api/auth/me` — return current user info.
- Pydantic schemas: `RegisterRequest`, `LoginRequest`, `TokenResponse`, `UserResponse`.

**Complexity: M**

**Files to create:**
- `backend/app/core/security.py` — password hashing + JWT creation
- `backend/app/auth.py` — `get_current_user`, `get_current_tenant` FastAPI dependencies
- `backend/app/schemas/auth.py` — register/login/token/user schemas
- Update `backend/app/api/endpoints/auth.py` — implement the 3 endpoints

### 0B. Base CRUD service

**Source:** Write fresh. bioqms-core1 has no generic base service.

Discovery's 11 modules all follow the same pattern:
- List: `SELECT * FROM table WHERE tenant_id = ? AND is_deleted = false`
- Create: set tenant_id, set created_by, generate auto-number, insert
- Get: by id + tenant_id + not deleted
- Update: PATCH with `exclude_unset=True`
- Delete: soft-delete (set is_deleted=True, deleted_at=now)

Build a generic `CRUDService[ModelT, CreateSchemaT, UpdateSchemaT]` class that handles all of this. Each module only needs to provide: model class, prefix for auto-numbering, and any module-specific validation.

**Auto-numbering helper:** Simple per-tenant sequential numbering. Pattern: `{PREFIX}-{seq:04d}` (e.g., `DOC-0001`, `CAPA-0001`, `NC-0001`). Count existing records for that tenant + prefix, add 1.

**Files to create:**
- `backend/app/services/base.py` — generic CRUD service
- `backend/app/services/__init__.py`
- `backend/app/utils/__init__.py`
- `backend/app/utils/numbering.py` — auto-number generator

**Complexity: M**

---

## Phase 1: Port the 4 Existing Modules (Simplified)

**Priority: Second. These have bioqms-core1 reference implementations.**

Each module needs: Pydantic schemas (Create, Update, Read) + endpoint implementation using the base CRUD service.

### 1A. Risks module

**Source:** Adapt from bioqms-core1 `schemas/risks.py` and `mvp_risks.py`.

What to port:
- Schema shape: title, description, severity (1-5), likelihood (1-5), risk_level (computed). Strip: detectability, RPN, URS linkage, row_version.
- CRUD endpoints: standard 5-endpoint pattern.
- risk_level computation: simple inline calculation, no separate risk_matrix_service.

What to strip:
- Status state machine, risk-training links, risk-validation links, trace graph sync, optimistic concurrency.

**Complexity: S**

### 1B. CAPAs module

**Source:** Adapt from bioqms-core1 `schemas/capa.py` and `capa.py`.

What to port:
- CRUD for parent CAPA: 5 standard endpoints.
- CRUD for CAPAAction child: POST/GET/PATCH under `/api/capas/{id}/actions`.

What to strip:
- Status state machine with guards, linkage tables, due date management, overdue computation, optimistic concurrency.

**Complexity: M** (has child entity CAPAAction)

### 1C. Documents module

**Source:** Adapt from bioqms-core1 `schemas/documents.py` and `mvp_documents.py`.

What to port:
- CRUD for Document: 5 standard endpoints.
- CRUD for DocumentVersion child: POST version, GET versions list.

What to strip:
- Complex code generation, file upload/download (defer), training mode, status lifecycle, S-Phase workspace checks, CSV export.

**Complexity: M** (has child entity DocumentVersion)

### 1D. Training module

**Source:** Adapt from bioqms-core1 `schemas/trainings.py` and `mvp_trainings.py`.

What to port:
- CRUD for Training: 5 standard endpoints.
- CRUD for TrainingAssignment child: assign user, list assignments, complete assignment.

What to strip:
- Status workflow, training requirements, passing_score, evidence, trace nodes.

**Complexity: M** (has child entity TrainingAssignment)

---

## Phase 2: Build the 7 New Modules

**Priority: Third. All written fresh, no bioqms-core1 reference.**

All 7 use the base CRUD service. Primarily schema definitions.

| Module | Auto-number | Child entities | Complexity |
|--------|------------|---------------|------------|
| Equipment | `EQ-{seq:04d}` | None | S |
| Calibration | None (append-only) | None | S |
| Supplier | None (by name) | None | S |
| NonConformance | `NC-{seq:04d}` | None | S |
| Deviation | `DEV-{seq:04d}` | None | S |
| Complaint | `COMP-{seq:04d}` | None | S |
| Change Control | `CC-{seq:04d}` | None | S |

**Dependency:** Calibration depends on Equipment (FK). All others depend only on the base service.

---

## Phase 3: Database Migration

- Run `alembic revision --autogenerate -m "initial_schema"` after all models finalized
- Run `alembic upgrade head` to apply
- Create seed script: default tenant + admin user

**Complexity: S**

---

## Phase 4: Testing

- `backend/tests/conftest.py` — SQLite in-memory test DB, test client, authenticated user fixture
- `backend/tests/test_auth.py` — register, login, me
- `backend/tests/test_{module}.py` — one file per module, test all 5 CRUD operations
- 11 modules × 5 endpoints = 55 test cases minimum

**Complexity: M**

---

## Implementation Order Summary

| Step | Module | Source | Complexity | Dependencies |
|------|--------|--------|------------|--------------|
| 0A | Auth | Adapt bioqms-core1 | M | None |
| 0B | Base CRUD Service | Fresh | M | Auth |
| 1A | Risks | Adapt bioqms-core1 | S | Base service |
| 1B | CAPAs | Adapt bioqms-core1 | M | Base service |
| 1C | Documents | Adapt bioqms-core1 | M | Base service |
| 1D | Training | Adapt bioqms-core1 | M | Base service, Documents |
| 2A | Equipment | Fresh | S | Base service |
| 2B | Calibration | Fresh | S | Equipment |
| 2C | Supplier | Fresh | S | Base service |
| 2D | NonConformance | Fresh | S | Base service |
| 2E | Deviation | Fresh | S | Base service |
| 2F | Complaint | Fresh | S | Base service |
| 2G | Change Control | Fresh | S | Base service |
| 3 | DB Migration | Fresh | S | All models |
| 4 | Tests | Fresh | M | All endpoints |

---

## Key Differences: bioqms-core1 vs Discovery

| Feature | bioqms-core1 | Discovery |
|---------|-------------|-----------|
| IDs | Integer auto-increment | UUID strings |
| Tenant model | TenantMembership join table | Simple tenant_id FK on User |
| Auth | OAuth2 + refresh tokens + revocation + lockout | Simple JWT login/register |
| Status fields | State machines with transition guards | Free-form string updates |
| Optimistic concurrency | row_version + If-Match header | None |
| Soft deletes | RetentionService | Inline `WHERE is_deleted = false` |
| Audit trail | Full audit logging | None |
| Trace graph | Trace nodes | None |
| Code generation | Complex vault/company/category prefix | Simple `PREFIX-{seq:04d}` |

---

## Files to Create

1. `backend/app/core/security.py`
2. `backend/app/auth.py`
3. `backend/app/schemas/__init__.py`
4. `backend/app/schemas/auth.py`
5. `backend/app/schemas/document.py`
6. `backend/app/schemas/capa.py`
7. `backend/app/schemas/risk.py`
8. `backend/app/schemas/training.py`
9. `backend/app/schemas/change_control.py`
10. `backend/app/schemas/nonconformance.py`
11. `backend/app/schemas/deviation.py`
12. `backend/app/schemas/equipment.py`
13. `backend/app/schemas/calibration.py`
14. `backend/app/schemas/complaint.py`
15. `backend/app/schemas/supplier.py`
16. `backend/app/services/__init__.py`
17. `backend/app/services/base.py`
18. `backend/app/utils/__init__.py`
19. `backend/app/utils/numbering.py`
20. `backend/tests/conftest.py`

## Files to Modify

1. `backend/app/api/endpoints/auth.py` — implement 3 endpoints
2. All 11 module endpoint files — implement CRUD
3. `backend/app/models/user.py` — add security fields (if needed)

---

## Estimated Total Effort

| Phase | Work | Time |
|-------|------|------|
| Phase 0 | Auth + Base Service | 3-4 hours |
| Phase 1 | 4 ported modules | 2-3 hours |
| Phase 2 | 7 new modules | 2-3 hours |
| Phase 3 | Migration + Seed | 30 minutes |
| Phase 4 | Tests | 3-4 hours |
| **Total** | | **~11-14 hours** |
