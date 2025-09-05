# UI Development Guide

This guide explains the **frontend development practices** for the Media Advertising Campaign Planning System.

---

## Tech Stack
- **React** with **Vite** (or CRA if required)
- **TailwindCSS** for styling
- **shadcn/ui** components for consistency
- **Framer Motion** for animations
- **Axios** for API calls

---

## Folder Structure
```
/src
  /components     # Reusable components
  /pages          # Page-level components
  /layouts        # Common layouts
  /services       # API handlers
  /hooks          # Custom hooks
  /assets         # Images, fonts, static files
```

---

## Styling Rules
- Use **TailwindCSS** for all styling.
- Avoid inline styles unless absolutely necessary.
- Use **responsive utilities** (`sm:`, `md:`, `lg:`).

---

## Components
- Must be **functional components** with hooks.
- Keep components small and composable.
- Example naming:
  - `StationCard.jsx`
  - `ShowForm.jsx`
  - `RateCardTable.jsx`

---

## State Management
- Use React's built-in **useState, useReducer, useContext**.
- If global state grows, consider **Zustand** or **Redux Toolkit**.

---

## API Integration
- Keep API functions in `/services/api.js`.
- Always handle errors with `try/catch`.
- Show **loading** and **error states** in UI.

---

## Animations
- Use **Framer Motion** for transitions.
- Keep animations subtle and not distracting.

---

## Testing
- Use **Jest + React Testing Library**.
- Write tests for critical components like forms and tables.

---

## Accessibility
- Use semantic HTML tags (`<button>`, `<nav>`, `<header>`).
- Ensure all inputs have labels.
- Test with keyboard navigation.

---

## Deployment
- Build optimized production files with:
  ```bash
  npm run build
  ```
- Serve via **Nginx** or integrated with **Django templates**.

---
