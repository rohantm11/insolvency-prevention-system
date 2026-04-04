"""
FastAPI application entry point for the Insolvency Prevention System.
"""

import asyncio
import hashlib
import io
import json
import sys
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse


def convert_numpy_types(obj: Any) -> Any:
    """Recursively convert numpy types to native Python types."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    return obj

# Add project root to path for ML model imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ml_models.insolvency_predictor import InsolvencyPredictor
from ml_models.employee_scorer import EmployeeScorer

from app.config import settings
from app.models.schemas import (
    HealthResponse,
    CompanyFinancialData,
    InsolvencyAnalysisResponse,
    InsolvencyPrediction,
    InsolvencyExplanation,
    InsolvencyBulkResponse,
    FeatureImportanceResponse,
    EmployeeData,
    EmployeeAnalysisResponse,
    EmployeePrediction,
    EmployeeExplanation,
    EmployeeBulkResponse,
    LayoffSimulationResponse,
    LayoffRecommendation,
    InsolvencyReportRequest,
    LayoffReportRequest,
    # Market Intelligence schemas
    EnhancedAnalysisRequest,
    EnhancedPredictionResponse,
    MarketIntelligenceRequest,
    MarketIntelligenceResponse,
    NewsArticleResponse,
    SectorDataResponse,
    EconomicIndicatorsResponse,
    RiskFactor,
    AnalysisHistoryEntry,
    RecentAnalysesResponse,
)
from app.services.pdf_generator import PDFReportGenerator
from app.services.market_intelligence import MarketIntelligenceService
from app.services.enhanced_prediction import EnhancedPredictionService


# Global model instances
insolvency_model: InsolvencyPredictor | None = None
employee_model: EmployeeScorer | None = None
pdf_generator: PDFReportGenerator | None = None
market_intelligence_service: MarketIntelligenceService | None = None
enhanced_prediction_service: EnhancedPredictionService | None = None

# In-memory prediction cache (key -> (response_dict, timestamp))
_prediction_cache: dict[str, tuple[Any, float]] = {}
CACHE_TTL_SECONDS = 600  # 10 minutes
CACHE_MAX_SIZE = 2000

# Analysis history for Dashboard (persisted to JSON)
ANALYSIS_HISTORY_MAX_ENTRIES = 500
_analysis_history_path: Path | None = None


def _get_analysis_history_path() -> Path:
    global _analysis_history_path
    if _analysis_history_path is None:
        _analysis_history_path = project_root / "data" / "analysis_history.json"
        _analysis_history_path.parent.mkdir(parents=True, exist_ok=True)
    return _analysis_history_path


def _append_analysis(
    analysis_type: Literal["Company Analysis", "Employee Scoring", "Layoff Simulation"],
    name: str,
    result: str,
    score: str | None = None,
    payload: dict[str, Any] | None = None,
) -> None:
    """Append an analysis entry to history (for Dashboard)."""
    try:
        path = _get_analysis_history_path()
        entries: list[dict] = []
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                entries = json.load(f)
        entry = {
            "id": str(uuid.uuid4()),
            "type": analysis_type,
            "name": name,
            "result": result,
            "score": score,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "payload": payload or {},
        }
        entries.insert(0, entry)
        entries = entries[:ANALYSIS_HISTORY_MAX_ENTRIES]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)
    except Exception:
        pass


def _get_recent_analyses(limit: int = 10) -> list[AnalysisHistoryEntry]:
    """Return most recent analysis entries."""
    try:
        path = _get_analysis_history_path()
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as f:
            entries = json.load(f)
        out = []
        for e in entries[:limit]:
            out.append(AnalysisHistoryEntry(**e))
        return out
    except Exception:
        return []


def _generate_executive_summary(
    company_name: str,
    risk_category: str,
    z_score: float,
    z_score_zone: str,
    probability_of_distress: float,
    top_risk_drivers: list[dict],
) -> str:
    """Generate a plain-language executive summary for the analysis."""
    name = company_name or "This company"
    pct = round(probability_of_distress * 100, 1)
    if risk_category == "Low" or z_score_zone == "Safe":
        summary = (
            f"{name} is in the Safe Zone (Z-Score {z_score:.2f}) with low insolvency risk. "
            f"Probability of distress is {pct}%. "
        )
    elif risk_category == "High" or z_score_zone == "Distress":
        summary = (
            f"{name} is in the Distress Zone (Z-Score {z_score:.2f}) with high insolvency risk. "
            f"Probability of distress is {pct}%. "
        )
    else:
        summary = (
            f"{name} is in the Grey Zone (Z-Score {z_score:.2f}) with moderate insolvency risk. "
            f"Probability of distress is {pct}%. "
        )
    if top_risk_drivers:
        drivers = [d.get("feature", d.get("name", "")) for d in top_risk_drivers[:3] if isinstance(d, dict)]
        if drivers:
            summary += "Key drivers of risk: " + ", ".join(drivers).replace("_", " ") + "."
    return summary


def _cache_key_from_dict(data: dict) -> str:
    """Stable hash for cache key from a dict (e.g. model_dump())."""
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def _get_cached(key: str) -> Any | None:
    """Return cached response dict if present and not expired, else None."""
    if key not in _prediction_cache:
        return None
    resp, ts = _prediction_cache[key]
    if time.time() - ts > CACHE_TTL_SECONDS:
        del _prediction_cache[key]
        return None
    return resp


def _set_cached(key: str, value: Any) -> None:
    """Store response in cache; evict expired entries if over max size."""
    if len(_prediction_cache) >= CACHE_MAX_SIZE:
        now = time.time()
        expired = [k for k, (_, ts) in _prediction_cache.items() if now - ts > CACHE_TTL_SECONDS]
        for k in expired[:200]:
            _prediction_cache.pop(k, None)
    _prediction_cache[key] = (value, time.time())


# ---------------------------------------------------------------------------
# Sync workers for thread pool (CPU-heavy predict/explain/simulate)
# ---------------------------------------------------------------------------


def _sync_analyze_company(data_dict: dict) -> dict:
    """Run predict + z-score + explain for one company. Returns raw results."""
    df = pd.DataFrame([data_dict])
    predictions = insolvency_model.predict(df)
    z_scores = insolvency_model.calculate_altman_zscore(df)
    explanation = insolvency_model.explain_prediction(df, index=0)
    return {
        "predictions": predictions,
        "z_scores": z_scores,
        "explanation": explanation,
        "data_dict": data_dict,
    }


def _sync_analyze_employee(data_dict: dict) -> dict:
    """Run predict + explain for one employee. Returns raw results."""
    df = pd.DataFrame([data_dict])
    predictions = employee_model.predict(df)
    explanation = employee_model.explain_prediction(df, index=0)
    return {"predictions": predictions, "explanation": explanation, "data_dict": data_dict}


def _sync_upload_financial_bulk(df: pd.DataFrame) -> dict:
    """Run bulk financial predict + z-score. No SHAP."""
    predictions = insolvency_model.predict(df)
    z_scores = insolvency_model.calculate_altman_zscore(df)
    return {"predictions": predictions, "z_scores": z_scores, "df": df}


def _sync_upload_employee_bulk(df: pd.DataFrame) -> dict:
    """Run bulk employee predict. No SHAP."""
    predictions = employee_model.predict(df)
    return {"predictions": predictions, "df": df}


def _sync_simulate_layoffs(df: pd.DataFrame, budget_cut_percent: float, min_per_dept: int) -> pd.DataFrame:
    """Run layoff simulation. Returns result DataFrame."""
    return employee_model.simulate_layoffs(df, budget_cut_percent=budget_cut_percent, min_per_dept=min_per_dept)


def _sync_explain_financial_row(df: pd.DataFrame, index: int) -> dict:
    """Run predict + explain for one row of financial DataFrame."""
    row_df = df.iloc[[index]]
    predictions = insolvency_model.predict(row_df)
    z_scores = insolvency_model.calculate_altman_zscore(row_df)
    explanation = insolvency_model.explain_prediction(row_df, index=0)
    return {
        "predictions": predictions,
        "z_scores": z_scores,
        "explanation": explanation,
        "row_df": row_df,
    }


def _sync_explain_employee_row(df: pd.DataFrame, index: int) -> dict:
    """Run predict + explain for one row of employee DataFrame."""
    row_df = df.iloc[[index]]
    predictions = employee_model.predict(row_df)
    explanation = employee_model.explain_prediction(row_df, index=0)
    return {"predictions": predictions, "explanation": explanation, "row_df": row_df}


def load_models():
    """Load ML models from disk or train new ones."""
    global insolvency_model, employee_model, pdf_generator
    global market_intelligence_service, enhanced_prediction_service

    model_dir = project_root / "ml_models" / "trained_models"
    data_dir = project_root / "data"

    # Load or train insolvency model
    insolvency_model_path = model_dir / "insolvency_model.pkl"
    insolvency_model = InsolvencyPredictor()

    if insolvency_model_path.exists():
        print(f"Loading insolvency model from {insolvency_model_path}")
        insolvency_model.load_model(insolvency_model_path)
    else:
        print("Training new insolvency model...")
        company_data_path = data_dir / "company_data.csv"
        if company_data_path.exists():
            df = pd.read_csv(company_data_path)
            insolvency_model.train(df)
            insolvency_model.save_model(insolvency_model_path)
        else:
            print(f"Warning: No training data found at {company_data_path}")

    # Load or train employee model
    employee_model_path = model_dir / "employee_model.pkl"
    employee_model = EmployeeScorer()

    if employee_model_path.exists():
        print(f"Loading employee model from {employee_model_path}")
        employee_model.load_model(employee_model_path)
    else:
        print("Training new employee model...")
        employee_data_path = data_dir / "employee_data.csv"
        if employee_data_path.exists():
            df = pd.read_csv(employee_data_path)
            employee_model.train(df)
            employee_model.save_model(employee_model_path)
        else:
            print(f"Warning: No training data found at {employee_data_path}")

    # Initialize PDF generator
    pdf_generator = PDFReportGenerator()
    print("PDF generator initialized")

    # Initialize market intelligence service
    market_intelligence_service = MarketIntelligenceService()
    print("Market intelligence service initialized")

    # Initialize enhanced prediction service
    enhanced_prediction_service = EnhancedPredictionService(models_dir=model_dir)
    print("Enhanced prediction service initialized")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    # Startup
    print("Starting Insolvency Prevention System API...")
    load_models()
    print("Models loaded successfully!")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    description="API for predicting and preventing company insolvency using ML models",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to the Insolvency Prevention System API"}


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with model status."""
    return HealthResponse(
        status="healthy",
        models_loaded=insolvency_model is not None and employee_model is not None,
        insolvency_model_metrics=insolvency_model.metrics if insolvency_model else None,
        employee_model_metrics=employee_model.metrics if employee_model else None,
    )


