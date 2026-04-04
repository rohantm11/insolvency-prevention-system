"""
Insolvency Prevention System - Stress Test Suite (20 scenarios).

Runs 20 stress tests against the API, collects metrics, and generates a PDF report.
Ensure the backend is running (e.g. uvicorn app.main:app --host 127.0.0.1 --port 8000) before running.

Usage:
    From project root with backend venv activated:
        python scripts/stress_tests.py
        python scripts/stress_tests.py --base-url http://127.0.0.1:8000 --output-dir reports
"""

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Add project root for imports
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    import httpx
except ImportError:
    print("Install httpx: pip install httpx")
    sys.exit(1)

# Sample payloads for POST endpoints
FINANCIAL_PAYLOAD = {
    "company_id": "STRESS_001",
    "company_name": "Stress Test Corp",
    "working_capital_to_total_assets": 0.25,
    "retained_earnings_to_total_assets": 0.35,
    "ebit_to_total_assets": 0.12,
    "market_value_equity_to_total_liabilities": 2.5,
    "sales_to_total_assets": 1.2,
    "current_ratio": 2.0,
    "quick_ratio": 1.5,
    "debt_to_equity": 0.8,
    "interest_coverage": 5.0,
    "net_profit_margin": 0.10,
    "return_on_assets": 0.08,
    "return_on_equity": 0.15,
}

EMPLOYEE_PAYLOAD = {
    "employee_id": "EMP_STRESS_001",
    "name": "Stress User",
    "age": 35,
    "gender": "Male",
    "department": "Engineering",
    "job_role": "Software Engineer",
    "job_level": 3,
    "performance_rating": 3,
    "job_satisfaction": 3,
    "job_involvement": 3,
    "environment_satisfaction": 3,
    "monthly_income": 8000,
    "percent_salary_hike": 15,
    "stock_option_level": 1,
    "years_at_company": 5,
    "years_in_current_role": 3,
    "total_working_years": 10,
    "distance_from_home": 10,
    "business_travel": "Travel_Rarely",
    "over_time": "No",
}

INSOLVENCY_REPORT_PAYLOAD = {
    "company_id": "STRESS_001",
    "company_name": "Stress Test Corp",
    "company_data": FINANCIAL_PAYLOAD,
}


@dataclass
class SingleResult:
    status_code: int
    latency_ms: float
    error: str | None = None


@dataclass
class StressTestResult:
    name: str
    scenario: str
    method: str
    endpoint: str
    total_requests: int
    concurrency: int
    success_count: int
    fail_count: int
    min_latency_ms: float
    avg_latency_ms: float
    max_latency_ms: float
    p95_latency_ms: float
    errors: list[str] = field(default_factory=list)
    passed: bool = True

    def to_dict(self):
        return asdict(self)


def run_one_request(
    base_url: str,
    method: str,
    path: str,
    json_body: dict | None = None,
    timeout: float = 60.0,
) -> SingleResult:
    url = base_url.rstrip("/") + path
    start = time.perf_counter()
    try:
        with httpx.Client(timeout=timeout) as client:
            if method == "GET":
                r = client.get(url)
            else:
                r = client.post(url, json=json_body or {})
        elapsed_ms = (time.perf_counter() - start) * 1000
        return SingleResult(status_code=r.status_code, latency_ms=elapsed_ms, error=None)
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return SingleResult(status_code=-1, latency_ms=elapsed_ms, error=str(e))


def run_sequential(
    base_url: str,
    method: str,
    path: str,
    json_body: dict | None,
    n: int,
    timeout: float = 60.0,
) -> list[SingleResult]:
    return [run_one_request(base_url, method, path, json_body, timeout) for _ in range(n)]


def run_concurrent(
    base_url: str,
    method: str,
    path: str,
    json_body: dict | None,
    n: int,
    timeout: float = 60.0,
) -> list[SingleResult]:
    with ThreadPoolExecutor(max_workers=min(n, 50)) as ex:
        futures = [
            ex.submit(run_one_request, base_url, method, path, json_body, timeout)
            for _ in range(n)
        ]
        return [f.result() for f in as_completed(futures)]


