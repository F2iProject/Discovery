# Discovery Frontend Implementation Plan

Based on analysis of the Discovery backend (11 modules with CRUD endpoints) and the existing bioqms-core1 frontend patterns.

---

## What I Found

**Discovery backend** has 11 modules with uniform CRUD endpoints at `/api/{module}` (GET list, POST create, GET by id, PATCH update, DELETE soft-delete), plus `/api/auth` (register, login, me). All models use UUID string PKs, `tenant_id` for multi-tenancy, `TimestampMixin`, and `SoftDeleteMixin`. The backend endpoints are stub implementations (TODO) but the route structure and models are complete.

**bioqms-core1 frontend** uses React 19 + TypeScript + Vite + Tailwind CSS 4 + Radix UI primitives (via shadcn/ui pattern) + lucide-react icons + react-router-dom v7. It has a clean architecture: `lib/api.ts` (ApiClient wrapper with auth), `context/ApiContext.tsx` (auth state + tenant selection), `services/` (per-module API mappers), `types.ts` (TypeScript interfaces), `components/ui/` (shadcn primitives), `components/` (domain components like StatusBadge, Sidebar), and `pages/` (list + detail pages per module). The layout is a sidebar + topbar + main content area.

**Key differences for Discovery**: No compliance features (no audit trail, no e-signatures, no training gating, no AI copilots). Dark mode preferred. Simpler data shapes (Discovery models are leaner than BioQMS). Must feel like a researcher tool, not enterprise software. Some models have child relationships (Document->DocumentVersion, CAPA->CAPAAction, Training->TrainingAssignment, Equipment->CalibrationRecord).

---

## What to Port vs Write Fresh

**Port from bioqms-core1** (adapt, do not copy verbatim):
- `lib/api.ts` -- the ApiClient wrapper is solid and module-agnostic. Change the base URL config for Discovery's `/api` prefix.
- `lib/apiConfig.ts` -- URL builder. Minor changes only.
- `context/ApiContext.tsx` -- auth provider pattern is reusable. Simplify: Discovery has simpler tenant model (single tenant per user likely for freeware tier). Remove the multi-tenant selection flow initially.
- `components/ui/` -- the shadcn/ui primitives (button, input, select, dialog, tabs, textarea, badge). Port all 8 files directly. These are framework-level.
- `lib/formatters.ts` -- date formatting utilities.
- The page layout pattern (Sidebar + TopBar + Suspense-wrapped Routes) from `App.tsx`.
- The list page pattern (search + filter + table + create dialog) from `DocumentsListPage.tsx`.

