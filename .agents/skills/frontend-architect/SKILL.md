---
name: frontend-architect-whatyousaid
description: Expert in React, Tailwind CSS, and i18next development. Use when creating or modifying frontend components, ensuring modern UI/UX standards, responsive design, and full internationalization (EN/PT-BR).
---

# Frontend Architect (WhatYouSaid)

This skill provides expert guidance for developing and maintaining the WhatYouSaid frontend dashboard. It focuses on a "Glassmorphism/Dark Mode" aesthetic, high performance, and seamless multi-language support.

## Core Principles

### 1. Internationalization (i18n)
- **ZERO Hardcoded Strings**: Never include visible text directly in JSX.
- **Hook Usage**: Always use `const { t } = useTranslation();` inside components.
- **Locale Files**: Update `frontend/src/locales/en.json` and `frontend/src/locales/pt-BR.json` simultaneously.
- **Namespace Organization**: Use nested keys (e.g., `settings.tabs.api`) to keep locale files organized.
- **Dynamic Values**: Use interpolation for dynamic strings: `t('key', { value: val })`.

### 2. UI/UX & Styling (Tailwind CSS)
- **Aesthetic**: Follow the project's Dark Mode theme using `zinc-900/950`, `emerald-500` for accents, and backdrop blurs.
- **Consistency**: Use existing color variables and spacing patterns.
- **Responsiveness**: Always use mobile-first breakpoints (`sm:`, `md:`, `lg:`).
- **Interactivity**: Use `motion/react` (Framer Motion) for smooth transitions and `lucide-react` for icons.
- **Layouts**: Prefer Flexbox and CSS Grid for structured layouts.

### 3. Technical Standards
- **TypeScript**: Ensure strict type safety for all props, states, and API responses.
- **Hooks**: Prefer functional components with hooks (`useState`, `useEffect`, `useCallback`, `useMemo`).
- **State Management**: Use `AppContext` for global state and specialized hooks (like `useIngestion`) for business logic.
- **Error Handling**: Wrap complex views in `ErrorBoundary` to prevent app-wide crashes.
- **Performance**: Use `useMemo` and `useCallback` to prevent unnecessary re-renders in heavy components.

## Specialized Workflows

### Creating a New Component
1. **Analyze Requirements**: Identify the purpose and necessary data.
2. **Scaffold**: Create the `.tsx` file in `frontend/src/components/`.
3. **Define Props**: Create an interface for the component props.
4. **Implement UI**: Use Tailwind for styling, adhering to the "Glassmorphism" theme.
5. **Add i18n**: Extract all strings to locale files.
6. **Integrate**: Add the component to the main view or parent component.
7. **Validate**: Test responsiveness and language switching.

### Modifying Existing UI
1. **Research**: Use `grep_search` to find the relevant component and its usages.
2. **Surgical Update**: Apply changes while preserving existing logic and styles.
3. **i18n Audit**: Check if any new strings were added or existing ones modified.
4. **Clean up**: Remove debug logs (`console.log`) before finishing.

## Reference Material

- **Icons**: Use `lucide-react`.
- **Animations**: Use `motion/react`.
- **API**: Use the centralized `api` service in `frontend/src/services/api.ts`.
- **Global State**: Check `frontend/src/store/AppContext.tsx`.