def summarize_results(name: str, scenario: str, method: str, endpoint: str, results: list[SingleResult], concurrency: int) -> StressTestResult:
    success = [r for r in results if r.status_code and 200 <= r.status_code < 300]
    failed = [r for r in results if r not in success]
    latencies = [r.latency_ms for r in success]
    errors = [r.error or f"HTTP {r.status_code}" for r in failed]
    passed = len(failed) == 0
    if not latencies:
        min_lat = max_lat = avg_lat = p95_lat = 0.0
    else:
        min_lat = min(latencies)
        max_lat = max(latencies)
        avg_lat = sum(latencies) / len(latencies)
        sorted_lat = sorted(latencies)
        p95_lat = sorted_lat[int(len(sorted_lat) * 0.95)] if sorted_lat else 0.0
    return StressTestResult(
        name=name,
        scenario=scenario,
        method=method,
        endpoint=endpoint,
        total_requests=len(results),
        concurrency=concurrency,
        success_count=len(success),
        fail_count=len(failed),
        min_latency_ms=round(min_lat, 2),
        avg_latency_ms=round(avg_lat, 2),
        max_latency_ms=round(max_lat, 2),
        p95_latency_ms=round(p95_lat, 2),
        errors=errors[:10],
        passed=passed,
    )


def run_stress_tests(base_url: str, timeout: float = 60.0) -> list[StressTestResult]:
    results: list[StressTestResult] = []

    # 1. Health check - 50 sequential
    r1 = run_sequential(base_url, "GET", "/api/health", None, 50, timeout)
    results.append(summarize_results(
        "Health check sequential (50)", "Sequential load", "GET", "/api/health", r1, 1
    ))

    # 2. Health check - 20 concurrent
    r2 = run_concurrent(base_url, "GET", "/api/health", None, 20, timeout)
    results.append(summarize_results(
        "Health check concurrent (20)", "Concurrent load", "GET", "/api/health", r2, 20
    ))

    # 3. Recent analyses - 30 sequential
    r3 = run_sequential(base_url, "GET", "/api/analyses/recent", None, 30, timeout)
    results.append(summarize_results(
        "Recent analyses sequential (30)", "Sequential load", "GET", "/api/analyses/recent", r3, 1
    ))

    # 4. Recent analyses - 15 concurrent
    r4 = run_concurrent(base_url, "GET", "/api/analyses/recent", None, 15, timeout)
    results.append(summarize_results(
        "Recent analyses concurrent (15)", "Concurrent load", "GET", "/api/analyses/recent", r4, 15
    ))

    # 5. Financial analyze - 10 sequential
    r5 = run_sequential(base_url, "POST", "/api/financial/analyze", FINANCIAL_PAYLOAD, 10, timeout)
    results.append(summarize_results(
        "Financial analyze sequential (10)", "Sequential load", "POST", "/api/financial/analyze", r5, 1
    ))

    # 6. Financial analyze - 5 concurrent
    r6 = run_concurrent(base_url, "POST", "/api/financial/analyze", FINANCIAL_PAYLOAD, 5, timeout)
    results.append(summarize_results(
        "Financial analyze concurrent (5)", "Concurrent load", "POST", "/api/financial/analyze", r6, 5
    ))

    # 7. Financial analyze - invalid payload (expect 422)
    r7 = run_one_request(base_url, "POST", "/api/financial/analyze", {"invalid": "payload"}, timeout)
    passed_7 = r7.status_code == 422
    results.append(StressTestResult(
        name="Financial analyze invalid payload",
        scenario="Validation stress",
        method="POST",
        endpoint="/api/financial/analyze",
        total_requests=1,
        concurrency=1,
        success_count=1 if passed_7 else 0,
        fail_count=0 if passed_7 else 1,
        min_latency_ms=r7.latency_ms,
        avg_latency_ms=r7.latency_ms,
        max_latency_ms=r7.latency_ms,
        p95_latency_ms=r7.latency_ms,
        errors=[] if passed_7 else [r7.error or f"HTTP {r7.status_code}"],
        passed=passed_7,
    ))

    # 8. Financial feature importance - 20 sequential
    r8 = run_sequential(base_url, "GET", "/api/financial/feature-importance", None, 20, timeout)
    results.append(summarize_results(
        "Financial feature importance (20)", "Sequential load", "GET", "/api/financial/feature-importance", r8, 1
    ))

    # 9. Employee analyze - 10 sequential
    r9 = run_sequential(base_url, "POST", "/api/employee/analyze", EMPLOYEE_PAYLOAD, 10, timeout)
    results.append(summarize_results(
        "Employee analyze sequential (10)", "Sequential load", "POST", "/api/employee/analyze", r9, 1
    ))

    # 10. Employee analyze - 5 concurrent
    r10 = run_concurrent(base_url, "POST", "/api/employee/analyze", EMPLOYEE_PAYLOAD, 5, timeout)
    results.append(summarize_results(
        "Employee analyze concurrent (5)", "Concurrent load", "POST", "/api/employee/analyze", r10, 5
    ))

    # 11. Employee analyze - invalid payload (expect 422)
    r11 = run_one_request(base_url, "POST", "/api/employee/analyze", {"age": 10}, timeout)
    passed_11 = r11.status_code == 422
    results.append(StressTestResult(
        name="Employee analyze invalid payload",
        scenario="Validation stress",
        method="POST",
        endpoint="/api/employee/analyze",
        total_requests=1,
        concurrency=1,
        success_count=1 if passed_11 else 0,
        fail_count=0 if passed_11 else 1,
        min_latency_ms=r11.latency_ms,
        avg_latency_ms=r11.latency_ms,
        max_latency_ms=r11.latency_ms,
        p95_latency_ms=r11.latency_ms,
        errors=[] if passed_11 else [r11.error or f"HTTP {r11.status_code}"],
        passed=passed_11,
    ))

    # 12. Employee feature importance - 20 sequential
    r12 = run_sequential(base_url, "GET", "/api/employee/feature-importance", None, 20, timeout)
    results.append(summarize_results(
        "Employee feature importance (20)", "Sequential load", "GET", "/api/employee/feature-importance", r12, 1
    ))

    # 13. Templates company - 20 sequential
    r13 = run_sequential(base_url, "GET", "/api/templates/company", None, 20, timeout)
    results.append(summarize_results(
        "Templates company (20)", "Sequential load", "GET", "/api/templates/company", r13, 1
    ))

    # 14. Templates employee - 20 sequential
    r14 = run_sequential(base_url, "GET", "/api/templates/employee", None, 20, timeout)
    results.append(summarize_results(
        "Templates employee (20)", "Sequential load", "GET", "/api/templates/employee", r14, 1
    ))

    # 15. Mixed workload - health + financial + employee concurrent (5 each = 15 total)
    def mixed_task(idx: int) -> SingleResult:
        if idx % 3 == 0:
            return run_one_request(base_url, "GET", "/api/health", None, timeout)
        if idx % 3 == 1:
            return run_one_request(base_url, "POST", "/api/financial/analyze", FINANCIAL_PAYLOAD, timeout)
        return run_one_request(base_url, "POST", "/api/employee/analyze", EMPLOYEE_PAYLOAD, timeout)

    with ThreadPoolExecutor(max_workers=15) as ex:
        mixed_futures = [ex.submit(mixed_task, i) for i in range(15)]
        r15 = [f.result() for f in as_completed(mixed_futures)]
    results.append(summarize_results(
        "Mixed workload concurrent (15)", "Mixed concurrent", "GET/POST", "health+financial+employee", r15, 15
    ))

    # 16. Sustained load - 100 health requests
    r16 = run_sequential(base_url, "GET", "/api/health", None, 100, timeout)
    results.append(summarize_results(
        "Sustained health load (100)", "Sustained load", "GET", "/api/health", r16, 1
    ))

    # 17. Financial analyze throughput - 20 sequential
    r17 = run_sequential(base_url, "POST", "/api/financial/analyze", FINANCIAL_PAYLOAD, 20, timeout)
    results.append(summarize_results(
        "Financial analyze throughput (20)", "Throughput", "POST", "/api/financial/analyze", r17, 1
    ))

    # 18. Reports insolvency - 3 sequential (heavy)
    r18 = run_sequential(base_url, "POST", "/api/reports/insolvency", INSOLVENCY_REPORT_PAYLOAD, 3, timeout)
    results.append(summarize_results(
        "Report insolvency (3)", "Heavy sequential", "POST", "/api/reports/insolvency", r18, 1
    ))

    # 19. Error recovery - invalid then valid
    run_one_request(base_url, "POST", "/api/financial/analyze", {"invalid": "payload"}, timeout)
    r19 = run_sequential(base_url, "POST", "/api/financial/analyze", FINANCIAL_PAYLOAD, 5, timeout)
    results.append(summarize_results(
        "Error recovery (invalid then 5 valid)", "Recovery", "POST", "/api/financial/analyze", r19, 1
    ))

    # 20. High concurrency health - 30 concurrent
    r20 = run_concurrent(base_url, "GET", "/api/health", None, 30, timeout)
    results.append(summarize_results(
        "High concurrency health (30)", "High concurrency", "GET", "/api/health", r20, 30
    ))

    return results


