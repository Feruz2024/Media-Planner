# Media Advertising Campaign Planning System – Project Description

## 1. Overview
The Media Advertising Campaign Planning System is a hybrid multi-tenant SaaS platform built with Django/Python (backend), React/TypeScript (frontend), and PostgreSQL 16. It supports multi-language (English, Amharic) and multi-currency operations. Core capabilities include campaign planning, media plan generation, rate card management, monitoring reconciliation, licensing, and export features (Excel/PDF).

The app is designed for agencies and planners to manage advertising campaigns across TV and Radio stations, track performance, and ensure accountability with reconciled reports.

---

## 2. Workflow (High-Level)

1. **License Validation**  
   - Offline license validation based on machine-hash key.  
   - App restricts usage if not validated.  

2. **Initial Data Setup**  
   - Upload (batch/single):  
     - Stations (with network, city, motto, call sign, management/marketing contacts).  
     - Show categories.  
     - Audience categorizations (linked to show categories).  
     - Dayparts (time blocks).  
     - Rate cards (price per second by show/day).  
     - Sponsorship prices (per 30/60/120 min blocks).  
   - Planners can also create/edit these one by one.  
```markdown
# Media Planner — Project Description (enhanced)

## Purpose
Media Planner is a hybrid SaaS web application for creating, scheduling, tracking, and reporting TV and Radio advertising campaigns for agencies and their clients.

This document is intended to be an actionable spec for implementation: explicit field types, API shapes, RBAC rules, tenancy guidance, and next development steps.

### Summary of stack
- Backend: Django 4.x + Django REST Framework, PostgreSQL 16
- Frontend: React + TypeScript (Vite), Tailwind CSS, shadcn/ui
- Background jobs: Celery + Redis
- Object storage: S3 (AWS) or MinIO for local/dev
- Exports: background jobs producing Excel (openpyxl/pandas) and PDF (WeasyPrint/ReportLab)
- Licensing: offline alphanumeric keys bound to a machine fingerprint

---

## Core Entities (fields, types, and requiredness)
Notes: use UUID PKs for public-facing tables; created_at/updated_at on all tables. tenant_id is required on tenant-scoped models.

1) Tenant
  - id: UUID (PK)
  - name: string (required, max 255)
  - license_key: string (nullable)
  - settings: jsonb (currency: string, timezone: string, language: string)
  - created_at, updated_at

2) User
  - id: UUID
  - tenant_id: UUID (FK, required)
  - username: string (required, unique per tenant)
  - email: string (required)
  - full_name: string (optional)
  - role: enum['Admin','Planner','Client','StationRep'] (required)
  - is_active: bool (default true)

3) Station
  - id: UUID
  - tenant_id: UUID (FK, required)
  - name: string (required)
  - type: enum['TV','Radio']
  - region: string (optional)
  - contact_info: jsonb (emails/phones)

4) Show
  - id: UUID
  - station_id: UUID (FK, required)
  - name: string (required)
  - genre: string (optional)
  - default_dayparts: Array<UUID> (optional)

5) Daypart
  - id: UUID
  - name: string (required)
  - start_time: time
  - end_time: time

6) RateCard
  - id: UUID
  - station_id: UUID (FK)
  - show_id: UUID (FK, nullable)
  - daypart_id: UUID (FK)
  - price: decimal (required)
  - currency: string (3-letter ISO)

7) Campaign
  - id: UUID
  - tenant_id: UUID (FK, required)
  - name: string (required)
  - advertiser_name: string (optional)
  - target_audience: string (optional)
  - start_date: date
  - end_date: date
  - budget: decimal
  - status: enum['draft','active','paused','completed','cancelled'] (default 'draft')

8) MediaPlan (Spot)
  - id: UUID
  - campaign_id: UUID (FK, required)
  - station_id: UUID (FK)
  - show_id: UUID (FK)
  - daypart_id: UUID (FK)
  - date: date
  - spots: integer
  - price_per_spot: decimal (optional)
  - status: enum['draft','pending','accepted','locked','rejected'] (default 'draft')

9) MediaBrief
  - id: UUID
  - campaign_id: UUID (FK)
  - title: string
  - description: text
  - attachments: relation to stored files

10) MonitoringReport
  - id: UUID
  - campaign_id: UUID
  - file: stored file reference
  - metrics: jsonb (spots_aired:int, reach:int, impressions:int, notes:string)
  - uploaded_at: timestamp

11) License
  - id: UUID
  - tenant_id: UUID
  - license_key: string
  - machine_hash: string
  - issued_at: timestamp
  - expiry_date: date (nullable)

---

## API contract examples (unchanged shapes, but with types and conventions)

General conventions:
- All list endpoints must implement pagination (offset/limit or cursor) and support filtering by tenant_id for admin tooling.
- Standard error response shape (400 validation, 401 auth, 403 permission, 404 not found):

```json
{ "detail": "Human readable message", "errors": { "field": ["error message"] } }
```

### Create Campaign
POST /api/campaigns/
Request body types (example):
```json
{
  "tenant_id": "uuid",
  "name": "string",
  "target_audience": "string",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "budget": 50000.00
}
```

Response (201): minimal resource representation and status.

### Add MediaPlan Spot
POST /api/media-plans/
Body: campaign_id (UUID), station_id (UUID), show_id (UUID), daypart_id (UUID), date (YYYY-MM-DD), spots (int)

Response: 201 with MediaPlan object (see fields above).

### Upload Monitoring Report
POST /api/monitoring-reports/ (multipart/form-data)
Fields: campaign_id (UUID), file (binary), metrics (json)

Response: 201 with MonitoringReport object and uploaded_at timestamp.

---

## Tenancy & RLS notes
- Approach: row-level tenancy using a required `tenant_id` column and PostgreSQL Row-Level Security (RLS) policies.
- Application roles (DB user used by the app) should be configured to SET LOCAL ROLE or use session variables for current_tenant to simplify RLS policies.
- Migration path: maintain a central `tenants` table; ensure migrations do not accidentally leak data across tenants. Test migrations on staging.

When to consider schema-per-tenant: extremely high data isolation/regulatory requirements or when tenants need per-customer customizations at DB level.

---

## RBAC (role → allowed actions) — short matrix

Admin:
- Full CRUD on tenant-scoped resources (users, stations, shows, ratecards, campaigns)
- Manage licenses and tenant settings

Planner:
- Create/update campaigns and media plans
- Upload briefs and view monitoring reports

Client:
- View campaigns/media plans assigned to them
- Confirm/accept media plans (when workflow requires client acceptance)

StationRep:
- View incoming media plan invites for their station
- Accept/reject station-side offers

Implementation notes: use DRF permissions + object-level checks (e.g., IsAdminOrReadOnly + custom IsTenantMember). Enforce role checks in viewsets/services for destructive actions.

---

## MediaPlan status transitions
- draft -> pending (when submitted to stations or to clients)
- pending -> accepted (when station/client accepts)
- accepted -> locked (finalized; no edits)
- pending -> rejected (station/client rejects; back to draft)

Enforce transitions in service layer; store an audit log of transitions.

---

## License activation flow (offline)
1. Client generates `machine_hash` locally (MAC addresses + disk UUIDs hashed) and sends it to support or a license UI when offline activation is needed.
2. Admin/License server generates a license_key bound to `machine_hash` and returns an alphanumeric key with metadata (issued_at, expiry_date).
3. Client enters license_key in admin UI; backend validates the signature and machine_hash, stores `license` record for tenant, and flips tenant to active state.
4. Periodic offline checks: client may validate hash/expiry locally; when unable to reach license server, the app falls back to cached license until expiry.

Failure modes: mismatched machine_hash, expired key, tampering. Provide support override path (time-limited emergency key) and logging for activation attempts.

---

## Indexing, PKs, and performance notes
- Use UUID primary keys for external tables. Add btree indexes on (tenant_id), (campaign_id), and date fields used in filters.
- Composite indexes for common queries: (tenant_id, created_at), (campaign_id, date).
- For large list endpoints, prefer cursor pagination for stable ordering.

---

## Pagination, filtering, sorting (examples)
- /api/campaigns/?tenant_id=...&limit=25&offset=0&ordering=-start_date
- /api/media-plans/?campaign_id=...&date__gte=2025-10-01&date__lte=2025-10-31

---

## ER adjacency (quick)
- Tenant 1--* User
- Tenant 1--* Campaign
- Campaign 1--* MediaPlan
- Station 1--* Show
- Station 1--* RateCard
- MediaPlan -> (Station, Show, Daypart)

---

## Next steps (recommended immediate work)
1. Add required/optional markers in this file (done) and review with the backend devs.
2. Scaffold Django models & migrations from the field list (I can generate these next).
3. Produce minimal OpenAPI spec for campaigns/media-plans/monitoring-reports.
4. Create `.env.example` and add pre-commit config to enforce `coding_guidelines.md`.

---

End of spec.
```
- **Dashboard** with quick stats (campaigns, spots, performance).  
- **Station/Show Management** grid with import/export options.  
- **Campaign Wizard**:  
  1. Select audience & budget.  
  2. Add shows/stations (grid by station/show category).  
  3. Review & override pricing.  
  4. Export plan.  
- **Monitoring Reports** upload & reconciliation dashboard.  

---

## 8. Testing Strategy

- **Unit Tests**:  
  - Entities: CRUD for Tenant, Station, Show, RateCard, Campaign, MediaPlan.  
  - API endpoints (create campaign, generate media plan, upload monitoring report).  
- **Integration Tests**:  
  - Campaign → MediaPlan → MonitoringReport flow.  
  - Data import (stations, rate cards).  
- **Frontend Tests**:  
  - UI rendering of campaign wizard, plan grids.  
  - File upload validation.  
- **End-to-End Tests**:  
  - Planner workflow: license → setup → campaign → plan → export → monitoring report.  

---
