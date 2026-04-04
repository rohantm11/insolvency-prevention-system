# Insolvency Prevention System — Technical Overview (~60 min study)

This document is a complete technical overview of the codebase: structure, frontend, backend, API connection, data flow, config, and how to run the project. Use it as ~60 minutes of study material.

---

## 1. Project Structure

### Overall folder/file structure

```
insolvency-prevention-system/
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── main.py             # Single entry: FastAPI app, all routes, lifespan
│   │   ├── config.py           # Pydantic Settings (APP_NAME, DATABASE_URL, CORS, MODEL_PATH)
│   │   ├── models/
│   │   │   ├── schemas.py      # Pydantic request/response models
│   │   │   └── __init__.py
│   │   ├── routes/             # Empty; routes live in main.py
│   │   │   └── __init__.py
│   │   └── services/
│   │       ├── enhanced_prediction.py   # ML + market intelligence combined
│   │       ├── market_intelligence.py   # News, sector, economic APIs + scraping
│   │       ├── pdf_generator.py         # ReportLab PDFs (insolvency, layoff)
│   │       └── __init__.py
│   ├── tests/
│   │   └── test_health.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── Dockerfile.dev
├── frontend/                   # React + Vite SPA
│   ├── src/
│   │   ├── App.tsx             # Router, Layout, lazy-loaded page routes
│   │   ├── main.tsx            # React root, ErrorBoundary
│   │   ├── index.css           # Tailwind + custom CSS (fonts, dark theme, keyframes)
│   │   ├── routes.tsx          # Lazy page components + preloadRoute()
│   │   ├── components/         # Reusable UI (Layout, RiskGauge, ShapChart, etc.)
│   │   ├── pages/              # Route-level components (Landing, Dashboard, etc.)
│   │   ├── context/            # ThemeContext, ToastContext
│   │   ├── services/
│   │   │   └── api.ts          # Axios client + all API functions
│   │   ├── types/              # TypeScript types for API responses
│   │   ├── constants/           # tooltipCopy, watchlist
│   │   └── remotion/           # Remotion video components (BackgroundVideo, etc.)
│   ├── package.json
│   ├── vite.config.ts          # React plugin, proxy /api → backend
│   ├── tailwind.config.js
│   └── Dockerfile
├── ml_models/                  # ML code (loaded by backend at startup)
│   ├── insolvency_predictor.py # XGBoost + SHAP for company insolvency
│   ├── employee_scorer.py      # XGBoost + SHAP for employee attrition/layoff
│   ├── insolvency_predictor_v2.py
│   └── __init__.py
├── data/                       # CSV data, analysis history, data loaders
│   ├── company_data.csv, employee_data.csv   # Used by backend to train if no .pkl
│   ├── company_train.csv, employee_train.csv
│   ├── analysis_history.json   # Written by backend for Dashboard “recent analyses”
│   ├── data_loader.py         # Load/generate company & employee DataFrames
│   ├── generate_dummy_data.py
│   ├── good/, bad/, generated/ # Sample/generated CSVs
│   └── ...
├── scripts/
│   ├── generate_data.py        # Generate company/employee training CSVs
│   ├── train_models.py         # Train and save .pkl to ml_models/trained_models/
│   ├── generate_test_companies.py, generate_single_company_files.py
│   ├── test_models.py, stress_tests.py, demo.py
│   └── ...
├── ml_models/trained_models/   # Persisted models (created at runtime or by scripts)
│   ├── insolvency_model.pkl
│   └── employee_model.pkl
├── .env.example                # Backend/frontend/env and optional API keys
├── docker-compose.yml          # backend + frontend services
├── docker-compose.dev.yml, docker-compose.prod.yml
├── deploy.sh
├── README.md
├── SETUP_FIRST_RUN.md
└── TECHNICAL_OVERVIEW.md       # This file
```

### Main modules/packages