@app.get("/api/analyses/recent", response_model=RecentAnalysesResponse)
async def get_recent_analyses(limit: int = 10):
    """Return recent analyses for Dashboard. Capped at 50."""
    limit = min(max(1, limit), 50)
    entries = _get_recent_analyses(limit=limit)
    return RecentAnalysesResponse(entries=entries, total=len(entries))


# CSV templates for uploads
COMPANY_CSV_HEADER = "company_id,company_name,industry,working_capital_to_total_assets,retained_earnings_to_total_assets,ebit_to_total_assets,market_value_equity_to_total_liabilities,sales_to_total_assets,current_ratio,quick_ratio,debt_to_equity,interest_coverage,net_profit_margin,return_on_assets,return_on_equity"
EMPLOYEE_CSV_HEADER = "employee_id,name,gender,age,department,job_role,job_level,performance_rating,job_satisfaction,job_involvement,environment_satisfaction,monthly_income,percent_salary_hike,stock_option_level,years_at_company,years_in_current_role,total_working_years,distance_from_home,business_travel,over_time"


@app.get("/api/templates/company")
async def get_company_csv_template():
    """Download CSV template for company financial upload."""
    return Response(
        content=COMPANY_CSV_HEADER + "\n",
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=company_financial_template.csv"},
    )


