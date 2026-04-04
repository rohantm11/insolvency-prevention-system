"""
Generate synthetic data for the SolvencyInsight Insolvency Prediction System.

All financial ratios are derived from a single coherent synthetic balance sheet
and income statement per company — not sampled independently.

Generation pipeline:
  1. Sample base financial statement primitives per industry
  2. Compute every balance-sheet line item from those primitives
  3. Derive all ratios mathematically (DuPont identity holds,
     Quick <= Current always, Interest Coverage = EBIT / Interest Expense)
  4. Compute Altman Z-score; use it to assign bankruptcy label

Industry parameters calibrated to US benchmarks (Damodaran 2025,
Eqvista 2025, FullRatio 2026).
"""

import numpy as np
import pandas as pd
from pathlib import Path


COMPANY_PREFIXES = [
    "Global", "United", "Premier", "Advanced", "Dynamic", "Strategic", "Prime",
    "Elite", "Apex", "Summit", "Horizon", "Pinnacle", "Vanguard", "Pioneer",
    "Quantum", "Stellar", "Alpha", "Omega", "Nova", "Titan",
]

COMPANY_SUFFIXES = [
    "Industries", "Solutions", "Technologies", "Systems", "Enterprises", "Corp",
    "Holdings", "Group", "Partners", "Dynamics", "Innovations", "Ventures",
    "Services", "International", "Logistics", "Manufacturing",
]

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph",
    "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Lisa",
    "Daniel", "Nancy", "Matthew", "Betty", "Anthony", "Margaret", "Mark",
    "Sandra", "Donald", "Ashley", "Steven", "Kimberly", "Paul", "Emily",
    "Andrew", "Donna", "Joshua", "Michelle", "Kenneth", "Dorothy", "Kevin",
    "Carol", "Brian", "Amanda", "George", "Melissa", "Timothy", "Deborah",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson",
    "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez",
    "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis",
    "Robinson", "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres",
    "Nguyen", "Hill", "Flores",
]

DEPARTMENTS = [
    "Sales", "Research & Development", "Human Resources", "Finance", "Marketing",
    "Operations", "Engineering", "Customer Service", "IT", "Legal",
]

JOB_ROLES = {
    "Sales": ["Sales Representative", "Account Manager", "Sales Director", "Business Development"],
    "Research & Development": ["Research Scientist", "Product Developer", "R&D Manager", "Lab Technician"],
    "Human Resources": ["HR Specialist", "Recruiter", "HR Manager", "Training Coordinator"],
    "Finance": ["Financial Analyst", "Accountant", "Finance Manager", "Controller"],
    "Marketing": ["Marketing Specialist", "Content Creator", "Marketing Manager", "Brand Strategist"],
    "Operations": ["Operations Analyst", "Process Engineer", "Operations Manager", "Quality Specialist"],
    "Engineering": ["Software Engineer", "Mechanical Engineer", "Engineering Manager", "Technical Lead"],
    "Customer Service": ["Support Specialist", "Customer Success Manager", "Service Representative", "Support Lead"],
    "IT": ["System Administrator", "Network Engineer", "IT Manager", "Security Analyst"],
    "Legal": ["Legal Counsel", "Compliance Officer", "Paralegal", "Contract Specialist"],
}

# Industry parameters calibrated to published US benchmarks.
# Each entry: (ebit_margin_mu, sigma, ca/ta_mu, sigma,
#              equity_ratio_mu, sigma, interest_rate, asset_turnover_mu, sigma)
INDUSTRY_PARAMS = {
    "Technology":          (0.18, 0.07, 0.55, 0.10, 0.62, 0.12, 0.045, 0.85, 0.25),
    "Manufacturing":       (0.09, 0.05, 0.40, 0.08, 0.48, 0.12, 0.050, 0.90, 0.20),
    "Healthcare":          (0.14, 0.06, 0.52, 0.10, 0.55, 0.12, 0.048, 0.70, 0.20),
    "Financial Services":  (0.22, 0.08, 0.30, 0.08, 0.12, 0.06, 0.030, 0.25, 0.10),
    "Retail":              (0.05, 0.03, 0.38, 0.07, 0.38, 0.10, 0.052, 1.80, 0.40),
    "Energy":              (0.12, 0.07, 0.32, 0.08, 0.40, 0.12, 0.055, 0.55, 0.15),
    "Transportation":      (0.07, 0.04, 0.28, 0.07, 0.35, 0.10, 0.053, 0.80, 0.20),
    "Construction":        (0.07, 0.04, 0.55, 0.08, 0.42, 0.10, 0.055, 1.10, 0.25),
    "Telecommunications":  (0.20, 0.07, 0.28, 0.07, 0.25, 0.08, 0.048, 0.45, 0.12),
    "Real Estate":         (0.15, 0.06, 0.18, 0.06, 0.30, 0.10, 0.050, 0.25, 0.10),
}
INDUSTRIES = list(INDUSTRY_PARAMS.keys())