def generate_pdf_report(results: list[StressTestResult], output_path: Path) -> None:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError:
        print("ReportLab not found. Install with: pip install reportlab")
        return

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="CustomTitle",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=12,
    )
    story = []

    story.append(Paragraph("Stress Test Report – Insolvency Prevention System", title_style))
    story.append(Paragraph(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    story.append(Paragraph(
        f"<b>Summary:</b> {len(results)} tests run. Passed: {passed}, Failed: {failed}.",
        styles["Normal"],
    ))
    story.append(Spacer(1, 0.2 * inch))

    # Table: Test name, Pass/Fail, Requests, Success, Fail, Avg latency (ms), P95 (ms)
    data = [["#", "Test", "Pass", "Total", "OK", "Fail", "Avg (ms)", "P95 (ms)"]]
    for i, r in enumerate(results, 1):
        data.append([
            str(i),
            r.name[:40] + ("..." if len(r.name) > 40 else ""),
            "Yes" if r.passed else "No",
            str(r.total_requests),
            str(r.success_count),
            str(r.fail_count),
            f"{r.avg_latency_ms:.1f}",
            f"{r.p95_latency_ms:.1f}",
        ])
    t = Table(data, colWidths=[0.35 * inch, 2.8 * inch, 0.45 * inch, 0.5 * inch, 0.4 * inch, 0.4 * inch, 0.7 * inch, 0.7 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph("Recommendations", styles["Heading2"]))
    if failed > 0:
        story.append(Paragraph(
            "• Review failed tests and ensure the backend is running and models are loaded.",
            styles["Normal"],
        ))
    story.append(Paragraph(
        "• Monitor P95 latency under production load; consider caching for heavy endpoints.",
        styles["Normal"],
    ))
    story.append(Paragraph(
        "• Run tests periodically (e.g. in CI) to catch regressions.",
        styles["Normal"],
    ))

    doc.build(story)
    print(f"PDF report written to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Run 20 stress tests and generate PDF report")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="API base URL")
    parser.add_argument("--output-dir", default=None, help="Output directory for JSON and PDF (default: project reports/)")
    parser.add_argument("--timeout", type=float, default=60.0, help="Request timeout in seconds")
    parser.add_argument("--no-pdf", action="store_true", help="Skip PDF generation")
    args = parser.parse_args()

    out_dir = Path(args.output_dir) if args.output_dir else project_root / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Running 20 stress tests...")
    print(f"Base URL: {args.base_url}")
    start = time.perf_counter()
    results = run_stress_tests(args.base_url, args.timeout)
    elapsed = time.perf_counter() - start
    print(f"Completed in {elapsed:.1f}s. Passed: {sum(1 for r in results if r.passed)} / {len(results)}")

    results_dict = [r.to_dict() for r in results]
    json_path = out_dir / "stress_test_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"elapsed_seconds": round(elapsed, 2), "results": results_dict}, f, indent=2)
    print(f"JSON results written to: {json_path}")

    if not args.no_pdf:
        pdf_path = out_dir / "stress_test_report.pdf"
        generate_pdf_report(results, pdf_path)


if __name__ == "__main__":
    main()