@app.get("/api/templates/employee")
async def get_employee_csv_template():
    """Download CSV template for employee data upload."""
    return Response(
        content=EMPLOYEE_CSV_HEADER + "\n",
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=employee_data_template.csv"},
    )


# ============================================================================
# Financial Analysis Endpoints
# ============================================================================

@app.post("/api/financial/analyze", response_model=InsolvencyAnalysisResponse)
async def analyze_company(data: CompanyFinancialData):
    """
    Analyze a single company's financial data for insolvency risk.
    Returns prediction with SHAP explanation.
    Uses thread pool for CPU work and caches repeated identical inputs.
    """
    if not insolvency_model or not insolvency_model.is_fitted:
        raise HTTPException(status_code=503, detail="Insolvency model not loaded")

    try:
        data_dict = data.model_dump()
        cache_key = _cache_key_from_dict(data_dict)
        cached = _get_cached(cache_key)
        if cached is not None:
            return InsolvencyAnalysisResponse(**cached)

        raw = await asyncio.to_thread(_sync_analyze_company, data_dict)
        predictions = raw["predictions"]
        z_scores = raw["z_scores"]
        explanation = convert_numpy_types(raw["explanation"])

        estimated_time = predictions["estimated_time_to_event"].iloc[0]
        exec_summary = _generate_executive_summary(
            data.company_name or "",
            str(predictions["risk_category"].iloc[0]),
            float(z_scores["z_score"].iloc[0]),
            str(z_scores["z_score_zone"].iloc[0]),
            float(predictions["probability_of_distress"].iloc[0]),
            explanation.get("top_risk_drivers", []) or [],
        )
        prediction = InsolvencyPrediction(
            company_id=data.company_id,
            company_name=data.company_name,
            probability_of_distress=float(predictions["probability_of_distress"].iloc[0]),
            risk_category=str(predictions["risk_category"].iloc[0]),
            estimated_time_to_event=int(estimated_time) if pd.notna(estimated_time) else None,
            z_score=float(z_scores["z_score"].iloc[0]),
            z_score_zone=str(z_scores["z_score_zone"].iloc[0]),
            executive_summary=exec_summary,
        )
        explanation_response = InsolvencyExplanation(
            shap_values=convert_numpy_types(explanation["shap_values"]),
            top_risk_drivers=convert_numpy_types(explanation["top_risk_drivers"]),
            base_value=float(explanation["base_value"]),
            prediction_value=float(explanation["prediction_value"]),
        )
        response = InsolvencyAnalysisResponse(prediction=prediction, explanation=explanation_response)
        _set_cached(cache_key, response.model_dump())
        _append_analysis(
            "Company Analysis",
            data.company_name or data.company_id or "Unknown",
            str(predictions["risk_category"].iloc[0]) + " Risk",
            f"{(float(predictions['probability_of_distress'].iloc[0]) * 100):.1f}%",
            {"company_id": data.company_id},
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/financial/upload-single", response_model=InsolvencyAnalysisResponse)
async def upload_single_company(file: UploadFile = File(...)):
    """
    Upload a CSV file with a single company's financial data.
    Returns prediction with SHAP explanation (same as /analyze but from CSV).
    """
    if not insolvency_model or not insolvency_model.is_fitted:
        raise HTTPException(status_code=503, detail="Insolvency model not loaded")

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        if len(df) == 0:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        df_single = df.iloc[[0]]

        raw = await asyncio.to_thread(_sync_explain_financial_row, df_single, 0)
        predictions = raw["predictions"]
        z_scores = raw["z_scores"]
        explanation = convert_numpy_types(raw["explanation"])

        estimated_time = predictions["estimated_time_to_event"].iloc[0]
        comp_name = str(df_single["company_name"].iloc[0]) if "company_name" in df_single.columns else str(df_single["company_id"].iloc[0]) if "company_id" in df_single.columns else "Unknown"
        exec_summary = _generate_executive_summary(
            comp_name,
            str(predictions["risk_category"].iloc[0]),
            float(z_scores["z_score"].iloc[0]),
            str(z_scores["z_score_zone"].iloc[0]),
            float(predictions["probability_of_distress"].iloc[0]),
            explanation.get("top_risk_drivers", []) or [],
        )
        prediction = InsolvencyPrediction(
            company_id=df_single["company_id"].iloc[0] if "company_id" in df_single.columns else "Unknown",
            company_name=df_single["company_name"].iloc[0] if "company_name" in df_single.columns else None,
            probability_of_distress=float(predictions["probability_of_distress"].iloc[0]),
            risk_category=str(predictions["risk_category"].iloc[0]),
            estimated_time_to_event=int(estimated_time) if pd.notna(estimated_time) else None,
            z_score=float(z_scores["z_score"].iloc[0]),
            z_score_zone=str(z_scores["z_score_zone"].iloc[0]),
            executive_summary=exec_summary,
        )
        explanation_response = InsolvencyExplanation(
            shap_values=convert_numpy_types(explanation["shap_values"]),
            top_risk_drivers=convert_numpy_types(explanation["top_risk_drivers"]),
            base_value=float(explanation["base_value"]),
            prediction_value=float(explanation["prediction_value"]),
        )
        _append_analysis(
            "Company Analysis",
            comp_name,
            str(predictions["risk_category"].iloc[0]) + " Risk",
            f"{(float(predictions['probability_of_distress'].iloc[0]) * 100):.1f}%",
            {"company_id": prediction.company_id},
        )
        return InsolvencyAnalysisResponse(prediction=prediction, explanation=explanation_response)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload processing failed: {str(e)}")


@app.post("/api/financial/upload", response_model=InsolvencyBulkResponse)
async def upload_financial_data(file: UploadFile = File(...)):
    """
    Upload a CSV file with company financial data.
    Returns predictions for all companies (no SHAP per row; use explain-row for one).
    """
    if not insolvency_model or not insolvency_model.is_fitted:
        raise HTTPException(status_code=503, detail="Insolvency model not loaded")

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        raw = await asyncio.to_thread(_sync_upload_financial_bulk, df)
        predictions = raw["predictions"]
        z_scores = raw["z_scores"]
        df = raw["df"]

        results = []
        for i in range(len(df)):
            pred = InsolvencyPrediction(
                company_id=df["company_id"].iloc[i] if "company_id" in df.columns else f"Company_{i+1}",
                company_name=df["company_name"].iloc[i] if "company_name" in df.columns else None,
                probability_of_distress=float(predictions["probability_of_distress"].iloc[i]),
                risk_category=predictions["risk_category"].iloc[i],
                estimated_time_to_event=int(predictions["estimated_time_to_event"].iloc[i]) if pd.notna(
                    predictions["estimated_time_to_event"].iloc[i]
                ) else None,
                z_score=float(z_scores["z_score"].iloc[i]),
                z_score_zone=z_scores["z_score_zone"].iloc[i],
            )
            results.append(pred)

        # Summary statistics
        summary = {
            "high_risk_count": len([r for r in results if r.risk_category == "High"]),
            "medium_risk_count": len([r for r in results if r.risk_category == "Medium"]),
            "low_risk_count": len([r for r in results if r.risk_category == "Low"]),
            "avg_probability": float(predictions["probability_of_distress"].mean()),
            "z_score_distress_count": len([r for r in results if r.z_score_zone == "Distress"]),
        }

        _append_analysis(
            "Company Analysis",
            f"Bulk upload ({len(results)} companies)",
            f"{summary['high_risk_count']} High / {summary['low_risk_count']} Low Risk",
            f"{summary['avg_probability']*100:.1f}% avg distress",
            {"total_companies": len(results)},
        )
        return InsolvencyBulkResponse(
            total_companies=len(results),
            predictions=results,
            summary=summary,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload processing failed: {str(e)}")


@app.get("/api/financial/feature-importance", response_model=FeatureImportanceResponse)
async def get_financial_feature_importance():
    """Get feature importance from the insolvency prediction model."""
    if not insolvency_model or not insolvency_model.is_fitted:
        raise HTTPException(status_code=503, detail="Insolvency model not loaded")

    try:
        # Get feature importance from XGBoost model
        importance = dict(zip(
            insolvency_model.feature_names,
            insolvency_model.model.feature_importances_.tolist()
        ))

        # Sort by importance
        importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))

        return FeatureImportanceResponse(
            feature_importance=importance,
            model_metrics=insolvency_model.metrics,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feature importance: {str(e)}")


@app.post("/api/financial/explain-row", response_model=InsolvencyAnalysisResponse)
async def explain_financial_row(
    file: UploadFile = File(...),
    row_index: int = 0,
):
    """
    Get prediction + SHAP explanation for a single row from a bulk financial CSV.
    Use after bulk upload to explain one row without re-uploading the full file.
    """
    if not insolvency_model or not insolvency_model.is_fitted:
        raise HTTPException(status_code=503, detail="Insolvency model not loaded")
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        if row_index < 0 or row_index >= len(df):
            raise HTTPException(
                status_code=400,
                detail=f"row_index must be 0..{len(df) - 1} for this file ({len(df)} rows)",
            )
        cache_key = hashlib.sha256(contents).hexdigest() + f":{row_index}"
        cached = _get_cached(cache_key)
        if cached is not None:
            return InsolvencyAnalysisResponse(**cached)
        raw = await asyncio.to_thread(_sync_explain_financial_row, df, row_index)
        predictions = raw["predictions"]
        z_scores = raw["z_scores"]
        explanation = convert_numpy_types(raw["explanation"])
        row_df = raw["row_df"]
        estimated_time = predictions["estimated_time_to_event"].iloc[0]
        prediction = InsolvencyPrediction(
            company_id=row_df["company_id"].iloc[0] if "company_id" in row_df.columns else "Unknown",
            company_name=row_df["company_name"].iloc[0] if "company_name" in row_df.columns else None,
            probability_of_distress=float(predictions["probability_of_distress"].iloc[0]),
            risk_category=str(predictions["risk_category"].iloc[0]),
            estimated_time_to_event=int(estimated_time) if pd.notna(estimated_time) else None,
            z_score=float(z_scores["z_score"].iloc[0]),
            z_score_zone=str(z_scores["z_score_zone"].iloc[0]),
        )
        explanation_response = InsolvencyExplanation(
            shap_values=convert_numpy_types(explanation["shap_values"]),
            top_risk_drivers=convert_numpy_types(explanation["top_risk_drivers"]),
            base_value=float(explanation["base_value"]),
            prediction_value=float(explanation["prediction_value"]),
        )
        response = InsolvencyAnalysisResponse(prediction=prediction, explanation=explanation_response)
        _set_cached(cache_key, response.model_dump())
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explain row failed: {str(e)}")


# ============================================================================
# Employee Analysis Endpoints
# ============================================================================

@app.post("/api/employee/analyze", response_model=EmployeeAnalysisResponse)
async def analyze_employee(data: EmployeeData):
    """
    Analyze a single employee's data for attrition risk.
    Returns prediction with SHAP explanation.
    Uses thread pool and caches repeated identical inputs.
    """
    if not employee_model or not employee_model.is_fitted:
        raise HTTPException(status_code=503, detail="Employee model not loaded")

    try:
        data_dict = data.model_dump()
        cache_key = _cache_key_from_dict(data_dict)
        cached = _get_cached(cache_key)
        if cached is not None:
            return EmployeeAnalysisResponse(**cached)

        raw = await asyncio.to_thread(_sync_analyze_employee, data_dict)
        predictions = raw["predictions"]
        explanation = convert_numpy_types(raw["explanation"])

        prediction = EmployeePrediction(
            employee_id=data.employee_id,
            name=data.name,
            department=data.department,
            retention_score=float(predictions["retention_score"].iloc[0]),
            attrition_probability=float(predictions["attrition_probability"].iloc[0]),
            attrition_risk=str(predictions["attrition_risk"].iloc[0]),
            layoff_priority=str(predictions["layoff_priority"].iloc[0]),
        )
        explanation_response = EmployeeExplanation(
            shap_values=convert_numpy_types(explanation["shap_values"]),
            top_factors=convert_numpy_types(explanation["top_factors"]),
            base_value=float(explanation["base_value"]),
            prediction_value=float(explanation["prediction_value"]),
        )
        response = EmployeeAnalysisResponse(prediction=prediction, explanation=explanation_response)
        _set_cached(cache_key, response.model_dump())
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/employee/upload", response_model=EmployeeBulkResponse)
async def upload_employee_data(file: UploadFile = File(...)):
    """
    Upload a CSV file with employee data.
    Returns predictions for all employees (no SHAP per row; use explain-row for one).
    """
    if not employee_model or not employee_model.is_fitted:
        raise HTTPException(status_code=503, detail="Employee model not loaded")

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        raw = await asyncio.to_thread(_sync_upload_employee_bulk, df)
        predictions = raw["predictions"]
        df = raw["df"]

        # Build response
        results = []
        for i in range(len(df)):
            pred = EmployeePrediction(
                employee_id=df["employee_id"].iloc[i] if "employee_id" in df.columns else f"Employee_{i+1}",
                name=df["name"].iloc[i] if "name" in df.columns else None,
                department=df["department"].iloc[i] if "department" in df.columns else None,
                retention_score=float(predictions["retention_score"].iloc[i]),
                attrition_probability=float(predictions["attrition_probability"].iloc[i]),
                attrition_risk=predictions["attrition_risk"].iloc[i],
                layoff_priority=predictions["layoff_priority"].iloc[i],
            )
            results.append(pred)

        # Summary statistics
        summary = {
            "high_attrition_risk_count": len([r for r in results if r.attrition_risk == "High"]),
            "medium_attrition_risk_count": len([r for r in results if r.attrition_risk == "Medium"]),
            "low_attrition_risk_count": len([r for r in results if r.attrition_risk == "Low"]),
            "avg_retention_score": float(predictions["retention_score"].mean()),
            "avg_attrition_probability": float(predictions["attrition_probability"].mean()),
            "high_layoff_priority_count": len([r for r in results if r.layoff_priority == "High"]),
        }

        _append_analysis(
            "Employee Scoring",
            f"Bulk ({len(results)} employees)",
            f"{summary['high_attrition_risk_count']} High / {summary['low_attrition_risk_count']} Low Risk",
            f"Avg retention {summary['avg_retention_score']:.1f}",
            {"total_employees": len(results)},
        )
        return EmployeeBulkResponse(
            total_employees=len(results),
            predictions=results,
            summary=summary,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload processing failed: {str(e)}")


@app.post("/api/employee/simulate-layoff", response_model=LayoffSimulationResponse)
async def simulate_layoffs(
    budget_cut_percent: float,
    min_per_dept: int = 1,
    file: UploadFile = File(...),
):
    """
    Simulate layoff recommendations based on budget constraints.
    Upload employee CSV and specify budget cut percentage.
    """
    if not employee_model or not employee_model.is_fitted:
        raise HTTPException(status_code=503, detail="Employee model not loaded")

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        # Read CSV
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        # Validate required columns
        if "department" not in df.columns or "monthly_income" not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="CSV must contain 'department' and 'monthly_income' columns"
            )

        # Run simulation in thread pool (capture print output)
        import io as stdio
        old_stdout = sys.stdout
        sys.stdout = stdio.StringIO()
        try:
            result_df = await asyncio.to_thread(
                _sync_simulate_layoffs, df, budget_cut_percent, min_per_dept
            )
        finally:
            sys.stdout = old_stdout

        # Calculate statistics
        total_payroll = df["monthly_income"].sum()
        target_savings = total_payroll * (budget_cut_percent / 100)
        actual_savings = result_df[result_df["layoff_recommended"]]["monthly_income"].sum()
        n_layoffs = result_df["layoff_recommended"].sum()

        # Build recommendations list (one pass from records, no iterrows)
        records = result_df.to_dict("records")
        recommendations = [
            LayoffRecommendation(
                employee_id=r["employee_id"],
                name=r["name"],
                department=r["department"],
                monthly_income=int(r["monthly_income"]),
                retention_score=float(r["retention_score"]),
                layoff_recommended=bool(r["layoff_recommended"]),
                layoff_reason=r["layoff_reason"],
            )
            for r in records
        ]

        # Department breakdown
        dept_breakdown = result_df[result_df["layoff_recommended"]].groupby("department").size().to_dict()

        _append_analysis(
            "Layoff Simulation",
            f"{budget_cut_percent}% Budget Cut Scenario",
            f"{int(n_layoffs)} Affected",
            None,
            {"employees_affected": int(n_layoffs), "target_percent": budget_cut_percent},
        )
        return LayoffSimulationResponse(
            target_budget_cut=budget_cut_percent,
            target_monthly_savings=float(target_savings),
            actual_monthly_savings=float(actual_savings),
            employees_affected=int(n_layoffs),
            savings_achieved_percent=float((actual_savings / total_payroll) * 100) if total_payroll > 0 else 0,
            recommendations=recommendations,
            department_breakdown=dept_breakdown,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@app.get("/api/employee/feature-importance", response_model=FeatureImportanceResponse)
async def get_employee_feature_importance():
    """Get feature importance from the employee scoring model."""
    if not employee_model or not employee_model.is_fitted:
        raise HTTPException(status_code=503, detail="Employee model not loaded")

    try:
        # Get feature importance from XGBoost model
        importance = dict(zip(
            employee_model.feature_names,
            employee_model.model.feature_importances_.tolist()
        ))

        # Sort by importance
        importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))

        return FeatureImportanceResponse(
            feature_importance=importance,
            model_metrics=employee_model.metrics,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feature importance: {str(e)}")


@app.post("/api/employee/explain-row", response_model=EmployeeAnalysisResponse)
async def explain_employee_row(
    file: UploadFile = File(...),
    row_index: int = 0,
):
    """
    Get prediction + SHAP explanation for a single row from a bulk employee CSV.
    Use after bulk upload to explain one row without re-uploading the full file.
    """
    if not employee_model or not employee_model.is_fitted:
        raise HTTPException(status_code=503, detail="Employee model not loaded")
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        if row_index < 0 or row_index >= len(df):
            raise HTTPException(
                status_code=400,
                detail=f"row_index must be 0..{len(df) - 1} for this file ({len(df)} rows)",
            )
        cache_key = hashlib.sha256(contents).hexdigest() + f":emp:{row_index}"
        cached = _get_cached(cache_key)
        if cached is not None:
            return EmployeeAnalysisResponse(**cached)
        raw = await asyncio.to_thread(_sync_explain_employee_row, df, row_index)
        predictions = raw["predictions"]
        explanation = convert_numpy_types(raw["explanation"])
        row_df = raw["row_df"]
        prediction = EmployeePrediction(
            employee_id=row_df["employee_id"].iloc[0] if "employee_id" in row_df.columns else "Unknown",
            name=row_df["name"].iloc[0] if "name" in row_df.columns else None,
            department=row_df["department"].iloc[0] if "department" in row_df.columns else None,
            retention_score=float(predictions["retention_score"].iloc[0]),
            attrition_probability=float(predictions["attrition_probability"].iloc[0]),
            attrition_risk=str(predictions["attrition_risk"].iloc[0]),
            layoff_priority=str(predictions["layoff_priority"].iloc[0]),
        )
        explanation_response = EmployeeExplanation(
            shap_values=convert_numpy_types(explanation["shap_values"]),
            top_factors=convert_numpy_types(explanation["top_factors"]),
            base_value=float(explanation["base_value"]),
            prediction_value=float(explanation["prediction_value"]),
        )
        response = EmployeeAnalysisResponse(prediction=prediction, explanation=explanation_response)
        _set_cached(cache_key, response.model_dump())
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explain row failed: {str(e)}")


# ============================================================================
# Report Generation Endpoints
# ============================================================================

@app.post("/api/reports/generate")
async def generate_report(
    report_type: Literal["insolvency", "layoff"],
    request: InsolvencyReportRequest | None = None,
    layoff_request: LayoffReportRequest | None = None,
    file: UploadFile | None = File(None),
):
    """
    Generate a PDF report.

    For insolvency report:
    - report_type: "insolvency"
    - request: InsolvencyReportRequest with company_id, company_name, company_data

    For layoff report:
    - report_type: "layoff"
    - layoff_request: LayoffReportRequest with budget_cut_percent, min_per_dept
    - file: CSV file with employee data
    """
    if not pdf_generator:
        raise HTTPException(status_code=503, detail="PDF generator not initialized")

    try:
        if report_type == "insolvency":
            return await _generate_insolvency_report(request)
        elif report_type == "layoff":
            return await _generate_layoff_report(layoff_request, file)
        else:
            raise HTTPException(status_code=400, detail="Invalid report_type. Use 'insolvency' or 'layoff'")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@app.post("/api/reports/insolvency")
async def generate_insolvency_report(request: InsolvencyReportRequest):
    """
    Generate an insolvency risk assessment PDF report.

    Returns a downloadable PDF file containing:
    - Company identification and date
    - Risk score with color coding
    - Altman Z-Score analysis
    - Time to event estimate
    - Top 10 risk drivers with SHAP values
    - Recommendations section
    """
    return await _generate_insolvency_report(request)


async def _generate_insolvency_report(request: InsolvencyReportRequest | None):
    """Internal function to generate insolvency report."""
    if not request:
        raise HTTPException(status_code=400, detail="Request body required for insolvency report")

    if not insolvency_model or not insolvency_model.is_fitted:
        raise HTTPException(status_code=503, detail="Insolvency model not loaded")

    if not pdf_generator:
        raise HTTPException(status_code=503, detail="PDF generator not initialized")

    company_data = request.company_data.model_dump()
    raw = await asyncio.to_thread(_sync_analyze_company, company_data)
    predictions = raw["predictions"]
    z_scores = raw["z_scores"]
    explanation = raw["explanation"]

    # Build prediction dict
    prediction_dict = {
        "probability_of_distress": float(predictions["probability_of_distress"].iloc[0]),
        "risk_category": predictions["risk_category"].iloc[0],
        "estimated_time_to_event": int(predictions["estimated_time_to_event"].iloc[0])
            if pd.notna(predictions["estimated_time_to_event"].iloc[0]) else None,
        "z_score": float(z_scores["z_score"].iloc[0]),
        "z_score_zone": z_scores["z_score_zone"].iloc[0],
    }

    # Generate PDF
    pdf_bytes = pdf_generator.generate_insolvency_report(
        company_id=request.company_id,
        company_name=request.company_name,
        prediction=prediction_dict,
        explanation=explanation,
    )

    # Return PDF as downloadable file
    filename = f"insolvency_report_{request.company_id}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@app.post("/api/reports/layoff")
async def generate_layoff_report(
    budget_cut_percent: float,
    min_per_dept: int = 1,
    file: UploadFile = File(...),
):
    """
    Generate a layoff simulation PDF report.

    Upload an employee CSV file and specify budget cut parameters.

    Returns a downloadable PDF file containing:
    - Simulation parameters
    - Summary statistics
    - List of recommended layoffs with scores
    - Cost savings analysis
    - Department impact analysis
    """
    layoff_request = LayoffReportRequest(
        budget_cut_percent=budget_cut_percent,
        min_per_dept=min_per_dept
    )
    return await _generate_layoff_report(layoff_request, file)


async def _generate_layoff_report(
    request: LayoffReportRequest | None,
    file: UploadFile | None
):
    """Internal function to generate layoff report."""
    if not request:
        raise HTTPException(status_code=400, detail="Request parameters required for layoff report")

    if not file:
        raise HTTPException(status_code=400, detail="Employee CSV file required for layoff report")

    if not employee_model or not employee_model.is_fitted:
        raise HTTPException(status_code=503, detail="Employee model not loaded")

    if not pdf_generator:
        raise HTTPException(status_code=503, detail="PDF generator not initialized")

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    # Read CSV
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))

    # Validate required columns
    if "department" not in df.columns or "monthly_income" not in df.columns:
        raise HTTPException(
            status_code=400,
            detail="CSV must contain 'department' and 'monthly_income' columns"
        )

    import io as stdio
    old_stdout = sys.stdout
    sys.stdout = stdio.StringIO()
    try:
        result_df = await asyncio.to_thread(
            _sync_simulate_layoffs,
            df,
            request.budget_cut_percent,
            request.min_per_dept,
        )
    finally:
        sys.stdout = old_stdout

    # Calculate statistics
    total_payroll = df["monthly_income"].sum()
    target_savings = total_payroll * (request.budget_cut_percent / 100)
    actual_savings = result_df[result_df["layoff_recommended"]]["monthly_income"].sum()
    n_layoffs = result_df["layoff_recommended"].sum()

    # Build simulation params
    simulation_params = {
        "budget_cut_percent": request.budget_cut_percent,
        "min_per_dept": request.min_per_dept,
    }

    # Build summary
    summary = {
        "target_monthly_savings": float(target_savings),
        "actual_monthly_savings": float(actual_savings),
        "employees_affected": int(n_layoffs),
        "savings_achieved_percent": float((actual_savings / total_payroll) * 100) if total_payroll > 0 else 0,
    }

    # Build recommendations list (one pass from records, no iterrows)
    records = result_df.to_dict("records")
    recommendations = [
        {
            "employee_id": r["employee_id"],
            "name": r["name"],
            "department": r["department"],
            "monthly_income": int(r["monthly_income"]),
            "retention_score": float(r["retention_score"]),
            "layoff_recommended": bool(r["layoff_recommended"]),
            "layoff_reason": r["layoff_reason"],
        }
        for r in records
    ]

    # Department breakdown
    dept_breakdown = result_df[result_df["layoff_recommended"]].groupby("department").size().to_dict()

    # Generate PDF
    pdf_bytes = pdf_generator.generate_layoff_report(
        simulation_params=simulation_params,
        summary=summary,
        recommendations=recommendations,
        department_breakdown=dept_breakdown,
    )

    # Return PDF as downloadable file
    filename = f"layoff_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