| Area | Location | Purpose |
|------|----------|---------|
| **Backend API** | `backend/app/main.py` | FastAPI app, CORS, lifespan, all HTTP endpoints |
| **Backend config** | `backend/app/config.py` | `Settings` (pydantic-settings): APP_NAME, DATABASE_URL, CORS_ORIGINS, MODEL_PATH |
| **Request/response models** | `backend/app/models/schemas.py` | Pydantic: `CompanyFinancialData`, `InsolvencyAnalysisResponse`, `EmployeeData`, `MarketIntelligenceResponse`, etc. |
| **ML – insolvency** | `ml_models/insolvency_predictor.py` | `InsolvencyPredictor`: XGBoost, Altman Z-Score, SHAP |
| **ML – employee** | `ml_models/employee_scorer.py` | `EmployeeScorer`: XGBoost, retention/layoff, SHAP |
| **Services** | `backend/app/services/` | `EnhancedPredictionService`, `MarketIntelligenceService`, `PDFReportGenerator` |
| **Frontend app** | `frontend/src/App.tsx` | React Router, Layout, lazy routes |
| **Frontend API layer** | `frontend/src/services/api.ts` | Axios instance + all API functions |
| **Frontend routing** | `frontend/src/routes.tsx` | Lazy page components + `preloadRoute(path)` |

---

## 2. Frontend

### Framework/library

- **React 19** with **TypeScript**.
- **Vite 7** for dev server and build (`vite.config.ts`).
- **react-router-dom** (v7) for routing.

### UI structure (pages, components, routing)

- **Entry:** `main.tsx` → `App.tsx` (wrapped in `ErrorBoundary`).
- **App.tsx:** `ThemeProvider` → `ToastProvider` → `Router` → `Layout` → `Routes`.
- **Routes (all in App.tsx):**
  - `/` → `Landing`
  - `/dashboard` → `Dashboard`
  - `/insolvency` → `InsolvencyAnalysis`
  - `/employees` → `EmployeeScoring`
  - `/layoffs` → `LayoffSimulation`
  - `/reports` → `Reports`
  - `/compare` → `Compare`
- **Lazy loading:** All routes except Landing are loaded via `lazy(() => import('./pages/...'))` with a `Suspense` fallback (`PageFallback` with `LoadingSpinner`).
- **Layout** (`components/Layout.tsx`): Wraps all routes; includes `AnimatedBackground`, optional Remotion `BackgroundVideo`, `FloatingNav`, theme toggle. Uses `preloadRoute(path)` from `routes.tsx` for hover preload.
- **Pages:** `Landing`, `Dashboard`, `InsolvencyAnalysis`, `EmployeeScoring`, `LayoffSimulation`, `Reports`, `Compare`.
- **Reusable components (examples):** `Layout`, `FloatingNav`, `RiskGauge`, `ShapChart`, `DataTable`, `FileUpload`, `LoadingSpinner`, `Skeleton`, `AnimatedButton`, `AnimatedPage`, `CountUp`, `Tooltip`, `AnimatedBackground`, `LandingBackground`, `TerminalBlock`, `RotatingCube`, `ErrorBoundary`, `CustomCursor`. Exported from `components/index.ts`.

### Styling

- **Tailwind CSS** (utility-first). Config: `frontend/tailwind.config.js` (content: `./index.html`, `./src/**/*.{js,ts,jsx,tsx}`; `darkMode: 'class'`; custom colors: `dark.*`, `primary.*`, `accent.*`, `highlight.*`; custom fonts: `sans` (Inter), `heading` (Plus Jakarta Sans), `mono` (JetBrains Mono); custom shadows and font sizes).
- **Global CSS:** `frontend/src/index.css` — `@tailwind base/components/utilities`; Google Fonts import; base styles for `html`/`body`/`#root`; `.card` and `section` classes; dark background; `@layer base` and keyframes (e.g. `gradientShift`).
- **Component styling:** Inline Tailwind via `className` (e.g. `className="space-y-6"`, `className="text-3xl font-bold text-slate-800 dark:text-white"`). No CSS modules or styled-components in use.

### State management

- **No Redux/Zustand.** State is local (useState/useReducer) and context:
  - **ThemeContext** (`context/ThemeContext.tsx`): theme (e.g. light/dark), `toggleTheme`, persisted (e.g. localStorage).
  - **ToastContext** (`context/ToastContext.tsx`): toasts array, `addToast`, `removeToast`, helpers like `success`, `error`; uses Framer Motion for animations.
- **Server state:** API calls are made ad hoc from pages via `api.ts`; no React Query or SWR. Loading/error state is handled per page (useState around async calls).

---

## 3. Backend

### Framework/runtime

- **FastAPI** (Python). Served by **Uvicorn** (ASGI). Python 3.11+.

### Route/endpoint organization