**Write fresh**:
- All 11 service files (Discovery's API shapes differ from BioQMS).
- All type definitions (Discovery models are different).
- All 22+ page components (11 list pages + 11 detail/create pages + dashboard).
- Sidebar navigation (different modules, different icons).
- StatusBadge (different status values per module).
- Dark mode theme (bioqms-core1 is light mode with `bg-gray-50`).
- Login page (simpler, Discovery-branded, no API base config needed for Docker setup).

---

## Component Architecture

- `src/app/lib/` -- api.ts, apiConfig.ts, formatters.ts, cn.ts (classname utility)
- `src/app/context/` -- AuthContext.tsx (simpler than bioqms ApiContext)
- `src/app/types/` -- one file per module or a single types.ts
- `src/app/services/` -- one file per module (11 files) + authService.ts
- `src/app/components/ui/` -- shadcn primitives (button, input, select, dialog, tabs, textarea, badge)
- `src/app/components/` -- StatusBadge, Sidebar, TopBar, EmptyState, DataTable, PageHeader, ConfirmDialog
- `src/app/pages/` -- 24 page components total
- `src/styles/` -- tailwind.css, theme.css (dark mode variables)

---

## Routes Table (24 pages)

| Route | Page | Module |
|---|---|---|
| `/` | DashboardPage | -- |
| `/login` | LoginPage | Auth |
| `/documents` | DocumentListPage | Documents |
| `/documents/:id` | DocumentDetailPage | Documents |
| `/change-controls` | ChangeControlListPage | Change Control |
| `/change-controls/:id` | ChangeControlDetailPage | Change Control |
| `/capas` | CAPAListPage | CAPAs |
| `/capas/:id` | CAPADetailPage | CAPAs |
| `/risks` | RiskListPage | Risks |
| `/risks/:id` | RiskDetailPage | Risks |
| `/trainings` | TrainingListPage | Training |
| `/trainings/:id` | TrainingDetailPage | Training |
| `/nonconformances` | NCListPage | Non-Conformances |
| `/nonconformances/:id` | NCDetailPage | Non-Conformances |
| `/deviations` | DeviationListPage | Deviations |
| `/deviations/:id` | DeviationDetailPage | Deviations |
| `/equipment` | EquipmentListPage | Equipment |
| `/equipment/:id` | EquipmentDetailPage | Equipment |
| `/calibrations` | CalibrationListPage | Calibration |
| `/calibrations/:id` | CalibrationDetailPage | Calibration |
| `/complaints` | ComplaintListPage | Complaints |
| `/complaints/:id` | ComplaintDetailPage | Complaints |
| `/suppliers` | SupplierListPage | Suppliers |
| `/suppliers/:id` | SupplierDetailPage | Suppliers |

---

## UI Framework Recommendation

Tailwind CSS 4 + shadcn/ui primitives (Radix UI). This is exactly what bioqms-core1 uses. It is lightweight, composable, and works perfectly for the "clean, fast, simple" requirement. No full component libraries like MUI or Ant Design. Use lucide-react for icons. For dark mode, use Tailwind's `dark:` variant with CSS custom properties for theming.

---

## Auth Flow

1. LoginPage at `/login` (email + password form, Discovery branded)
2. POST `/api/auth/login` returns JWT
3. Store JWT in localStorage
4. AuthContext provides `client`, `currentUser`, `authStatus`
5. App.tsx checks authStatus: `checking` shows spinner, `unauthenticated` shows LoginPage, `authenticated` shows AppShell
6. ApiClient attaches `Authorization: Bearer {token}` to all requests
7. On 401, clear token and redirect to login
8. No tenant selection in v1 (freeware = single org per instance)

---

## Priority Order for Building (4 tiers)

### Tier 1 -- Foundation (build first, everything depends on this)
1. Vite project scaffolding (package.json, tsconfig, vite.config, tailwind)
2. `lib/api.ts`, `lib/apiConfig.ts`, `lib/cn.ts`, `lib/formatters.ts`
3. `components/ui/` -- all shadcn primitives
4. `context/AuthContext.tsx`
5. `App.tsx` (routing shell, Sidebar, TopBar)
6. `LoginPage.tsx`
7. `DashboardPage.tsx` (basic placeholder with module counts)

### Tier 2 -- Core modules (most used by researchers)
8. Documents (list + detail) -- complexity: medium (has versioning sub-table)
9. Equipment (list + detail) -- complexity: low (flat model)
10. Risks (list + detail) -- complexity: low-medium (severity/likelihood matrix display)

### Tier 3 -- Quality modules
11. CAPAs (list + detail) -- complexity: medium (has CAPAAction child records)
12. Non-Conformances (list + detail) -- complexity: low (flat, links to CAPA)
13. Deviations (list + detail) -- complexity: low (flat, links to CAPA + document)
14. Change Control (list + detail) -- complexity: low (flat, links to document)
15. Complaints (list + detail) -- complexity: low (flat, links to CAPA)

### Tier 4 -- Support modules
16. Training (list + detail) -- complexity: medium (has TrainingAssignment child records)
17. Calibrations (list + detail) -- complexity: low (links to equipment)
18. Suppliers (list + detail) -- complexity: low (flat model, contact info)

---

## Complexity Estimates per Page

| Page | Complexity | Notes |
|---|---|---|
| LoginPage | Low | Simple form, JWT storage |
| DashboardPage | Medium | Summary cards, maybe recent activity |
| DocumentListPage | Low | Standard table + search + filter |
| DocumentDetailPage | Medium | Version history sub-table, file upload |
| ChangeControlListPage | Low | Standard table |
| ChangeControlDetailPage | Low | Simple form |
| CAPAListPage | Low | Standard table + priority badges |
| CAPADetailPage | Medium | Action items sub-table (CRUD within detail) |
| RiskListPage | Low | Standard table + severity coloring |
| RiskDetailPage | Low-Medium | Severity x Likelihood display |
| TrainingListPage | Low | Standard table |
| TrainingDetailPage | Medium | Assignment sub-table (user + status + due date) |
| NCListPage | Low | Standard table |
| NCDetailPage | Low | Simple form + CAPA link |
| DeviationListPage | Low | Standard table |
| DeviationDetailPage | Low | Simple form |
| EquipmentListPage | Low | Standard table |
| EquipmentDetailPage | Low-Medium | Shows linked calibration records |
| CalibrationListPage | Low | Standard table |
| CalibrationDetailPage | Low | Simple form + equipment link |
| ComplaintListPage | Low | Standard table |
| ComplaintDetailPage | Low | Simple form |
| SupplierListPage | Low | Standard table |
| SupplierDetailPage | Low | Contact info form |

---

## Shared Components to Build

1. **DataTable** -- generic sortable/filterable table component. Accepts column definitions and data array. Used by all 11 list pages. This is the highest-leverage shared component.
2. **StatusBadge** -- simplified from bioqms. Maps status strings to colored badges. Needs module-aware coloring.
3. **PageHeader** -- title + description + action button (e.g., "Create Document"). Used on every list page.
4. **EmptyState** -- "No items yet" display with an icon and create button. Used when list is empty.
5. **ConfirmDialog** -- "Are you sure?" modal for delete actions.
6. **Sidebar** -- 11 module nav links + Dashboard. Group into categories: "Organize" (Documents, Equipment, Suppliers), "Track" (CAPAs, NCs, Deviations, Change Control, Complaints), "Develop" (Training, Risks, Calibrations).
7. **TopBar** -- user avatar/email, logout button, breadcrumbs optional.
8. **FormField** -- label + input wrapper for consistent form styling across detail pages.

---

## Dark Mode Strategy

- Define CSS custom properties in `theme.css` for bg, text, border, card colors
- Use Tailwind `dark:` classes throughout
- Default to dark mode (check `prefers-color-scheme`, default dark)
- Colors: dark navy/charcoal backgrounds (`#0f172a`, `#1e293b`), white/gray text, blue accent (`#3b82f6`), green/red/yellow for status badges
- Sidebar: dark background (`bg-slate-900`), lighter text

---

## Service Layer Pattern (per module)

Each service file exports an object with: `list(client, signal)`, `get(client, id, signal)`, `create(client, payload, signal)`, `update(client, id, payload, signal)`, `remove(client, id, signal)`. The service handles snake_case to camelCase mapping between API responses and TypeScript types.

---

## Type Definitions (all modules consolidated)

All in `src/app/types/index.ts`. Each module gets an interface matching the backend model fields (camelCase). Status union types defined per module. Child record types (DocumentVersion, CAPAAction, TrainingAssignment) defined alongside parent.

---

## Critical Reference Files

- `bioqms-core1/pilot_frontend/src/app/lib/api.ts` - Port this ApiClient wrapper directly; it is the foundation for all API calls
- `bioqms-core1/pilot_frontend/src/app/context/ApiContext.tsx` - Port and simplify this auth context pattern for Discovery's AuthContext
- `bioqms-core1/pilot_frontend/src/app/pages/DocumentsListPage.tsx` - Reference pattern for all 11 list pages (search + filter + table + create dialog)
- `bioqms-core1/pilot_frontend/src/app/App.tsx` - Reference for app shell structure (sidebar + routes + lazy loading + auth gate)
- `Discovery/backend/app/api/__init__.py` - Defines all 11 API route prefixes that the frontend services must match
