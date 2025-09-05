# GitHub Copilot Task Plan for Media Planner Project

## 📌 Overview
This task plan provides structured prompts, steps, tests, and progress entries to guide GitHub Copilot Agent Mode in **VS Code Insider** for building the Media Planner application.

The project is a **multi-tenant Media Advertising Campaign Planning Software** with:
- Django/Python backend (PostgreSQL, Celery, REST API)
- React/TypeScript frontend (shadcn/ui, Tailwind, charts)
- Multi-language & multi-currency support (English, Amharic)
- Offline licensing, file exports (PDF/Excel)
- Entities: Tenant, User, Network, Station, Show, ShowCategory, Audience, RateCard, Campaign, MediaPlan, MediaBrief, MonitoringReport, License

---

## 📂 Structure of Each Task
Each task includes:
1. **Part** → A logical project section (e.g., Backend Setup, Frontend UI)
2. **Step** → Specific implementation item
3. **Description** → Explanation of what to build
4. **Prompt for Agent** → Instruction for Copilot
5. **Test** → How to verify functionality
6. **Progress Entry** → Journal/log of completion

---

## 🧩 Task Plan

### Part 1: Project Setup
#### Step 1: Initialize Repository
- **Description:** Create a new repository and scaffold Django + React project structure.
- **Prompt for Agent:**  
  "Generate a Django backend with PostgreSQL setup and a React/TypeScript frontend using Vite. Configure Docker Compose to orchestrate Postgres, backend, and frontend."
- **Test:** Run `docker-compose up`, check both servers run at `localhost:8000` and `localhost:5173`.
- **Progress Entry:** Repository scaffolded and services confirmed running.

#### Step 2: Configure CI/CD
- **Description:** Add GitHub Actions workflow for testing, linting, and migrations.
- **Prompt for Agent:**  
  "Create `.github/workflows/ci.yml` with jobs for Python (pytest, flake8) and frontend (npm test, eslint)."
- **Test:** Push commit → workflow passes on GitHub.
- **Progress Entry:** CI pipeline green.

---

### Part 2: Backend Development (Django)
#### Step 3: Define Models
- **Description:** Implement entities: Tenant, User, Network, Station, Show, ShowCategory, Audience, RateCard, Campaign, MediaPlan, MediaBrief, MonitoringReport, License.
- **Prompt for Agent:**  
  "Write Django models for all entities with relationships (ForeignKey, ManyToMany) and constraints. Include fields like category (Tenant), city/motto/call sign (Station), audience (Show)."
- **Test:** Run `python manage.py makemigrations && migrate` without errors.
- **Progress Entry:** Models created and migrated.

#### Step 4: Expose REST API
- **Description:** Create DRF serializers & viewsets for each entity.
- **Prompt for Agent:**  
  "Generate DRF serializers and routers for all models, expose under `/api/v1/` namespace."
- **Test:** `GET /api/v1/tenants/` returns JSON list.
- **Progress Entry:** API endpoints tested with Postman.

---

### Part 3: Frontend Development (React/TypeScript)
#### Step 5: Authentication & Tenant Switching
- **Description:** Build login, logout, tenant selection.
- **Prompt for Agent:**  
  "Generate React components for login and tenant switcher using shadcn/ui and Tailwind. Connect with backend auth endpoints."
- **Test:** Login works, token saved, tenant context updates UI.
- **Progress Entry:** User authentication confirmed.

#### Step 6: Entity Management UIs
- **Description:** Create CRUD dashboards for Stations, Shows, Campaigns, RateCards.
- **Prompt for Agent:**  
  "Build grid/table views for each entity with search, filter, and CRUD dialogs."
- **Test:** Add/Edit/Delete entities reflect in DB via API.
- **Progress Entry:** CRUD operations verified.

---

### Part 4: Advanced Features
#### Step 7: Multi-language & Currency
- **Description:** Add i18n (English/Amharic) and currency conversion support.
- **Prompt for Agent:**  
  "Integrate i18next for language switching and implement currency formatting based on tenant settings."
- **Test:** Toggle language/currency updates UI and API responses.
- **Progress Entry:** Multi-language/currency confirmed.

#### Step 8: Reports & Monitoring
- **Description:** Generate PDF/Excel exports and monitoring dashboards.
- **Prompt for Agent:**  
  "Implement report generation with ReportLab (PDF) and openpyxl (Excel). Create React charts with recharts for monitoring spots (scheduled, transmitted, missed, gained)."
- **Test:** Downloaded reports match data in DB.
- **Progress Entry:** Reports tested and valid.

---

### Part 5: Deployment & Licensing
#### Step 9: Offline Licensing
- **Description:** Add license model with validation mechanism.
- **Prompt for Agent:**  
  "Create License model and middleware to validate license key. Deny access if invalid/expired."
- **Test:** Expired key blocks access; valid key allows system usage.
- **Progress Entry:** Licensing tested.

#### Step 10: Production Deployment
- **Description:** Deploy app to cloud with Docker.
- **Prompt for Agent:**  
  "Write Dockerfile and Compose for production with Nginx reverse proxy and Gunicorn for Django."
- **Test:** Production server runs correctly with HTTPS enabled.
- **Progress Entry:** Deployment successful.

---

## ✅ Visual Guide
- **ERD Diagram:** Entities and relations between Tenant, Network, Station, Show, Audience, Campaign, etc.  
- **Architecture Diagram:** Backend (Django + Celery + Postgres), Frontend (React/TS), S3, CI/CD pipeline.

---

## 📖 Usage Notes
- Start with **backend models + API**, then **frontend UI**.
- Use **CI/CD checks** as guardrails for correctness.
- Maintain **progress log** for accountability.

---

## 🏁 Final Note
This plan is structured for **step-by-step execution with GitHub Copilot Agent Mode in VS Code Insider**. Each task is self-contained, testable, and logged for traceability.