- **All routes are defined in one file:** `backend/app/main.py`. There are no separate `APIRouter` includes; `backend/app/routes/` is effectively unused.
- **Endpoint groups:**
  - **Root / health:** `GET /`, `GET /api/health`, `GET /api/analyses/recent`
  - **Templates:** `GET /api/templates/company`, `GET /api/templates/employee`
  - **Financial:** `POST /api/financial/analyze`, `POST /api/financial/upload-single`, `POST /api/financial/upload`, `GET /api/financial/feature-importance`, `POST /api/financial/explain-row`, `POST /api/financial/analyze-enhanced`
  - **Employee:** `POST /api/employee/analyze`, `POST /api/employee/upload`, `POST /api/employee/simulate-layoff`, `GET /api/employee/feature-importance`, `POST /api/employee/explain-row`
  - **Reports:** `POST /api/reports/insolvency`, `POST /api/reports/layoff`, `POST /api/reports/generate`
  - **Market intelligence:** `POST /api/market-intelligence`

### Middleware, authentication, authorization

- **CORS:** `CORSMiddleware` in `main.py`: `allow_origins=["*"]`, `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`.
- **No authentication or authorization:** No JWT, API keys, or role checks in the codebase. Optional placeholders exist in `.env.example` (e.g. `SECRET_KEY`, `API_KEY`) but are not used in app code.

---

## 4. Frontend ↔ Backend Connection

### Communication style

- **REST over HTTP.** All client–server communication is JSON (or file upload/download) via **Axios**. No GraphQL, WebSockets, or tRPC.

### Where API calls are made

- **Single central module:** `frontend/src/services/api.ts`.
  - **Axios instance:** `const api = axios.create({ baseURL: API_BASE_URL, headers: { 'Content-Type': 'application/json' }, timeout: 60000 })`.
  - **Base URL:** `const API_BASE_URL = import.meta.env.VITE_API_URL || ''` (empty string → relative URLs; with Vite proxy, `/api` goes to backend).
- **Consumers (pages):**
  - **Dashboard.tsx:** `getRecentAnalyses(5)`, `getMarketIntelligence`
  - **InsolvencyAnalysis.tsx:** `analyzeCompany`, `uploadSingleCompany`, `uploadFinancialData`, `generateInsolvencyReport`, `downloadBlob`, `downloadCompanyTemplate`
  - **Compare.tsx:** `analyzeCompany`, `uploadSingleCompany`
  - **EmployeeScoring.tsx:** `uploadEmployeeData`, `downloadEmployeeTemplate`
  - **LayoffSimulation.tsx:** `simulateLayoffs`, `generateLayoffReport`, `downloadBlob`
  - **Reports.tsx:** `generateInsolvencyReport`, `generateLayoffReport`, `downloadBlob`, `downloadCompanyTemplate`
- **Other API usage:** Any page that needs health, templates, feature importance, explain-row, or market intelligence imports the corresponding function from `api.ts`.

### Base URL and proxy

- **Base URL:** Set by **VITE_API_URL** in the frontend. In dev, often `http://localhost:8000` (see `frontend/.env.example` and `SETUP_FIRST_RUN.md`). If unset, `api.ts` uses `''`, so requests are relative (e.g. `/api/health`).
- **Vite proxy** (`frontend/vite.config.ts`):  
  `server.proxy['/api']` → `target: 'http://127.0.0.1:8000'`, `changeOrigin: true`.  
  So with `VITE_API_URL` empty, browser requests to `/api/*` are proxied to the backend on port 8000.
- **Production:** `.env.example` documents `VITE_API_URL=/api` for production (frontend built with this; nginx or similar proxies `/api` to the backend).

---

## 5. Data Flow & Generation

### Where data originates

- **Company insolvency:**  
  - **Training:** CSV under `data/` (e.g. `company_data.csv`, `company_train.csv`) with columns matching `InsolvencyPredictor.FEATURE_COLUMNS` and a target (e.g. `is_bankrupt`).  
  - **Inference:** User input (form or CSV upload) → validated by `CompanyFinancialData` (schemas) → passed to `InsolvencyPredictor.predict` / `explain_prediction` and (optionally) `EnhancedPredictionService`.
- **Employee scoring/layoff:**  
  - **Training:** CSV (e.g. `data/employee_data.csv`, `data/employee_train.csv`) with columns matching `EmployeeScorer.FEATURE_COLUMNS` (categoricals encoded in the model).  
  - **Inference:** Form or CSV upload → validated by `EmployeeData` or parsed from CSV → `EmployeeScorer.predict` / `simulate_layoffs` / `explain_prediction`.