# ============================================================================
# Market Intelligence Endpoints
# ============================================================================

@app.post("/api/market-intelligence", response_model=MarketIntelligenceResponse)
async def get_market_intelligence(request: MarketIntelligenceRequest):
    """
    Get market intelligence for a company without prediction.

    Returns:
    - Industry news with sentiment analysis
    - Sector performance data
    - Economic indicators
    - Market summary and risk adjustment factor

    This endpoint searches for:
    - Company-specific news
    - Industry/sector news
    - Economic conditions
    """
    if not market_intelligence_service:
        raise HTTPException(status_code=503, detail="Market intelligence service not initialized")

    try:
        report = await market_intelligence_service.generate_report(
            company_name=request.company_name,
            industry=request.industry,
            description=request.description or ""
        )

        # Convert to response format
        news_articles = [
            NewsArticleResponse(
                title=article.title,
                source=article.source,
                url=article.url,
                published_at=article.published_at.isoformat(),
                summary=article.summary,
                sentiment_score=article.sentiment_score,
                relevance_score=article.relevance_score
            )
            for article in report.news_articles
        ]

        sector_data = None
        if report.sector_data:
            sector_data = SectorDataResponse(
                sector=report.sector_data.sector,
                performance_1d=report.sector_data.performance_1d,
                performance_1w=report.sector_data.performance_1w,
                performance_1m=report.sector_data.performance_1m,
                performance_ytd=report.sector_data.performance_ytd,
                trend=report.sector_data.trend
            )

        economic_indicators = None
        if report.economic_indicators:
            economic_indicators = EconomicIndicatorsResponse(
                gdp_growth=report.economic_indicators.gdp_growth,
                unemployment_rate=report.economic_indicators.unemployment_rate,
                inflation_rate=report.economic_indicators.inflation_rate,
                interest_rate=report.economic_indicators.interest_rate,
                consumer_confidence=report.economic_indicators.consumer_confidence
            )

        return MarketIntelligenceResponse(
            company_name=report.company_name,
            industry=report.industry,
            sector=report.sector,
            generated_at=report.generated_at.isoformat(),
            news_articles=news_articles,
            overall_news_sentiment=report.overall_news_sentiment,
            sector_data=sector_data,
            economic_indicators=economic_indicators,
            risk_adjustment=report.risk_adjustment,
            market_summary=report.market_summary
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market intelligence failed: {str(e)}")


@app.post("/api/financial/analyze-enhanced", response_model=EnhancedPredictionResponse)
async def analyze_company_enhanced(request: EnhancedAnalysisRequest):
    """
    Analyze company with enhanced market intelligence.

    This endpoint combines:
    1. ML model prediction (XGBoost trained on financial ratios)
    2. Live market intelligence (news sentiment, sector performance, economic data)

    The adjusted probability considers:
    - Base model prediction from financial ratios
    - News sentiment for company/industry
    - Sector performance trends
    - Economic conditions

    Returns detailed risk factors and recommendations.
    """
    if not enhanced_prediction_service:
        raise HTTPException(status_code=503, detail="Enhanced prediction service not initialized")

    try:
        # Prepare company data dict
        company_data = {
            'company_name': request.company_name,
            'industry': request.industry,
            'description': request.description,
            'working_capital_to_total_assets': request.working_capital_to_total_assets,
            'retained_earnings_to_total_assets': request.retained_earnings_to_total_assets,
            'ebit_to_total_assets': request.ebit_to_total_assets,
            'market_value_equity_to_total_liabilities': request.market_value_equity_to_total_liabilities,
            'sales_to_total_assets': request.sales_to_total_assets,
            'current_ratio': request.current_ratio,
            'quick_ratio': request.quick_ratio,
            'debt_to_equity': request.debt_to_equity,
            'interest_coverage': request.interest_coverage,
            'net_profit_margin': request.net_profit_margin,
            'return_on_assets': request.return_on_assets,
            'return_on_equity': request.return_on_equity
        }

        # Get enhanced prediction
        result = await enhanced_prediction_service.predict_insolvency_enhanced(
            company_data=company_data,
            include_market_intelligence=request.include_market_intelligence
        )

        # Build market intelligence response if available
        market_intelligence = None
        if result.market_report:
            report = result.market_report
            news_articles = [
                NewsArticleResponse(
                    title=article.title,
                    source=article.source,
                    url=article.url,
                    published_at=article.published_at.isoformat(),
                    summary=article.summary,
                    sentiment_score=article.sentiment_score,
                    relevance_score=article.relevance_score
                )
                for article in report.news_articles
            ]

            sector_data = None
            if report.sector_data:
                sector_data = SectorDataResponse(
                    sector=report.sector_data.sector,
                    performance_1d=report.sector_data.performance_1d,
                    performance_1w=report.sector_data.performance_1w,
                    performance_1m=report.sector_data.performance_1m,
                    performance_ytd=report.sector_data.performance_ytd,
                    trend=report.sector_data.trend
                )

            economic_indicators = None
            if report.economic_indicators:
                economic_indicators = EconomicIndicatorsResponse(
                    gdp_growth=report.economic_indicators.gdp_growth,
                    unemployment_rate=report.economic_indicators.unemployment_rate,
                    inflation_rate=report.economic_indicators.inflation_rate,
                    interest_rate=report.economic_indicators.interest_rate,
                    consumer_confidence=report.economic_indicators.consumer_confidence
                )

            market_intelligence = MarketIntelligenceResponse(
                company_name=report.company_name,
                industry=report.industry,
                sector=report.sector,
                generated_at=report.generated_at.isoformat(),
                news_articles=news_articles,
                overall_news_sentiment=report.overall_news_sentiment,
                sector_data=sector_data,
                economic_indicators=economic_indicators,
                risk_adjustment=report.risk_adjustment,
                market_summary=report.market_summary
            )

        # Build risk factors response
        risk_factors = [
            RiskFactor(
                type=factor['type'],
                metric=factor['metric'],
                value=factor.get('value'),
                threshold=factor.get('threshold'),
                message=factor['message'],
                severity=factor['severity']
            )
            for factor in result.risk_factors
        ]

        return EnhancedPredictionResponse(
            base_probability=result.base_probability,
            base_prediction=result.base_prediction,
            adjusted_probability=result.adjusted_probability,
            adjusted_prediction=result.adjusted_prediction,
            risk_level=result.risk_level,
            model_contribution=result.model_contribution,
            market_contribution=result.market_contribution,
            risk_factors=risk_factors,
            recommendations=result.recommendations,
            market_intelligence=market_intelligence
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced analysis failed: {str(e)}")


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc)
        }
    )
