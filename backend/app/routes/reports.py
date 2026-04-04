"""Report generation routes."""

import asyncio
import io
import sys
from typing import Literal

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from app.models.schemas import (
    InsolvencyReportRequest,
    LayoffReportRequest,
)

router = APIRouter(prefix="/api/reports", tags=["Reports"])


def _get_main_module():
    """Get the main module regardless of import path."""
    import sys
    return sys.modules.get("backend.app.main") or sys.modules.get("app.main")


def _get_deps():
    """Lazy import to avoid circular dependencies with main module globals."""
    m = _get_main_module()
    return {
        "insolvency_model": m.insolvency_model,
        "employee_model": m.employee_model,
        "pdf_generator": m.pdf_generator,
        "convert_numpy_types": m.convert_numpy_types,
        "_sync_analyze_company": m._sync_analyze_company,
        "_sync_simulate_layoffs": m._sync_simulate_layoffs,
    }


@router.post("/generate")
async def generate_report(
    report_type: Literal["insolvency", "layoff"],
    request: InsolvencyReportRequest | None = None,
    layoff_request: LayoffReportRequest | None = None,
    file: UploadFile | None = File(None),
):
    """Generate a PDF report."""
    deps = _get_deps()
    if not deps["pdf_generator"]:
        raise HTTPException(status_code=503, detail="PDF generator not initialized")

    try:
        if report_type == "insolvency":
            return await _generate_insolvency_report_impl(deps, request)
        elif report_type == "layoff":
            return await _generate_layoff_report_impl(deps, layoff_request, file)
        else:
            raise HTTPException(status_code=400, detail="Invalid report_type. Use 'insolvency' or 'layoff'")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.post("/insolvency")
async def generate_insolvency_report(request: InsolvencyReportRequest):
    """Generate an insolvency risk assessment PDF report."""
    deps = _get_deps()
    return await _generate_insolvency_report_impl(deps, request)


@router.post("/layoff")
async def generate_layoff_report(
    budget_cut_percent: float,
    min_per_dept: int = 1,
    file: UploadFile = File(...),
):
    """Generate a layoff simulation PDF report."""
    deps = _get_deps()
    layoff_request = LayoffReportRequest(
        budget_cut_percent=budget_cut_percent,
        min_per_dept=min_per_dept
    )
    return await _generate_layoff_report_impl(deps, layoff_request, file)


async def _generate_insolvency_report_impl(deps: dict, request: InsolvencyReportRequest | None):
    """Internal function to generate insolvency report."""
    if not request:
        raise HTTPException(status_code=400, detail="Request body required for insolvency report")
    if not deps["insolvency_model"] or not deps["insolvency_model"].is_fitted:
        raise HTTPException(status_code=503, detail="Insolvency model not loaded")
    if not deps["pdf_generator"]:
        raise HTTPException(status_code=503, detail="PDF generator not initialized")

    company_data = request.company_data.model_dump()
    raw = await asyncio.to_thread(deps["_sync_analyze_company"], company_data)
    predictions = raw["predictions"]
    z_scores = raw["z_scores"]
    explanation = raw["explanation"]

    prediction_dict = {
        "probability_of_distress": float(predictions["probability_of_distress"].iloc[0]),
        "risk_category": predictions["risk_category"].iloc[0],
        "estimated_time_to_event": int(predictions["estimated_time_to_event"].iloc[0])
            if pd.notna(predictions["estimated_time_to_event"].iloc[0]) else None,
        "z_score": float(z_scores["z_score"].iloc[0]),
        "z_score_zone": z_scores["z_score_zone"].iloc[0],
    }

    pdf_bytes = deps["pdf_generator"].generate_insolvency_report(
        company_id=request.company_id,
        company_name=request.company_name,
        prediction=prediction_dict,
        explanation=explanation,
    )

    filename = f"insolvency_report_{request.company_id}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


async def _generate_layoff_report_impl(
    deps: dict,
    request: LayoffReportRequest | None,
    file: UploadFile | None
):
    """Internal function to generate layoff report."""
    if not request:
        raise HTTPException(status_code=400, detail="Request parameters required for layoff report")
    if not file:
        raise HTTPException(status_code=400, detail="Employee CSV file required for layoff report")
    if not deps["employee_model"] or not deps["employee_model"].is_fitted:
        raise HTTPException(status_code=503, detail="Employee model not loaded")
    if not deps["pdf_generator"]:
        raise HTTPException(status_code=503, detail="PDF generator not initialized")
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

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
            deps["_sync_simulate_layoffs"],
            df,
            request.budget_cut_percent,
            request.min_per_dept,
        )
    finally:
        sys.stdout = old_stdout

    total_payroll = df["monthly_income"].sum()
    target_savings = total_payroll * (request.budget_cut_percent / 100)
    actual_savings = result_df[result_df["layoff_recommended"]]["monthly_income"].sum()
    n_layoffs = result_df["layoff_recommended"].sum()

    simulation_params = {
        "budget_cut_percent": request.budget_cut_percent,
        "min_per_dept": request.min_per_dept,
    }

    summary = {
        "target_monthly_savings": float(target_savings),
        "actual_monthly_savings": float(actual_savings),
        "employees_affected": int(n_layoffs),
        "savings_achieved_percent": float((actual_savings / total_payroll) * 100) if total_payroll > 0 else 0,
    }

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

    dept_breakdown = result_df[result_df["layoff_recommended"]].groupby("department").size().to_dict()

    pdf_bytes = deps["pdf_generator"].generate_layoff_report(
        simulation_params=simulation_params,
        summary=summary,
        recommendations=recommendations,
        department_breakdown=dept_breakdown,
    )

    filename = f"layoff_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
