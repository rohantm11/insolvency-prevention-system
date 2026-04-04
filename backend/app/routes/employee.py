"""Employee analysis routes."""

import asyncio
import hashlib
import io
import sys

import numpy as np
import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from app.models.schemas import (
    EmployeeData,
    EmployeeAnalysisResponse,
    EmployeePrediction,
    EmployeeExplanation,
    EmployeeBulkResponse,
    LayoffSimulationResponse,
    LayoffRecommendation,
    FeatureImportanceResponse,
)

router = APIRouter(prefix="/api/employee", tags=["Employee Analysis"])


def _get_main_module():
    """Get the main module regardless of import path."""
    import sys
    return sys.modules.get("backend.app.main") or sys.modules.get("app.main")


def _get_deps():
    """Lazy import to avoid circular dependencies with main module globals."""
    m = _get_main_module()
    return {
        "employee_model": m.employee_model,
        "convert_numpy_types": m.convert_numpy_types,
        "_sync_analyze_employee": m._sync_analyze_employee,
        "_sync_upload_employee_bulk": m._sync_upload_employee_bulk,
        "_sync_simulate_layoffs": m._sync_simulate_layoffs,
        "_sync_explain_employee_row": m._sync_explain_employee_row,
        "_cache_key_from_dict": m._cache_key_from_dict,
        "_get_cached": m._get_cached,
        "_set_cached": m._set_cached,
        "_append_analysis": m._append_analysis,
    }


@router.post("/analyze", response_model=EmployeeAnalysisResponse)
async def analyze_employee(data: EmployeeData):
    """Analyze a single employee's data for attrition risk."""
    deps = _get_deps()
    employee_model = deps["employee_model"]
    if not employee_model or not employee_model.is_fitted:
        raise HTTPException(status_code=503, detail="Employee model not loaded")

    try:
        data_dict = data.model_dump()
        cache_key = deps["_cache_key_from_dict"](data_dict)
        cached = deps["_get_cached"](cache_key)
        if cached is not None:
            return EmployeeAnalysisResponse(**cached)

        raw = await asyncio.to_thread(deps["_sync_analyze_employee"], data_dict)
        predictions = raw["predictions"]
        explanation = deps["convert_numpy_types"](raw["explanation"])

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
            shap_values=deps["convert_numpy_types"](explanation["shap_values"]),
            top_factors=deps["convert_numpy_types"](explanation["top_factors"]),
            base_value=float(explanation["base_value"]),
            prediction_value=float(explanation["prediction_value"]),
        )
        response = EmployeeAnalysisResponse(prediction=prediction, explanation=explanation_response)
        deps["_set_cached"](cache_key, response.model_dump())
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/upload", response_model=EmployeeBulkResponse)
async def upload_employee_data(file: UploadFile = File(...)):
    """Upload a CSV file with employee data. Returns predictions for all employees."""
    deps = _get_deps()
    employee_model = deps["employee_model"]
    if not employee_model or not employee_model.is_fitted:
        raise HTTPException(status_code=503, detail="Employee model not loaded")

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        raw = await asyncio.to_thread(deps["_sync_upload_employee_bulk"], df)
        predictions = raw["predictions"]
        df = raw["df"]

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

        summary = {
            "high_attrition_risk_count": len([r for r in results if r.attrition_risk == "High"]),
            "medium_attrition_risk_count": len([r for r in results if r.attrition_risk == "Medium"]),
            "low_attrition_risk_count": len([r for r in results if r.attrition_risk == "Low"]),
            "avg_retention_score": float(predictions["retention_score"].mean()),
            "avg_attrition_probability": float(predictions["attrition_probability"].mean()),
            "high_layoff_priority_count": len([r for r in results if r.layoff_priority == "High"]),
        }

        deps["_append_analysis"](
            "Employee Scoring",
            f"Bulk ({len(results)} employees)",
            f"{summary['high_attrition_risk_count']} High / {summary['low_attrition_risk_count']} Low Risk",
            f"Avg retention {summary['avg_retention_score']:.1f}",
            {"total_employees": len(results)},
        )
        return EmployeeBulkResponse(total_employees=len(results), predictions=results, summary=summary)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload processing failed: {str(e)}")


@router.post("/simulate-layoff", response_model=LayoffSimulationResponse)
async def simulate_layoffs(
    budget_cut_percent: float,
    min_per_dept: int = 1,
    file: UploadFile = File(...),
):
    """Simulate layoff recommendations based on budget constraints."""
    deps = _get_deps()
    employee_model = deps["employee_model"]
    if not employee_model or not employee_model.is_fitted:
        raise HTTPException(status_code=503, detail="Employee model not loaded")

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

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
                deps["_sync_simulate_layoffs"], df, budget_cut_percent, min_per_dept
            )
        finally:
            sys.stdout = old_stdout

        total_payroll = df["monthly_income"].sum()
        target_savings = total_payroll * (budget_cut_percent / 100)
        actual_savings = result_df[result_df["layoff_recommended"]]["monthly_income"].sum()
        n_layoffs = result_df["layoff_recommended"].sum()

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

        dept_breakdown = result_df[result_df["layoff_recommended"]].groupby("department").size().to_dict()

        deps["_append_analysis"](
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


@router.get("/feature-importance", response_model=FeatureImportanceResponse)
async def get_employee_feature_importance():
    """Get feature importance from the employee scoring model."""
    deps = _get_deps()
    employee_model = deps["employee_model"]
    if not employee_model or not employee_model.is_fitted:
        raise HTTPException(status_code=503, detail="Employee model not loaded")

    try:
        importance = dict(zip(
            employee_model.feature_names,
            employee_model.model.feature_importances_.tolist()
        ))
        importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
        return FeatureImportanceResponse(feature_importance=importance, model_metrics=employee_model.metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feature importance: {str(e)}")


@router.post("/explain-row", response_model=EmployeeAnalysisResponse)
async def explain_employee_row(file: UploadFile = File(...), row_index: int = 0):
    """Get prediction + SHAP explanation for a single row from a bulk employee CSV."""
    deps = _get_deps()
    employee_model = deps["employee_model"]
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
        cached = deps["_get_cached"](cache_key)
        if cached is not None:
            return EmployeeAnalysisResponse(**cached)
        raw = await asyncio.to_thread(deps["_sync_explain_employee_row"], df, row_index)
        predictions = raw["predictions"]
        explanation = deps["convert_numpy_types"](raw["explanation"])
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
            shap_values=deps["convert_numpy_types"](explanation["shap_values"]),
            top_factors=deps["convert_numpy_types"](explanation["top_factors"]),
            base_value=float(explanation["base_value"]),
            prediction_value=float(explanation["prediction_value"]),
        )
        response = EmployeeAnalysisResponse(prediction=prediction, explanation=explanation_response)
        deps["_set_cached"](cache_key, response.model_dump())
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explain row failed: {str(e)}")