- **Dashboard “recent analyses”:** Backend appends entries to `data/analysis_history.json` in `_append_analysis()` and reads them in `_get_recent_analyses()` (both in `main.py`). No database used for this.
- **Market intelligence:** External sources: **NewsAPI**, **Alpha Vantage**, **FRED** (optional keys in `.env`), plus **BeautifulSoup**/httpx scraping fallbacks. Implemented in `backend/app/services/market_intelligence.py` and used by `MarketIntelligenceService` and `EnhancedPredictionService`.

### Database

- **No active DB for app logic.** `config.py` defines `DATABASE_URL: str = "sqlite:///./insolvency.db"` and `.env.example` mentions an optional `DATABASE_URL` for future use. No SQLAlchemy models or session usage in the main app; the app uses in-memory state, JSON file (`analysis_history.json`), and CSV/ML only.

### Data processing, transformation, ML inference

- **Backend (`main.py`):**
  - **Lifespan:** On startup, `load_models()` loads (or trains) `InsolvencyPredictor` and `EmployeeScorer` from `ml_models/trained_models/*.pkl`, and initializes `PDFReportGenerator`, `MarketIntelligenceService`, `EnhancedPredictionService`.
  - **CPU work offloaded:** Heavy work (predict, explain, simulate) runs in a thread pool via `asyncio.to_thread(_sync_analyze_company | _sync_upload_financial_bulk | _sync_simulate_layoffs`, etc.).
  - **Caching:** In-memory `_prediction_cache` (TTL 600s, max 2000 entries) keyed by hash of input; used for single-company and single-employee analyze and for explain-row.
  - **Numpy serialization:** `convert_numpy_types()` used so SHAP/numpy values are JSON-serializable.
- **ML models:**
  - **Insolvency:** `ml_models/insolvency_predictor.py` — `InsolvencyPredictor.train()`, `.predict()`, `.calculate_altman_zscore()`, `.explain_prediction()` (SHAP TreeExplainer).
  - **Employee:** `ml_models/employee_scorer.py` — `EmployeeScorer.train()`, `.predict()`, `.simulate_layoffs()`, `.explain_prediction()` (SHAP); label encoding for categoricals.
- **Enhanced prediction:** `backend/app/services/enhanced_prediction.py` — `EnhancedPredictionService.predict_insolvency_enhanced()` combines base ML prediction with `MarketIntelligenceService` output and returns adjusted probability, risk factors, and recommendations.
- **Data generation scripts:**  
  - **scripts/generate_data.py:** Generates company and employee CSVs (e.g. `company_train.csv`, `employee_train.csv`) for training.  
  - **data/generate_dummy_data.py**, **scripts/generate_test_companies.py**, **scripts/generate_single_company_files.py:** Additional data generation.  
  - **scripts/train_models.py:** Loads data from `data/` (or `data/generated/`), trains both models, saves `.pkl` into `ml_models/trained_models/`.  
  - **data/data_loader.py:** Central loading/contract for company and employee DataFrames used by training and other consumers.

---

## 6. Key Config Files