def altman_z(wc_ta, re_ta, ebit_ta, mve_tl, sales_ta):
    return 1.2 * wc_ta + 1.4 * re_ta + 3.3 * ebit_ta + 0.6 * mve_tl + 1.0 * sales_ta


def _clip(arr, lo, hi):
    return np.clip(arr, lo, hi)


def _build_cohort(n, industry, distressed=False, rng=None):
    """
    Build n synthetic companies from a single coherent financial statement.

    All ratios are derived from the same balance sheet primitives —
    never sampled independently. This guarantees internal consistency:
      - ROA = NPM × asset_turnover       (DuPont identity)
      - ROE = ROA / equity_ratio         (leverage identity)
      - Quick Ratio <= Current Ratio     (by construction)
      - Interest Coverage = EBIT / Interest Expense
    """
    if rng is None:
        rng = np.random.default_rng()

    p = INDUSTRY_PARAMS[industry]
    (ebit_mu, ebit_sig,
     ca_ta_mu, ca_ta_sig,
     eq_r_mu, eq_r_sig,
     int_rate_base,
     turn_mu, turn_sig) = p

    if distressed:
        equity_ratio   = rng.normal(eq_r_mu * 0.20, eq_r_sig * 1.5, n)
        ebit_margin    = rng.normal(-0.04, ebit_sig * 1.6, n)
        ca_ta          = _clip(rng.normal(ca_ta_mu * 0.60, ca_ta_sig * 1.3, n), 0.05, 0.75)
        inv_ca_ratio   = _clip(rng.normal(0.50, 0.12, n), 0.10, 0.85)
        asset_turnover = _clip(rng.normal(turn_mu * 0.55, turn_sig * 1.3, n), 0.05, 4.0)
        interest_rate  = _clip(rng.normal(int_rate_base * 2.2, 0.025, n), 0.04, 0.20)
        re_bleed       = rng.uniform(0.15, 0.50, n)
    else:
        equity_ratio   = _clip(rng.normal(eq_r_mu, eq_r_sig, n), 0.10, 0.95)
        ebit_margin    = _clip(rng.normal(ebit_mu, ebit_sig, n), 0.005, 0.55)
        ca_ta          = _clip(rng.normal(ca_ta_mu, ca_ta_sig, n), 0.10, 0.90)
        inv_ca_ratio   = _clip(rng.normal(0.30, 0.10, n), 0.05, 0.70)
        asset_turnover = _clip(rng.normal(turn_mu, turn_sig, n), 0.05, 5.0)
        interest_rate  = _clip(rng.normal(int_rate_base, 0.010, n), 0.015, 0.12)
        re_bleed       = np.zeros(n)

    # Step 1 — Absolute balance sheet ($M)
    total_assets        = rng.uniform(10, 5_000, n)
    equity              = total_assets * equity_ratio
    total_liabilities   = total_assets - equity
    cl_ratio            = _clip(rng.normal(0.45, 0.12, n), 0.10, 0.90)
    current_liabilities = total_liabilities * cl_ratio
    long_term_debt      = total_liabilities * (1 - cl_ratio)
    current_assets      = total_assets * ca_ta
    fixed_assets        = total_assets - current_assets
    inventory           = current_assets * inv_ca_ratio
    liquid_assets       = current_assets - inventory

    # Step 2 — Income statement
    sales            = total_assets * asset_turnover
    ebit             = sales * ebit_margin
    interest_expense = total_liabilities * interest_rate
    ebt              = ebit - interest_expense
    tax_rate         = _clip(rng.normal(0.22, 0.04, n), 0.10, 0.38)
    net_income       = ebt * (1 - tax_rate)
    net_income       = np.where(
        distressed,
        ebt * _clip(1 - tax_rate, 0.0, 1.0),
        net_income,
    )

    # Step 3 — Retained earnings (via company age + past ROA)
    company_age      = rng.integers(3, 40, n)
    annual_re_rate   = np.where(
        distressed,
        -re_bleed / np.maximum(company_age, 1),
        net_income / total_assets * rng.uniform(0.3, 0.7, n),
    )
    retained_earnings = total_assets * annual_re_rate * company_age * rng.uniform(0.5, 1.5, n)
    retained_earnings = np.clip(retained_earnings, -total_assets * 0.60, equity * 0.95)

    # Step 4 — Market value of equity
    pe_mult              = rng.uniform(2.0, 8.0, n) if distressed else rng.uniform(8.0, 25.0, n)
    net_income_positive  = np.maximum(net_income, total_assets * 0.001)
    mve                  = net_income_positive * pe_mult

    # Step 5 — Derive all ratios
    working_capital = current_assets - current_liabilities
    ta_safe  = np.maximum(total_assets, 1e-6)
    tl_safe  = np.maximum(total_liabilities, 1e-6)
    cl_safe  = np.maximum(current_liabilities, 1e-6)
    sl_safe  = np.maximum(sales, 1e-6)
    ie_safe  = np.maximum(interest_expense, 1e-6)

    wc_ta   = working_capital   / ta_safe
    re_ta   = retained_earnings / ta_safe
    ebit_ta = ebit              / ta_safe
    mve_tl  = mve               / tl_safe
    s_ta    = sales             / ta_safe

    current_ratio     = current_assets / cl_safe
    quick_ratio       = liquid_assets  / cl_safe      # always <= current_ratio
    debt_to_equity    = total_liabilities / np.maximum(equity, ta_safe * 0.01)
    interest_coverage = ebit / ie_safe
    net_profit_margin = net_income / sl_safe
    roa               = net_income / ta_safe
    roe               = net_income / np.maximum(equity, ta_safe * 0.01)

    return {
        "wc_ta": wc_ta, "re_ta": re_ta, "ebit_ta": ebit_ta,
        "mve_tl": mve_tl, "s_ta": s_ta,
        "current_ratio": current_ratio, "quick_ratio": quick_ratio,
        "debt_to_equity": debt_to_equity, "interest_coverage": interest_coverage,
        "net_profit_margin": net_profit_margin, "roa": roa, "roe": roe,
        "altman_z": altman_z(wc_ta, re_ta, ebit_ta, mve_tl, s_ta),
        "company_age": company_age,
    }


