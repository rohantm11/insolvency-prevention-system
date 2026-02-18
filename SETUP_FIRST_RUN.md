# First-time setup (this device)

This file was generated to get the project ready on your machine. Follow any steps that still apply.

## Done for you

- **Backend venv:** `backend/venv` created. Python dependencies were installed (if pip reported "file in use", see below).
- **Frontend .env:** `frontend/.env` created with `VITE_API_URL=http://localhost:8000`.
- **Data files:** `data/company_data.csv` and `data/employee_data.csv` copied from `data/generated/` so the backend can train models on first start if needed.
- **Models directory:** `ml_models/trained_models/` created (backend will save trained models here).

## If backend pip install had errors

If you saw `WinError 32` or "file in use" when installing Python packages:

1. Close any other terminals or IDEs using this project.
2. Open a new terminal and run:

   ```powershell
   cd "c:\Users\Milan\OneDrive\Desktop\insolvency-prevention-system\backend"
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

## Frontend: install Node dependencies

Node.js was not found in PATH on this machine. To install frontend dependencies:

1. Install **Node.js 20+** from https://nodejs.org (LTS).
2. Restart your terminal (or IDE) so `npm` is in PATH.
3. Run:

   ```powershell
   cd "c:\Users\Milan\OneDrive\Desktop\insolvency-prevention-system\frontend"
   npm install
   ```

## How to run the project

1. **Start the backend** (from project root or backend folder):

   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

   On first run the backend may train ML models (using `data/company_data.csv` and `data/employee_data.csv`); this can take a few minutes.

2. **Start the frontend** (in a second terminal, after `npm install`):

   ```powershell
   cd frontend
   npm run dev
   ```

3. Open **http://localhost:5173** in your browser. The app will call the API at http://localhost:8000 (set in `frontend/.env`).

## Optional: pre-train models

To train and save models before starting the server (so the first API start is faster), from project root with backend venv activated:

```powershell
# From project root, with backend venv active
python scripts/train_models.py
```

Note: `scripts/train_models.py` expects `data/generated/company_train.csv` and `data/generated/employee_train.csv`. If those don't exist, the backend will still train on first start using `data/company_data.csv` and `data/employee_data.csv`.
