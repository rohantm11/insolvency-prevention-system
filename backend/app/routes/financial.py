"""Financial analysis routes."""

import asyncio
import hashlib
import io

import numpy as np
import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from app.models.schemas import (
    CompanyFinancialData,
    InsolvencyAnalysisResponse,
    InsolvencyPrediction,
    InsolvencyExplanation,
    InsolvencyBulkResponse,
    FeatureImportanceResponse,
)

router = APIRouter(prefix="/api/financial", tags=["Financial Analysis"])


def _get_main_module():
    """Get the main module regardless of import path."""
    import sys
    return sys.modules.get("backend.app.main") or sys.modules.get("app.main")


def _get_deps():
    """Lazy import to avoid circular dependencies with main module globals."""
    m = _get_main_module()
    return {
        "insolvency_model": m.insolvency_model,
        "convert_numpy_types": m.convert_numpy_types,
        "_sync_analyze_company": m._sync_analyze_company,
        "_sync_upload_financial_bulk": m._sync_upload_financial_bulk,
        "_sync_explain_financial_row": m._sync_explain_financial_row,
        "_cache_key_from_dict": m._cache_key_from_dict,
        "_get_cached": m._get_cached,
        "_set_cached": m._set_cached,
        "_append_analysis": m._append_analysis,
        "_generate_executive_summary": m._generate_executive_summary,
    }


@router.post("/analyze", response_model=InsolvencyAnalysisResponse)
async def analyze_company(data: CompanyFinancialData):
    """Analyze a single company's financial data for insolvency risk."""
    deps = _get_deps()
    insolvency_model = deps["insolvency_model"]
    if not insolvency_model or not insolvency_model.is_fitted:
        raise HTTPException(status_code=503, detail="Insolvency model not loaded")

    try:
        data_dict = data.model_dump()

        # Run accounting identity checks
        input_warnings = insolvency_model.validate_input(data_dict) if insolvency_model else []

        cache_key = deps["_cache_key_from_dict"](data_dict)
        cached = deps["_get_cached"](cache_key)
        if cached is not None:
            return InsolvencyAnalysisResponse(**cached)

        raw = await asyncio.to_thread(deps["_sync_analyze_company"], data_dict)
        predictions = raw["predictions"]
        z_scores = raw["z_scores"]
        explanation = deps["convert_numpy_types"](raw["explanation"])

        estimated_time = predictions["estimated_time_to_event"].iloc[0]
        exec_summary = deps["_generate_executive_summary"](
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
            input_warnings=input_warnings,
        )
        explanation_response = InsolvencyExplanation(
            shap_values=deps["convert_numpy_types"](explanation["shap_values"]),
            top_risk_drivers=deps["convert_numpy_types"](explanation["top_risk_drivers"]),
            base_value=float(explanation["base_value"]),
            prediction_value=float(explanation["prediction_value"]),
        )
        response = InsolvencyAnalysisResponse(prediction=prediction, explanation=explanation_response)
        deps["_set_cached"](cache_key, response.model_dump())
        deps["_append_analysis"](
            "Company Analysis",
            data.company_name or data.company_id or "Unknown",
            str(predictions["risk_category"].iloc[0]) + " Risk",
            f"{(float(predictions['probability_of_distress'].iloc[0]) * 100):.1f}%",
            {"company_id": data.company_id},
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/upload-single", response_model=InsolvencyAnalysisResponse)
async def upload_single_company(file: UploadFile = File(...)):
    """Upload a CSV file with a single company's financial data."""
    deps = _get_deps()
    insolvency_model = deps["insolvency_model"]
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

        raw = await asyncio.to_thread(deps["_sync_explain_financial_row"], df_single, 0)
        predictions = raw["predictions"]
        z_scores = raw["z_scores"]
        explanation = deps["convert_numpy_types"](raw["explanation"])

        estimated_time = predictions["estimated_time_to_event"].iloc[0]
        comp_name = str(df_single["company_name"].iloc[0]) if "company_name" in df_single.columns else str(df_single["company_id"].iloc[0]) if "company_id" in df_single.columns else "Unknown"
        exec_summary = deps["_generate_executive_summary"](
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
            shap_values=deps["convert_numpy_types"](explanation["shap_values"]),
            top_risk_drivers=deps["convert_numpy_types"](explanation["top_risk_drivers"]),
            base_value=float(explanation["base_value"]),
            prediction_value=float(explanation["prediction_value"]),
        )
        deps["_append_analysis"](
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


@router.post("/upload", response_model=InsolvencyBulkResponse)
async def upload_financial_data(file: UploadFile = File(...)):
    """Upload a CSV file with company financial data. Returns predictions for all companies."""
    deps = _get_deps()
    insolvency_model = deps["insolvency_model"]
    if not insolvency_model or not insolvency_model.is_fitted:
        raise HTTPException(status_code=503, detail="Insolvency model not loaded")

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        raw = await asyncio.to_thread(deps["_sync_upload_financial_bulk"], df)
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

        summary = {
            "high_risk_count": len([r for r in results if r.risk_category == "High"]),
            "medium_risk_count": len([r for r in results if r.risk_category == "Medium"]),
            "low_risk_count": len([r for r in results if r.risk_category == "Low"]),
            "avg_probability": float(predictions["probability_of_distress"].mean()),
            "z_score_distress_count": len([r for r in results if r.z_score_zone == "Distress"]),
        }

        deps["_append_analysis"](
            "Company Analysis",
            f"Bulk upload ({len(results)} companies)",
            f"{summary['high_risk_count']} High / {summary['low_risk_count']} Low Risk",
            f"{summary['avg_probability']*100:.1f}% avg distress",
            {"total_companies": len(results)},
        )
        return InsolvencyBulkResponse(total_companies=len(results), predictions=results, summary=summary)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload processing failed: {str(e)}")


@router.get("/feature-importance", response_model=FeatureImportanceResponse)
async def get_financial_feature_importance():
    """Get feature importance from the insolvency prediction model."""
    deps = _get_deps()
    insolvency_model = deps["insolvency_model"]
    if not insolvency_model or not insolvency_model.is_fitted:
        raise HTTPException(status_code=503, detail="Insolvency model not loaded")

    try:
        importance = dict(zip(
            insolvency_model.feature_names,
            insolvency_model.model.feature_importances_.tolist()
        ))
        importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
        return FeatureImportanceResponse(feature_importance=importance, model_metrics=insolvency_model.metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feature importance: {str(e)}")


@router.post("/explain-row", response_model=InsolvencyAnalysisResponse)
async def explain_financial_row(file: UploadFile = File(...), row_index: int = 0):
    """Get prediction + SHAP explanation for a single row from a bulk financial CSV."""
    deps = _get_deps()
    insolvency_model = deps["insolvency_model"]
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
        cached = deps["_get_cached"](cache_key)
        if cached is not None:
            return InsolvencyAnalysisResponse(**cached)
        raw = await asyncio.to_thread(deps["_sync_explain_financial_row"], df, row_index)
        predictions = raw["predictions"]
        z_scores = raw["z_scores"]
        explanation = deps["convert_numpy_types"](raw["explanation"])
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
            shap_values=deps["convert_numpy_types"](explanation["shap_values"]),
            top_risk_drivers=deps["convert_numpy_types"](explanation["top_risk_drivers"]),
            base_value=float(explanation["base_value"]),
            prediction_value=float(explanation["prediction_value"]),
        )
        response = InsolvencyAnalysisResponse(prediction=prediction, explanation=explanation_response)
        deps["_set_cached"](cache_key, response.model_dump())
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explain row failed: {str(e)}")