def generate_company_data(n_samples: int = 1000, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic company financial data for insolvency prediction.

    All ratios are derived from a single coherent balance sheet —
    never sampled independently. DuPont identity holds, Quick <= Current
    always, Interest Coverage = EBIT / Interest Expense.

    Bankruptcy label is assigned using the Altman Z-score computed from
    the generated data, with a stochastic grey-zone to mimic real-world
    overlap (Z < 1.81 = distress zone, Z > 2.99 = safe zone).

    Args:
        n_samples : Total company records (default 1000)
        seed      : Random seed for reproducibility

    Returns:
        DataFrame conforming to the column contract expected by
        scripts/train_models.py and backend/app/main.py
    """
    rng = np.random.default_rng(seed)

    n_bankrupt = max(1, int(n_samples * 0.20))
    n_healthy  = n_samples - n_bankrupt

    industries_h = rng.choice(INDUSTRIES, n_healthy,  replace=True)
    industries_b = rng.choice(INDUSTRIES, n_bankrupt, replace=True)

    def build_for_industries(industry_arr, distressed):
        unique, counts = np.unique(industry_arr, return_counts=True)
        cohorts = {}
        for ind, cnt in zip(unique, counts):
            cohorts[ind] = _build_cohort(cnt, ind, distressed=distressed, rng=rng)
        idx_map = {ind: 0 for ind in unique}
        result  = {k: np.empty(len(industry_arr)) for k in next(iter(cohorts.values()))}
        for i, ind in enumerate(industry_arr):
            src = cohorts[ind]
            j   = idx_map[ind]
            for k in result:
                result[k][i] = src[k][j]
            idx_map[ind] += 1
        return result

    h = build_for_industries(industries_h, distressed=False)
    b = build_for_industries(industries_b, distressed=True)

    def cat(key):
        return np.concatenate([h[key], b[key]])

    is_bankrupt_raw = np.array([0] * n_healthy + [1] * n_bankrupt)
    z_scores        = cat("altman_z")

    # Grey-zone label smoothing — mirrors real-world imperfection
    noise = rng.random(n_samples)
    grey_healthy_to_bankrupt = (is_bankrupt_raw == 0) & (z_scores < 1.81) & (noise < 0.15)
    grey_bankrupt_to_healthy = (is_bankrupt_raw == 1) & (z_scores > 2.99) & (noise < 0.10)
    is_bankrupt = is_bankrupt_raw.copy()
    is_bankrupt[grey_healthy_to_bankrupt] = 1
    is_bankrupt[grey_bankrupt_to_healthy] = 0

    years_to_bankruptcy = np.where(
        is_bankrupt == 1,
        rng.integers(1, 6, n_samples).astype(float),
        np.nan,
    )

    company_ids = [f"COMP_{i:04d}" for i in range(1, n_samples + 1)]
    # Build names without unbounded collision loop (prefix+suffix space is finite)
    base_names = [f"{p} {s}" for p in COMPANY_PREFIXES for s in COMPANY_SUFFIXES]
    rng.shuffle(base_names)
    if n_samples <= len(base_names):
        names = list(base_names[:n_samples])
    else:
        names = list(base_names) + [
            f"{rng.choice(COMPANY_PREFIXES)} {rng.choice(COMPANY_SUFFIXES)} #{i}"
            for i in range(1, n_samples - len(base_names) + 1)
        ]
    rng.shuffle(names)

    industries_all = np.concatenate([industries_h, industries_b])

    df = pd.DataFrame({
        "company_id":   company_ids,
        "company_name": names,
        "industry":     industries_all,
        "working_capital_to_total_assets":          np.round(cat("wc_ta"),   4),
        "retained_earnings_to_total_assets":        np.round(cat("re_ta"),   4),
        "ebit_to_total_assets":                     np.round(cat("ebit_ta"), 4),
        "market_value_equity_to_total_liabilities": np.round(cat("mve_tl"),  4),
        "sales_to_total_assets":                    np.round(cat("s_ta"),    4),
        "current_ratio":     np.round(cat("current_ratio"), 4),
        "quick_ratio":       np.round(cat("quick_ratio"),   4),
        "debt_to_equity":    np.round(np.clip(cat("debt_to_equity"),    -50,  200), 4),
        "interest_coverage": np.round(np.clip(cat("interest_coverage"), -30,   80), 4),
        "net_profit_margin": np.round(np.clip(cat("net_profit_margin"), -1.5, 1.5), 4),
        "return_on_assets":  np.round(np.clip(cat("roa"),               -1.0, 1.0), 4),
        "return_on_equity":  np.round(np.clip(cat("roe"),               -5.0, 5.0), 4),
        "altman_z_score":    np.round(z_scores, 4),
        "is_bankrupt":       is_bankrupt,
        "years_to_bankruptcy": years_to_bankruptcy,
    })

    df = df.sample(frac=1, random_state=int(seed)).reset_index(drop=True)
    return df


def generate_employee_data(n_samples: int = 5000, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic employee data for attrition prediction.

    Causal model:
      - Latent base_dissatisfaction drives all satisfaction scores
      - monthly_income = f(job_level, years_at_company, performance_rating)
      - job_level = f(age, total_working_years)
      - Temporal chain enforced: years_in_role <= years_at_company
        <= total_working_years <= (age - 22)
      - Attrition probability is a structured weighted sum of causal
        predictors, not a random assignment

    Args:
        n_samples : Number of employee records (default 5000)
        seed      : Random seed for reproducibility

    Returns:
        DataFrame conforming to the column contract expected by
        scripts/train_models.py and backend/app/main.py
    """
    rng = np.random.default_rng(seed)

    employee_ids = [f"EMP_{i:05d}" for i in range(1, n_samples + 1)]
    names = [
        f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
        for _ in range(n_samples)
    ]

    # Demographics
    ages    = rng.integers(22, 60, n_samples)
    genders = rng.choice(["Male", "Female"], n_samples, p=[0.52, 0.48])

    # Career progression: job_level is a function of age + experience
    total_working_years = np.array([
        rng.integers(0, max(1, int(a - 21))) for a in ages
    ])
    raw_level = 1 + total_working_years / 8 + rng.normal(0, 0.5, n_samples)
    job_levels = np.clip(np.round(raw_level).astype(int), 1, 5)

    # Temporal chain — enforced by construction
    years_at_company = np.array([
        rng.integers(0, max(1, int(tw + 1))) for tw in total_working_years
    ])
    years_in_current_role = np.array([
        rng.integers(0, max(1, int(yac + 1))) for yac in years_at_company
    ])

    # Structural drivers of dissatisfaction
    over_time = rng.choice(["Yes", "No"], n_samples, p=[0.28, 0.72])
    business_travel = rng.choice(
        ["Non-Travel", "Travel_Rarely", "Travel_Frequently"],
        n_samples, p=[0.15, 0.70, 0.15],
    )
    distance_from_home = rng.integers(1, 30, n_samples)

    overtime_flag = (over_time == "Yes").astype(float)
    travel_flag   = (business_travel == "Travel_Frequently").astype(float)
    distance_flag = (distance_from_home > 20).astype(float)
    new_hire_flag = (years_at_company < 2).astype(float)

    # Latent dissatisfaction (0 = very satisfied, 1 = very dissatisfied)
    structural_dissatisfaction = np.clip(
        0.30 * overtime_flag
        + 0.18 * travel_flag
        + 0.10 * distance_flag
        + 0.15 * new_hire_flag
        + rng.uniform(0, 0.30, n_samples),
        0, 1,
    )

    # All satisfaction scores co-vary through the shared latent factor
    def to_scale(latent, noise_scale=0.25):
        raw = 4 - 3 * latent + rng.normal(0, noise_scale, n_samples)
        return np.clip(np.round(raw).astype(int), 1, 4)

    job_satisfaction         = to_scale(structural_dissatisfaction, 0.30)
    environment_satisfaction = to_scale(structural_dissatisfaction, 0.30)
    job_involvement          = to_scale(structural_dissatisfaction * 0.7, 0.35)

    # Performance driven by involvement and dissatisfaction
    perf_raw = (
        4
        - 1.5 * structural_dissatisfaction
        + 0.5 * (job_involvement / 4)
        + rng.normal(0, 0.4, n_samples)
    )
    performance_rating = np.clip(np.round(perf_raw).astype(int), 1, 4)

    # Compensation: function of level, tenure, performance — not independent
    base_income    = 3_000 + (job_levels * 1_800) + (total_working_years * 120)
    perf_bonus     = (performance_rating - 2) * 400
    tenure_bonus   = years_at_company * 80
    monthly_income = np.clip(
        np.round(
            base_income + perf_bonus + tenure_bonus
            + rng.normal(0, 600, n_samples)
        ).astype(int),
        1_500, 25_000,
    )

    percent_salary_hike = np.clip(
        np.round(
            11 + (performance_rating - 1) * 3.5
            - (job_levels - 1) * 0.8
            + rng.normal(0, 1.5, n_samples)
        ).astype(int),
        11, 25,
    )
    stock_option_level = np.clip(
        np.round(
            (job_levels - 1) / 4 * 3 + rng.normal(0, 0.5, n_samples)
        ).astype(int),
        0, 3,
    )

    departments = rng.choice(DEPARTMENTS, n_samples)
    job_roles   = [rng.choice(JOB_ROLES[dept]) for dept in departments]

    # Attrition: structured causal formula targeting ~16% rate
    income_z         = (monthly_income - monthly_income.mean()) / monthly_income.std()
    income_dissatisf = np.clip(-income_z * 0.08, 0, 0.20)

    attrition_score = (
        0.22 * (4 - job_satisfaction) / 3
        + 0.12 * (4 - environment_satisfaction) / 3
        + 0.10 * (4 - job_involvement) / 3
        + 0.10 * (4 - performance_rating) / 3
        + 0.18 * overtime_flag
        + 0.08 * travel_flag
        + 0.05 * distance_flag
        + 0.08 * new_hire_flag
        + 0.07 * income_dissatisf
        + rng.uniform(0, 0.12, n_samples)
    )

    threshold = np.percentile(attrition_score, 84)
    attrition = np.where(attrition_score >= threshold, "Yes", "No")

    return pd.DataFrame({
        "employee_id":              employee_ids,
        "name":                     names,
        "age":                      ages,
        "gender":                   genders,
        "department":               departments,
        "job_role":                 job_roles,
        "job_level":                job_levels,
        "performance_rating":       performance_rating,
        "job_satisfaction":         job_satisfaction,
        "job_involvement":          job_involvement,
        "environment_satisfaction": environment_satisfaction,
        "monthly_income":           monthly_income,
        "percent_salary_hike":      percent_salary_hike,
        "stock_option_level":       stock_option_level,
        "years_at_company":         years_at_company,
        "years_in_current_role":    years_in_current_role,
        "total_working_years":      total_working_years,
        "distance_from_home":       distance_from_home,
        "business_travel":          business_travel,
        "over_time":                over_time,
        "attrition":                attrition,
    })


def validate_company_data(df: pd.DataFrame) -> None:
    """Run internal consistency checks on the generated company dataset."""
    violations = []

    # 1. Quick ratio must never exceed current ratio
    bad = (df["quick_ratio"] > df["current_ratio"] + 0.01).sum()
    if bad > 0:
        violations.append(f"  [X] quick_ratio > current_ratio: {bad} rows")
    else:
        print("  [OK] quick_ratio <= current_ratio  (always)")

    # 2. DuPont check: ROA ≈ NPM × (sales/TA)
    dupont_roa = df["net_profit_margin"] * df["sales_to_total_assets"]
    diff = (df["return_on_assets"] - dupont_roa).abs()
    bad2 = (diff > 0.05).sum()
    if bad2 > 0:
        violations.append(f"  [X] DuPont ROA deviation >0.05: {bad2} rows")
    else:
        print(f"  [OK] DuPont identity holds  (max deviation: {diff.max():.4f})")

    # 3. Bankrupt companies should have lower Altman Z on average
    z_h = df.loc[df["is_bankrupt"] == 0, "altman_z_score"].mean()
    z_b = df.loc[df["is_bankrupt"] == 1, "altman_z_score"].mean()
    if z_h > z_b:
        print(f"  [OK] Z-score: healthy={z_h:.2f}  bankrupt={z_b:.2f}  (correct direction)")
    else:
        violations.append(
            f"  [X] Z-score: healthy={z_h:.2f} <= bankrupt={z_b:.2f}  (wrong direction)"
        )

    # 4. Distressed firms should have higher D/E on average
    dte_h = df.loc[df["is_bankrupt"] == 0, "debt_to_equity"].median()
    dte_b = df.loc[df["is_bankrupt"] == 1, "debt_to_equity"].median()
    if dte_b > dte_h:
        print(f"  [OK] Debt/Equity: healthy median={dte_h:.2f}  bankrupt median={dte_b:.2f}")
    else:
        violations.append(
            f"  [X] D/E not higher for bankrupt (h={dte_h:.2f}, b={dte_b:.2f})"
        )

    if violations:
        print("\nVALIDATION FAILURES:")
        for v in violations:
            print(v)


def validate_employee_data(df: pd.DataFrame) -> None:
    """Run internal consistency checks on the generated employee dataset."""

    # 1. Temporal chain
    chain_ok = (
        (df["years_in_current_role"] <= df["years_at_company"]).all()
        and (df["years_at_company"] <= df["total_working_years"]).all()
        and (df["total_working_years"] <= (df["age"] - 22) + 1).all()
    )
    if chain_ok:
        print("  [OK] Temporal chain: years_in_role <= years_at_company <= total_years <= (age-22)")
    else:
        bad_r = (df["years_in_current_role"] > df["years_at_company"]).sum()
        bad_c = (df["years_at_company"] > df["total_working_years"]).sum()
        bad_a = (df["total_working_years"] > (df["age"] - 22) + 1).sum()
        print(f"  [X] Chain violations - role>company: {bad_r}, company>total: {bad_c}, total>age: {bad_a}")

    # 2. Income vs job level correlation (should be strong)
    corr = df["monthly_income"].corr(df["job_level"].astype(float))
    if corr > 0.5:
        print(f"  [OK] Income-JobLevel correlation = {corr:.3f}  (strong, expected)")
    else:
        print(f"  [!]  Income-JobLevel correlation = {corr:.3f}  (weaker than expected)")

    # 3. Performance vs satisfaction correlation (should be moderate)
    corr2 = df["performance_rating"].corr(df["job_satisfaction"].astype(float))
    if corr2 > 0.2:
        print(f"  [OK] Performance-Satisfaction correlation = {corr2:.3f}")
    else:
        print(f"  [!]  Performance-Satisfaction correlation = {corr2:.3f}  (low)")

    # 4. Attrition gradient — low satisfaction should mean higher attrition
    att_low  = (df.loc[df["job_satisfaction"] <= 2, "attrition"] == "Yes").mean()
    att_high = (df.loc[df["job_satisfaction"] >= 3, "attrition"] == "Yes").mean()
    if att_low > att_high:
        print(f"  [OK] Attrition: low-sat={att_low:.1%}  high-sat={att_high:.1%}  (correct direction)")
    else:
        print(f"  [X] Attrition not higher for low satisfaction")


def generate_company_trajectories(
    n_companies: int = 200,
    n_years: int = 3,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate multi-year financial trajectories for each company.

    Each company appears n_years times (year_offset = -(n_years-1) to 0,
    where 0 is the most recent observation). Bankrupt companies show a
    deteriorating trend in their ratios leading up to failure — a pattern
    XGBoost can use as a temporal signal.

    Column schema is identical to generate_company_data() plus:
      year_offset : 0 = most recent, -1 = one year prior, -2 = two years prior

    Args:
        n_companies : Number of unique companies
        n_years     : Number of annual snapshots per company (default 3)
        seed        : Random seed for reproducibility
    """
    rng = np.random.default_rng(seed)
    all_frames = []
    base_df = generate_company_data(n_samples=n_companies, seed=seed)

    for yr in range(-(n_years - 1), 1):   # e.g. -2, -1, 0
        year_df = base_df.copy()
        year_df.insert(1, "year_offset", yr)

        if yr < 0:
            # Scale bankrupt companies back toward healthier values in
            # earlier years — the closer to 0, the worse the ratios
            recovery = abs(yr) / (n_years - 1)

            bankrupt_mask = year_df["is_bankrupt"] == 1
            for col, nudge in [
                ("current_ratio",                     +recovery * 0.6),
                ("quick_ratio",                       +recovery * 0.4),
                ("debt_to_equity",                    -recovery * 0.5),
                ("interest_coverage",                 +recovery * 1.2),
                ("net_profit_margin",                 +recovery * 0.05),
                ("return_on_assets",                  +recovery * 0.04),
                ("ebit_to_total_assets",              +recovery * 0.04),
                ("working_capital_to_total_assets",   +recovery * 0.08),
                ("retained_earnings_to_total_assets", +recovery * 0.06),
            ]:
                if col in year_df.columns:
                    noise = rng.normal(0, 0.01, bankrupt_mask.sum())
                    year_df.loc[bankrupt_mask, col] = (
                        year_df.loc[bankrupt_mask, col] + nudge + noise
                    )

            # Healthy companies get a slight random walk year-to-year
            healthy_mask = ~bankrupt_mask
            for col in ["current_ratio", "net_profit_margin", "return_on_assets"]:
                if col in year_df.columns:
                    walk = rng.normal(0, 0.02, healthy_mask.sum())
                    year_df.loc[healthy_mask, col] = (
                        year_df.loc[healthy_mask, col] + walk
                    )

        all_frames.append(year_df)

    return (
        pd.concat(all_frames, ignore_index=True)
        .sort_values(["company_id", "year_offset"])
        .reset_index(drop=True)
    )


def main():
    output_dir = Path(__file__).parent

    # ── Company Data ──────────────────────────────────────────────────────
    print("=" * 65)
    print("GENERATING COMPANY FINANCIAL DATA  (n=1000)")
    print("=" * 65)
    company_data = generate_company_data(n_samples=1000, seed=42)
    company_data.to_csv(output_dir / "company_data.csv",  index=False)
    company_data.to_csv(output_dir / "company_train.csv", index=False)

    bkr_rate = company_data["is_bankrupt"].mean()
    z_safe   = company_data.loc[company_data["altman_z_score"] > 2.99, "is_bankrupt"].mean()
    z_dist   = company_data.loc[company_data["altman_z_score"] < 1.81, "is_bankrupt"].mean()

    print(f"  Total companies    : {len(company_data)}")
    print(f"  Bankruptcy rate    : {bkr_rate:.1%}")
    print(f"  Z>2.99 (safe zone) -> {1 - z_safe:.0%} actually healthy  [OK]")
    print(f"  Z<1.81 (distress)  -> {z_dist:.0%} actually bankrupt  [OK]")

    print("\n  INTERNAL CONSISTENCY CHECKS:")
    validate_company_data(company_data)

    print("\n  Sample BANKRUPT company:")
    b = company_data[company_data["is_bankrupt"] == 1].iloc[0]
    print(f"    Industry      : {b['industry']}")
    print(f"    Current Ratio : {b['current_ratio']:.2f}   Quick: {b['quick_ratio']:.2f}")
    print(f"    Debt/Equity   : {b['debt_to_equity']:.2f}")
    print(f"    Net Margin    : {b['net_profit_margin']:.2%}")
    print(f"    ROA           : {b['return_on_assets']:.2%}")
    print(f"    ROE           : {b['return_on_equity']:.2%}")
    print(f"    Altman Z      : {b['altman_z_score']:.2f}")

    print("\n  Sample HEALTHY company:")
    h = company_data[company_data["is_bankrupt"] == 0].iloc[0]
    print(f"    Industry      : {h['industry']}")
    print(f"    Current Ratio : {h['current_ratio']:.2f}   Quick: {h['quick_ratio']:.2f}")
    print(f"    Debt/Equity   : {h['debt_to_equity']:.2f}")
    print(f"    Net Margin    : {h['net_profit_margin']:.2%}")
    print(f"    ROA           : {h['return_on_assets']:.2%}")
    print(f"    ROE           : {h['return_on_equity']:.2%}")
    print(f"    Altman Z      : {h['altman_z_score']:.2f}")

    print("\n  Generating 3-year trajectories (200 companies)...")
    traj = generate_company_trajectories(n_companies=200, n_years=3, seed=42)
    traj.to_csv(output_dir / "company_trajectories.csv", index=False)
    print(f"  Saved {len(traj):,} trajectory rows to company_trajectories.csv")

    print(f"\n  Saved: company_data.csv + company_train.csv")

    # ── Employee Data ──────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("GENERATING EMPLOYEE DATA  (n=5000)")
    print("=" * 65)
    employee_data = generate_employee_data(n_samples=5000, seed=42)
    employee_data.to_csv(output_dir / "employee_data.csv",  index=False)
    employee_data.to_csv(output_dir / "employee_train.csv", index=False)

    att_rate = (employee_data["attrition"] == "Yes").mean()
    print(f"  Total employees    : {len(employee_data)}")
    print(f"  Attrition rate     : {att_rate:.1%}")

    print("\n  INTERNAL CONSISTENCY CHECKS:")
    validate_employee_data(employee_data)

    print("\n  Attrition by job satisfaction (causal gradient):")
    for lv in [1, 2, 3, 4]:
        sub  = employee_data[employee_data["job_satisfaction"] == lv]
        rate = (sub["attrition"] == "Yes").mean() if len(sub) > 0 else 0
        bar  = "#" * int(rate * 40)
        print(f"    Satisfaction {lv}: {rate:5.1%}  {bar}  (n={len(sub)})")

    print("\n  Income by job level (structural dependency):")
    for lv in range(1, 6):
        sub = employee_data[employee_data["job_level"] == lv]
        if len(sub) > 0:
            print(f"    Level {lv}: ${sub['monthly_income'].mean():,.0f} avg  (n={len(sub)})")

    print(f"\n  Saved: employee_data.csv + employee_train.csv")

    print("\n" + "=" * 65)
    print("DATA GENERATION COMPLETE")
    print("=" * 65)
    print("\n  Files written to data/:")
    print("    company_data.csv          <- backend/app/main.py, demo.py")
    print("    company_train.csv         <- scripts/train_models.py")
    print("    company_trajectories.csv  <- 3-year trend data (optional)")
    print("    employee_data.csv         <- backend/app/main.py, demo.py")
    print("    employee_train.csv        <- scripts/train_models.py")


if __name__ == "__main__":
    main()
