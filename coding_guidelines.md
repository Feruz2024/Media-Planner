# Coding Guidelines

## General Principles
- Follow **PEP 8** for Python code.
- Use **ESLint + Prettier** for JavaScript/React code.
- Follow **Django best practices** for project structure and security.
- Ensure consistent naming conventions across backend and frontend.

---

## Python (Django)
- Use **snake_case** for variables and functions.
- Use **PascalCase** for class names.
- Keep views thin and business logic in **services** or **managers**.
- Write unit tests with `pytest` or Django's `TestCase`.
- Use environment variables for secrets (never commit credentials).

---

## JavaScript / React
- Use **camelCase** for variables and functions.
- Use **PascalCase** for components.
- Organize components inside `/components` and pages inside `/pages`.
- Prefer **functional components** with hooks instead of class components.
- Handle API calls using Axios or Fetch in a separate `/services` directory.

---

## Database (PostgreSQL)
- Use singular names for tables (e.g., `Station`, `Show`, `RateCard`).
- All primary keys should be `id` (auto-increment integer or UUID).
- Define foreign keys with `ON DELETE CASCADE` where appropriate.
- Ensure migrations are created and tested before pushing.

---

## Git & Collaboration
- Create feature branches from `main` (e.g., `feature/auth-system`).
- Commit messages must be clear and follow conventional commits:
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation updates
  - `refactor:` for code improvements
- Always open a Pull Request for review before merging.

---

## Testing
- Write unit tests for backend (pytest or Django tests).
- Write React component tests with **Jest + React Testing Library**.
- Ensure CI (GitHub Actions) passes before merging.

---

## Security & Quality
- Sanitize all user inputs.
- Apply authentication and authorization checks consistently.
- Use HTTPS in production.
- Run **linters** and **formatters** before commits.
- Use Docker for consistent environments.

---

## Documentation
- Maintain an updated **README**.
- Keep **ERD diagrams** updated when the schema changes.
- Add docstrings for all functions and classes.

---
