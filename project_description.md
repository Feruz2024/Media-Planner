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

3. **Campaign Creation**  
   - Planner creates campaign with:  
     - Budget, target audience, region.  
     - References uploaded entities (stations, shows, pricing).  
     - Campaign assets (briefs, storyboards, media files).  
   - Planner can override spot/sponsorship pricing (e.g., agency discounts) or add free spots.  

4. **Media Plan Drafting**  
   - Planner creates draft plan by:  
     - Selecting shows directly.  
     - Selecting by station → show category → show.  
     - Selecting by show category only (auto-assigns all matching shows).  
   - Draft includes:  
     - Spots by station, show, daypart, weekday.  
     - Total spots per campaign, per station, and per show/day combination.  

5. **Approval & Export**  
   - Media plan reviewed internally.  
   - Export to Excel/PDF for client sharing.  

6. **Monitoring Report Integration**  
   - External monitoring agency provides spot transmission reports.  
   - Reports uploaded and reconciled against planned spots:  
     - Scheduled / Transmitted / Missed / Gained.  
   - Campaign transmission performance report generated.  

---

## 3. Feature List

- **Licensing & Security**  
  - Offline machine-hash license validation.  
- **Data Management**  
  - CRUD + bulk import (CSV/Excel) for stations, networks, shows, categories, audiences, dayparts, rate cards.  
- **Campaign Planning**  
  - Campaign creation with budget, audience, assets.  
  - Media plan drafting via flexible selection workflows.  
  - Manual pricing overrides and zero-cost spots.  
- **Media Plan Management**  
  - Track spots by campaign, station, show, day.  
  - Export to Excel/PDF.  
- **Monitoring & Reconciliation**  
  - Upload monitoring reports.  
  - Compare scheduled vs transmitted vs missed vs gained spots.  
- **Multi-Tenant & Localization**  
  - Row-level tenancy.  
  - Multi-language support (English, Amharic).  
  - Multi-currency support.  

---

## 4. User Stories

### As an **Admin**
- I can create/manage tenants.  
- I can manage users (planners).  
- I can configure system-wide settings (localization, licensing).  

### As a **Planner**
- I can validate license to start using the app.  
- I can batch/single upload stations, shows, categories, rate cards.  
- I can create campaigns with budget, audience, and media assets.  
- I can create media plans by:  
  - Selecting shows directly.  
  - Selecting by station → show category → show.  
  - Selecting by show category.  
- I can override spot pricing or set zero-cost spots.  
- I can generate media plan exports (Excel/PDF).  
- I can upload monitoring reports and see reconciled results.  

---

## 5. Backend Design

### Entities
- **Tenant**: `id, name, category, locale, currency`  
- **User**: `id, tenant_id, role, name, email, password`  
- **Network**: `id, name, description`  
- **Station**: `id, network_id, city, motto, call_sign, management_contact, marketing_contact`  
- **ShowCategory**: `id, name, description`  
- **AudienceCategory**: `id, name, description`  
- **Show**: `id, station_id, category_id, audience_id, name, description, schedule_days`  
- **Daypart**: `id, name, start_time, end_time`  
- **RateCard**: `id, station_id, show_id, weekday, price_per_second`  
- **SponsorshipPrice**: `id, show_id, block_length, price`  
- **Campaign**: `id, tenant_id, name, budget, target_audience, region, assets`  
- **MediaPlan**: `id, campaign_id, station_id, show_id, day, num_spots, price_overridden`  
- **MonitoringReport**: `id, campaign_id, station_id, show_id, timestamp, status`  

### Relationships
- `Station` belongs to `Network`.  
- `Show` belongs to both `ShowCategory` and `AudienceCategory`.  
- `RateCard` ties station + show + weekday → price.  
- `Campaign` references shows/stations through `MediaPlan`.  
- `MonitoringReport` references campaigns and spots.  

---

## 6. API Examples

### Create Campaign (POST)
```json
{
  "tenant_id": "t123",
  "name": "Enjoy Campaign",
  "budget": 10000,
  "target_audience": "Urban Youth",
  "region": "Addis Ababa",
  "assets": ["brief.pdf", "storyboard.png"]
}
```

**Response**
```json
{ "id": "c567", "status": "created" }
```

### Get Media Plan by Campaign (GET)
**Request**
```
/api/campaigns/c567/mediaplan
```

**Response**
```json
{
  "campaign_id": "c567",
  "plans": [
    {
      "station": "EBS TV",
      "show": "News",
      "weekday": "Monday",
      "spots": 3,
      "price_per_second": 25,
      "total_cost": 2475
    }
  ]
}
```

### Upload Monitoring Report (POST)
```json
{
  "campaign_id": "c567",
  "station": "EBS TV",
  "show": "News",
  "timestamp": "2025-05-02T12:05:13",
  "status": "transmitted"
}
```

**Response**
```json
{ "status": "recorded" }
```

---

## 7. Frontend Design

### UI Elements
- **Login / License Validation** screen.  
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