| File | Role |
|------|------|
| **frontend/package.json** | Scripts: `dev` (vite), `build` (tsc -b && vite build), `preview`, `lint`, `type-check`. Deps: react, react-dom, react-router-dom, axios, framer-motion, recharts, remotion, react-dropzone, lucide-react; dev: vite, @vitejs/plugin-react, tailwindcss, postcss, typescript, eslint. |
| **backend/requirements.txt** | fastapi, uvicorn, pydantic, pydantic-settings, python-multipart, python-dotenv; sqlalchemy (optional); numpy, pandas; scikit-learn, xgboost, shap; reportlab; httpx, beautifulsoup4, lxml. |
| **.env / .env.example** | Root `.env.example`: NODE_ENV, TAG, BACKEND_PORT, LOG_LEVEL, CORS_ORIGINS, DATABASE_URL (optional), FRONTEND_PORT, **VITE_API_URL** (/api or http://localhost:8000), MODEL_PATH, optional NEWS_API_KEY, FRED_API_KEY, ALPHA_VANTAGE_API_KEY, SECRET_KEY, API_KEY, Sentry, AWS, Docker registry. Frontend `frontend/.env.example`: optional **VITE_API_URL** (e.g. http://localhost:8000). |
| **frontend/vite.config.ts** | React plugin; `server.port: 5173`; `server.proxy['/api']` → `http://127.0.0.1:8000`. |
| **frontend/tailwind.config.js** | Content paths, darkMode: 'class', theme extensions (colors, fonts, shadows, fontSize). |
| **docker-compose.yml** | `backend` (build backend/, port 8000, volume `./data:/app/data:ro`, healthcheck on `/api/health`); `frontend` (build frontend/, build-arg VITE_API_URL=/api, port 3000:80, depends_on backend). Network `insolvency-network`. |
| **docker-compose.dev.yml / docker-compose.prod.yml** | Variants for dev vs prod. |
| **backend/Dockerfile** | Build and run backend (e.g. uvicorn). |
| **frontend/Dockerfile** | Build and serve frontend (e.g. nginx). |
| **deploy.sh** | Deployment script (usage depends on repo). |

There is no **pyproject.toml** in the repo; Python deps are managed only via **requirements.txt**.

---

## 7. How to Run the Project

### Backend

1. **Prepare environment (first time):**
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1   # Windows
   pip install -r requirements.txt
   ```
2. **Start API:**
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   - On first run, if `ml_models/trained_models/insolvency_model.pkl` and `employee_model.pkl` are missing, the app trains models using `data/company_data.csv` and `data/employee_data.csv` (can take a few minutes).
   - API: http://localhost:8000; docs: http://localhost:8000/docs.

### Frontend

1. **Install dependencies (first time):**
   ```powershell
   cd frontend
   npm install
   ```
2. **Start dev server:**
   ```powershell
   cd frontend
   npm run dev
   ```
   - App: http://localhost:5173. With default proxy, frontend calls `/api` which Vite proxies to http://127.0.0.1:8000.
   - If the API is on another host/port, set `VITE_API_URL` in `frontend/.env` (e.g. `VITE_API_URL=http://localhost:8000`).

### Build steps / scripts

- **Frontend build:** `npm run build` (runs `tsc -b && vite build`). Output in `frontend/dist/`.
- **Frontend preview (production build locally):** `npm run preview`.
- **Pre-train models (optional):** From project root with backend venv activated:
  ```powershell
  python scripts/train_models.py
  ```
  Expects training CSVs in `data/` or `data/generated/` (see script or `data/data_loader.py`). Creates/updates `ml_models/trained_models/*.pkl`.
- **Generate training data:** `python scripts/generate_data.py` (see script for options like `--healthy`, `--at-risk`, `--output-dir`).
- **Docker:** From project root, `docker-compose up` (or `-f docker-compose.dev.yml`) builds and runs backend and frontend; backend on 8000, frontend on 3000 with `VITE_API_URL=/api`.

---

## Quick reference: important file and function names

| Topic | File / function |
|-------|------------------|
| API entry | `backend/app/main.py` — `app = FastAPI(...)`, `lifespan`, `load_models()` |
| Health | `GET /api/health` → `health_check()` |
| Company analyze | `POST /api/financial/analyze` → `analyze_company(data)` → `_sync_analyze_company()` |
| Bulk financial | `POST /api/financial/upload` → `upload_financial_data(file)` → `_sync_upload_financial_bulk()` |
| Employee analyze | `POST /api/employee/analyze` → `analyze_employee(data)` → `_sync_analyze_employee()` |
| Layoff sim | `POST /api/employee/simulate-layoff` → `simulate_layoffs()` → `_sync_simulate_layoffs()` |
| Reports | `POST /api/reports/insolvency`, `POST /api/reports/layoff` → `_generate_insolvency_report()`, `_generate_layoff_report()` |
| Market intel | `POST /api/market-intelligence` → `get_market_intelligence(request)` → `MarketIntelligenceService.generate_report()` |
| Frontend API | `frontend/src/services/api.ts` — `api`, `getHealth`, `analyzeCompany`, `uploadFinancialData`, `getRecentAnalyses`, etc. |
| Insolvency ML | `ml_models/insolvency_predictor.py` — `InsolvencyPredictor`, `train`, `predict`, `calculate_altman_zscore`, `explain_prediction` |
| Employee ML | `ml_models/employee_scorer.py` — `EmployeeScorer`, `train`, `predict`, `simulate_layoffs`, `explain_prediction` |
| Schemas | `backend/app/models/schemas.py` — `CompanyFinancialData`, `InsolvencyAnalysisResponse`, `EmployeeData`, `MarketIntelligenceRequest/Response` |

---

*End of technical overview.*
