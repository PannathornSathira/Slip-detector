# Repository Guidelines

## Project Structure & Module Organization

- `backend/main.py` defines the FastAPI application and HTTP endpoints.
- `backend/services/` contains OCR, categorization, and processor-selection logic. Keep route handlers thin and place reusable business logic here.
- `backend/config/categories.json` stores merchant-to-category mappings and may be updated by the application.
- `backend/scratch/` and `model/` contain manual experiments for categorization and vision-language models.
- `frontend/src/pages/` holds route-level React views; `frontend/src/components/` contains reusable UI components.
- `frontend/src/assets/` and `frontend/public/` contain bundled and static assets respectively. Generated `frontend/dist/`, uploads, caches, and local environments should not be committed.

## Build, Test, and Development Commands

Run the backend from its directory so relative upload paths remain predictable:

```bash
cd backend
python -m pip install -r requirements.txt
python main.py
```

The API starts on `http://localhost:8000`. Run the frontend separately:

```bash
cd frontend
npm install
npm run dev
npm run lint
npm run build
npm run preview
```

These commands start Vite, lint JavaScript/JSX, create a production bundle, and serve that bundle locally.

## Coding Style & Naming Conventions

Use four spaces and `snake_case` for Python functions, variables, and modules; use `PascalCase` for classes. Keep service interfaces small and preserve type hints on FastAPI boundaries. In React, use functional components, `PascalCase` component filenames, and `camelCase` variables and handlers. Follow the existing JSX style and Tailwind utility classes. Run `npm run lint` before submitting frontend changes; ESLint uses the recommended JavaScript, React Hooks, and Vite rules.

## Testing Guidelines

There is currently no automated test framework or coverage threshold. Treat `backend/scratch/test_categorization.py` and `model/test_vlm.py <image-path>` as manual diagnostics, not a complete suite. For backend changes, exercise affected endpoints and include representative Thai and English receiver names. For frontend changes, run lint and build, then verify upload, editing, dashboard, and category-management flows. Add automated tests in a dedicated `backend/tests/` or colocated `*.test.jsx` file when introducing test infrastructure.

## Commit & Pull Request Guidelines

History uses short, imperative summaries such as `add local model feature`; keep commits focused and use the same style. Pull requests should explain behavior changes, list verification commands, note configuration or category-file changes, and link related issues. Include screenshots for visible UI changes and sample API requests/responses for endpoint changes.

## Security & Configuration

Copy `backend/.env.example` to `backend/.env` for local configuration. Never commit API keys, payment-slip images, uploaded files, or personal transaction data. Review edits to `categories.json` to avoid adding sensitive receiver information unintentionally.
