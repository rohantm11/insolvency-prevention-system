"""
Generate comprehensive PDF documentation for SolvencyInsight project.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, ListFlowable, ListItem
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus.tableofcontents import TableOfContents

# Create document
doc = SimpleDocTemplate(
    'SolvencyInsight_Complete_Documentation.pdf',
    pagesize=letter,
    leftMargin=0.75*inch,
    rightMargin=0.75*inch,
    topMargin=0.75*inch,
    bottomMargin=0.75*inch
)

# Styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=28, spaceAfter=20, alignment=TA_CENTER, textColor=colors.HexColor('#1a365d'))
h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=18, spaceAfter=12, spaceBefore=24, textColor=colors.HexColor('#1e3a5f'), borderPadding=5)
h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=14, spaceAfter=10, spaceBefore=16, textColor=colors.HexColor('#2c5282'))
h3 = ParagraphStyle('H3', parent=styles['Heading3'], fontSize=12, spaceAfter=8, spaceBefore=12, textColor=colors.HexColor('#3182ce'))
body = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, spaceAfter=8, alignment=TA_JUSTIFY, leading=14)
code_style = ParagraphStyle('Code', parent=styles['Code'], fontSize=8, backColor=colors.HexColor('#f7fafc'), leftIndent=15, rightIndent=15, spaceBefore=6, spaceAfter=6)
bullet = ParagraphStyle('Bullet', parent=body, leftIndent=20, bulletIndent=10)
caption = ParagraphStyle('Caption', parent=styles['Normal'], fontSize=9, textColor=colors.grey, alignment=TA_CENTER, spaceAfter=12)

story = []

# ============================================================================
# TITLE PAGE
# ============================================================================
story.append(Spacer(1, 2*inch))
story.append(Paragraph('SolvencyInsight', title_style))
story.append(Paragraph('AI-Powered Financial Distress Prediction System', ParagraphStyle('Sub', parent=styles['Heading2'], alignment=TA_CENTER, textColor=colors.HexColor('#4a5568'))))
story.append(Spacer(1, 0.5*inch))
story.append(Paragraph('Complete Technical Documentation', ParagraphStyle('Sub2', parent=styles['Heading3'], alignment=TA_CENTER, textColor=colors.grey)))
story.append(Spacer(1, 1.5*inch))

# Team table
team_data = [
    ['Team Member', 'Primary Responsibility'],
    ['Rohan', 'Machine Learning Module & Backend Architecture'],
    ['Jonathan', 'Machine Learning Module & Backend Development'],
    ['Neha', 'Data Preparation & Frontend Development'],
    ['Mariya', 'Frontend Development & UI/UX'],
]
team_table = Table(team_data, colWidths=[2*inch, 4*inch])
team_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
    ('TOPPADDING', (0, 0), (-1, -1), 8),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
]))
story.append(team_table)
story.append(PageBreak())

# ============================================================================
# TABLE OF CONTENTS
# ============================================================================
story.append(Paragraph('Table of Contents', h1))
toc_items = [
    '1. Executive Summary',
    '2. Project Architecture',
    '3. Data Layer',
    '4. Machine Learning Module',
    '5. Backend API',
    '6. Frontend Application',
    '7. Model Comparison Analysis',
    '8. Feature Engineering Deep Dive',
    '9. Team Contributions',
]
for item in toc_items:
    story.append(Paragraph(item, body))
story.append(PageBreak())

# ============================================================================
# 1. EXECUTIVE SUMMARY
# ============================================================================
story.append(Paragraph('1. Executive Summary', h1))

story.append(Paragraph('1.1 What is SolvencyInsight?', h2))
story.append(Paragraph('SolvencyInsight is an enterprise-grade financial distress prediction platform that combines <b>traditional financial analysis</b> (Altman Z-Score) with <b>modern machine learning</b> (XGBoost with SHAP explainability) to predict corporate bankruptcy risk with <b>97.97% ROC-AUC accuracy</b>.', body))

story.append(Paragraph('1.2 Problem Statement', h2))
story.append(Paragraph('Corporate bankruptcy can devastate stakeholders - employees lose jobs, investors lose capital, and suppliers lose revenue. Early detection of financial distress allows investors to divest, creditors to adjust terms, management to take corrective action, and regulators to intervene proactively.', body))

story.append(Paragraph('1.3 Key Capabilities', h2))
capabilities = [
    ['Feature', 'Description'],
    ['Single Company Analysis', 'Upload CSV or enter data manually for instant risk assessment'],
    ['Bulk Analysis', 'Process hundreds of companies simultaneously'],
    ['SHAP Explanations', 'Understand WHY a company is flagged as high-risk'],
    ['Altman Z-Score', 'Classic bankruptcy predictor with zone classification'],
    ['PDF Reports', 'Generate professional reports for stakeholders'],
]
cap_table = Table(capabilities, colWidths=[2*inch, 4.5*inch])
cap_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
]))
story.append(cap_table)

story.append(Paragraph('1.4 Technology Stack', h2))
tech_stack = [
    ['Layer', 'Technologies'],
    ['Frontend', 'React 18, TypeScript, TailwindCSS, Recharts, Vite'],
    ['Backend', 'FastAPI, Pydantic, Uvicorn, Python 3.11+'],
    ['Machine Learning', 'XGBoost, SHAP, Scikit-learn, Pandas, NumPy'],
    ['Data', '10,000 Company Dataset, 30 Industries, 5 Company Sizes'],
]
tech_table = Table(tech_stack, colWidths=[1.5*inch, 5*inch])
tech_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
]))
story.append(tech_table)
story.append(PageBreak())

# ============================================================================
# 2. PROJECT ARCHITECTURE
# ============================================================================
story.append(Paragraph('2. Project Architecture', h1))

story.append(Paragraph('2.1 Directory Structure', h2))
dir_structure = """insolvency-prevention-system/
|-- backend/                    # FastAPI Backend
|   |-- app/
|   |   |-- main.py            # API endpoints
|   |   |-- models/schemas.py  # Pydantic models
|   |   |-- services/          # Business logic
|-- frontend/                   # React Frontend
|   |-- src/
|   |   |-- components/        # UI components
|   |   |-- pages/             # Page components
|   |   |-- services/api.ts    # API client
|-- ml_models/                  # ML Module
|   |-- insolvency_predictor_v2.py  # Enhanced model
|   |-- saved_models/          # Trained models
|-- data/training_companies_10k/  # Dataset"""
story.append(Paragraph(dir_structure.replace('\n', '<br/>'), code_style))

story.append(Paragraph('2.2 Data Flow', h2))
story.append(Paragraph('<b>User uploads CSV</b> --> <b>FileUpload component</b> --> <b>api.ts (Axios)</b> --> <b>FastAPI endpoint</b> --> <b>Pandas reads CSV</b> --> <b>Feature Engineering (12 to 41 features)</b> --> <b>XGBoost prediction</b> --> <b>SHAP explanation</b> --> <b>JSON response</b> --> <b>React renders results</b>', body))

story.append(Paragraph('2.3 Key Integration Points', h2))
story.append(Paragraph('<b>Vite Proxy:</b> Frontend dev server (port 5173) proxies /api requests to backend (port 8001), enabling seamless development without CORS issues.', body))
story.append(Paragraph('<b>FormData Upload:</b> CSV files sent as multipart/form-data, parsed by FastAPI using python-multipart.', body))
story.append(Paragraph('<b>Model Loading:</b> On backend startup, the trained XGBoost model is loaded from pickle file into memory for fast inference.', body))
story.append(PageBreak())

# ============================================================================
# 3. DATA LAYER
# ============================================================================
story.append(Paragraph('3. Data Layer', h1))

story.append(Paragraph('3.1 Dataset Overview', h2))
dataset_stats = [
    ['Metric', 'Value'],
    ['Total Companies', '10,000'],
    ['Healthy Companies', '5,302 (53.0%)'],
    ['Distressed Companies', '4,698 (47.0%)'],
    ['Industries', '30'],
    ['Company Sizes', '5 categories (micro, small, medium, large, enterprise)'],
    ['Economic Cycles', '4 phases (expansion, peak, contraction, trough)'],
]
ds_table = Table(dataset_stats, colWidths=[2.5*inch, 4*inch])
ds_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
]))
story.append(ds_table)

story.append(Paragraph('3.2 Input Features (12 Base Ratios)', h2))
story.append(Paragraph('<b>Altman Z-Score Components (5 ratios):</b>', h3))
zscore_features = [
    ['Feature', 'Formula', 'Weight'],
    ['working_capital_to_total_assets', '(CA - CL) / TA', '1.2'],
    ['retained_earnings_to_total_assets', 'RE / TA', '1.4'],
    ['ebit_to_total_assets', 'EBIT / TA', '3.3'],
    ['market_value_equity_to_total_liabilities', 'MVE / TL', '0.6'],
    ['sales_to_total_assets', 'Sales / TA', '1.0'],
]
zf_table = Table(zscore_features, colWidths=[3*inch, 2*inch, 1*inch])
zf_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3182ce')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))
story.append(zf_table)

story.append(Paragraph('<b>Additional Financial Ratios (7 ratios):</b>', h3))
add_features = [
    ['Feature', 'Healthy Range', 'Distressed Range'],
    ['current_ratio', '> 1.5', '< 1.0'],
    ['quick_ratio', '> 1.0', '< 0.5'],
    ['debt_to_equity', '< 1.0', '> 2.5'],
    ['interest_coverage', '> 3.0', '< 1.5'],
    ['net_profit_margin', '> 5%', '< 0%'],
    ['return_on_assets', '> 5%', '< 0%'],
    ['return_on_equity', '> 10%', '< 0%'],
]
af_table = Table(add_features, colWidths=[2.5*inch, 2*inch, 2*inch])
af_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3182ce')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))
story.append(af_table)
story.append(PageBreak())

# ============================================================================
# 4. MACHINE LEARNING MODULE
# ============================================================================
story.append(Paragraph('4. Machine Learning Module', h1))

story.append(Paragraph('4.1 Model Selection: Why XGBoost?', h2))
model_comparison = [
    ['Criterion', 'XGBoost V2', 'Random Forest', 'Logistic Regression'],
    ['ROC-AUC', '97.97%', '97.60%', '97.30%'],
    ['Non-linearity', 'Excellent', 'Good', 'Limited'],
    ['Feature Interactions', 'Automatic', 'Automatic', 'Manual only'],
    ['Regularization', 'L1 + L2 + gamma', 'Tree constraints', 'L2 only'],
    ['SHAP Support', 'Native', 'Supported', 'Coefficients'],
]
mc_table = Table(model_comparison, colWidths=[1.8*inch, 1.5*inch, 1.5*inch, 1.7*inch])
mc_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('BACKGROUND', (1, 1), (1, -1), colors.HexColor('#e6fffa')),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))
story.append(mc_table)

story.append(Paragraph('4.2 XGBoost Hyperparameters', h2))
hyperparams = [
    ['Parameter', 'Value', 'Purpose'],
    ['n_estimators', '200', 'Number of boosting rounds'],
    ['max_depth', '6', 'Tree depth (captures interactions)'],
    ['learning_rate', '0.05', 'Step size shrinkage'],
    ['reg_alpha', '0.5', 'L1 regularization (Lasso)'],
    ['reg_lambda', '2.0', 'L2 regularization (Ridge)'],
    ['subsample', '0.8', 'Row sampling per tree'],
    ['colsample_bytree', '0.8', 'Feature sampling per tree'],
    ['min_child_weight', '5', 'Min samples per leaf'],
    ['gamma', '0.1', 'Min loss reduction for split'],
    ['early_stopping_rounds', '20', 'Stop if no improvement'],
]
hp_table = Table(hyperparams, colWidths=[2*inch, 1*inch, 3.5*inch])
hp_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))
story.append(hp_table)

story.append(Paragraph('4.3 Training Pipeline', h2))
story.append(Paragraph('1. <b>Extract 12 base features</b> from input DataFrame', bullet))
story.append(Paragraph('2. <b>Engineer 41 total features</b> (see Section 8)', bullet))
story.append(Paragraph('3. <b>Train-test split</b> (80/20, stratified by class)', bullet))
story.append(Paragraph('4. <b>Train XGBoost</b> with early stopping on validation set', bullet))
story.append(Paragraph('5. <b>Create SHAP TreeExplainer</b> for interpretability', bullet))
story.append(Paragraph('6. <b>Calculate metrics</b> (accuracy, precision, recall, F1, ROC-AUC)', bullet))
story.append(Paragraph('7. <b>5-fold cross-validation</b> for robust performance estimate', bullet))
story.append(Paragraph('8. <b>Save model</b> to pickle file', bullet))

story.append(Paragraph('4.4 SHAP Explainability', h2))
story.append(Paragraph('SHAP (SHapley Additive exPlanations) values measure each features contribution to the prediction:', body))
story.append(Paragraph('<b>Prediction = Base Value + SHAP(feature_1) + SHAP(feature_2) + ... + SHAP(feature_n)</b>', code_style))
story.append(Paragraph('<b>Positive SHAP:</b> Feature INCREASES bankruptcy risk (e.g., high debt)', bullet))
story.append(Paragraph('<b>Negative SHAP:</b> Feature DECREASES bankruptcy risk (e.g., high current ratio)', bullet))
story.append(Paragraph('<b>Near Zero:</b> Feature has minimal impact on this prediction', bullet))

story.append(Paragraph('4.5 Altman Z-Score', h2))
story.append(Paragraph('<b>Formula:</b> Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5', body))
zone_classification = [
    ['Zone', 'Z-Score Range', 'Interpretation'],
    ['Safe', 'Z > 2.99', 'Low bankruptcy probability'],
    ['Grey', '1.81 <= Z <= 2.99', 'Uncertain, monitoring needed'],
    ['Distress', 'Z < 1.81', 'High bankruptcy probability'],
]
zone_table = Table(zone_classification, colWidths=[1.5*inch, 2*inch, 3*inch])
zone_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#c6f6d5')),
    ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#fefcbf')),
    ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#fed7d7')),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
]))
story.append(zone_table)
story.append(PageBreak())

# ============================================================================
# 5. MODEL COMPARISON ANALYSIS
# ============================================================================
story.append(Paragraph('5. Model Comparison Analysis', h1))

story.append(Paragraph('5.1 Performance Results', h2))
perf_results = [
    ['Model', 'Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC'],
    ['XGBoost V2', '91.15%', '93.01%', '87.77%', '90.31%', '97.97%'],
    ['Random Forest', '90.55%', '93.51%', '85.85%', '89.52%', '97.60%'],
    ['Logistic Regression', '90.15%', '91.42%', '87.23%', '89.28%', '97.30%'],
]
perf_table = Table(perf_results, colWidths=[1.8*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch])
perf_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#e6fffa')),
    ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
]))
story.append(perf_table)

story.append(Paragraph('5.2 Cross-Validation Results (5-Fold)', h2))
cv_results = [
    ['Model', 'CV Mean', 'CV Std', '95% Confidence Interval'],
    ['XGBoost V2', '98.14%', '0.17%', '[97.80%, 98.48%]'],
    ['Random Forest', '97.61%', '0.28%', '[97.06%, 98.17%]'],
    ['Logistic Regression', '97.32%', '0.27%', '[96.79%, 97.85%]'],
]
cv_table = Table(cv_results, colWidths=[2*inch, 1.2*inch, 1.2*inch, 2.2*inch])
cv_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#e6fffa')),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
]))
story.append(cv_table)

story.append(Paragraph('5.3 Why XGBoost V2 is Best', h2))
story.append(Paragraph('<b>1. Highest ROC-AUC (97.97%):</b> Best ability to distinguish healthy vs distressed companies across all thresholds.', bullet))
story.append(Paragraph('<b>2. Feature Engineering:</b> 41 engineered features capture complex relationships (composite scores, interactions, zone indicators).', bullet))
story.append(Paragraph('<b>3. Gradient Boosting:</b> Sequential error correction outperforms Random Forests bagging approach.', bullet))
story.append(Paragraph('<b>4. Built-in Regularization:</b> L1 + L2 + gamma prevents overfitting on financial data with spurious correlations.', bullet))
story.append(Paragraph('<b>5. Non-linear Patterns:</b> Captures thresholds (e.g., debt_to_equity > 3.0 = danger zone) that Logistic Regression misses.', bullet))
story.append(Paragraph('<b>6. SHAP Integration:</b> TreeExplainer provides fast, accurate, auditable explanations for each prediction.', bullet))

story.append(Paragraph('5.4 Confusion Matrix Analysis (XGBoost V2)', h2))
cm_analysis = [
    ['Metric', 'Value', 'Interpretation'],
    ['True Negatives', '998', 'Healthy companies correctly identified'],
    ['True Positives', '825', 'Distressed companies correctly identified'],
    ['False Positives', '62', 'Healthy companies incorrectly flagged (Type I)'],
    ['False Negatives', '115', 'Distressed companies missed (Type II)'],
    ['Specificity', '94.15%', 'True Negative Rate'],
    ['Sensitivity', '87.77%', 'True Positive Rate (Recall)'],
]
cm_table = Table(cm_analysis, colWidths=[1.5*inch, 1*inch, 4*inch])
cm_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
]))
story.append(cm_table)
story.append(PageBreak())

# ============================================================================
# 6. FEATURE ENGINEERING
# ============================================================================
story.append(Paragraph('6. Feature Engineering Deep Dive', h1))

story.append(Paragraph('Feature engineering transforms <b>12 base features</b> into <b>41 total features</b> by creating derived metrics, indicators, and interaction terms.', body))

story.append(Paragraph('6.1 Feature Categories', h2))
feature_cats = [
    ['Category', 'Features', 'Purpose'],
    ['Z-Score', 'altman_z_score, z_score_safe, z_score_grey, z_score_distress', 'Classic bankruptcy indicator'],
    ['Liquidity', 'liquidity_gap, severe_liquidity_stress, moderate_liquidity_stress', 'Short-term solvency'],
    ['Leverage', 'high_leverage, extreme_leverage, leverage_coverage_ratio', 'Debt risk indicators'],
    ['Profitability', 'negative_profit, negative_roa, negative_roe, profitability_score', 'Profit health'],
    ['Working Capital', 'negative_working_capital, working_capital_trend', 'WC health signals'],
    ['Efficiency', 'asset_utilization, capital_efficiency', 'Asset productivity'],
    ['Coverage', 'interest_coverage_safe, interest_coverage_danger', 'Debt service ability'],
    ['Interactions', 'leverage_liquidity_interaction, profit_leverage_interaction, z_score_leverage_interaction', 'Combined effects'],
    ['Composite', 'financial_distress_score, financial_health_score', 'Aggregated signals'],
]
fc_table = Table(feature_cats, colWidths=[1.2*inch, 3.3*inch, 2*inch])
fc_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
]))
story.append(fc_table)

story.append(Paragraph('6.2 Top 10 Most Important Features', h2))
top_features = [
    ['Rank', 'Feature', 'Importance', 'Description'],
    ['1', 'financial_distress_score', '40.29%', 'Sum of 5 warning flags'],
    ['2', 'profitability_score', '13.79%', 'Average of profit margins'],
    ['3', 'z_score_leverage_interaction', '5.89%', 'Z-Score adjusted for debt'],
    ['4', 'z_score_grey', '4.55%', 'In grey zone indicator'],
    ['5', 'negative_retained_earnings', '2.65%', 'Accumulated losses flag'],
    ['6', 'financial_health_score', '2.55%', 'Sum of 5 health indicators'],
    ['7', 'retained_earnings_to_total_assets', '2.40%', 'Original Altman component'],
    ['8', 'interest_coverage_safe', '2.12%', 'Coverage > 3x indicator'],
    ['9', 'altman_z_score', '1.81%', 'Continuous Z-Score'],
    ['10', 'interest_coverage_danger', '1.54%', 'Coverage < 1.5x indicator'],
]
tf_table = Table(top_features, colWidths=[0.5*inch, 2.5*inch, 1*inch, 2.5*inch])
tf_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
    ('ALIGN', (2, 0), (2, -1), 'CENTER'),
]))
story.append(tf_table)

story.append(Paragraph('6.3 Key Engineered Features Explained', h2))
story.append(Paragraph('<b>financial_distress_score</b> (Most Important - 40.29%)', h3))
story.append(Paragraph('Combines 5 binary warning flags into a single 0-5 score:', body))
code_fds = """financial_distress_score = (
    negative_working_capital +      # WC/TA < 0
    severe_liquidity_stress +       # Current Ratio < 1.0
    high_leverage +                 # D/E > 2.0
    negative_profit +               # Net Margin < 0
    interest_coverage_danger        # Coverage < 1.5x
)"""
story.append(Paragraph(code_fds.replace('\n', '<br/>'), code_style))
story.append(Paragraph('Score 0 = No red flags (healthy), Score 5 = Severe distress', body))

story.append(Paragraph('<b>profitability_score</b> (Second Most Important - 13.79%)', h3))
story.append(Paragraph('Average of three profitability metrics:', body))
code_ps = """profitability_score = (net_profit_margin + return_on_assets + return_on_equity) / 3"""
story.append(Paragraph(code_ps, code_style))

story.append(Paragraph('<b>z_score_leverage_interaction</b> (Third Most Important - 5.89%)', h3))
story.append(Paragraph('Adjusts Z-Score for leverage level:', body))
code_zli = """z_score_leverage_interaction = altman_z_score / (debt_to_equity + 0.5)"""
story.append(Paragraph(code_zli, code_style))
story.append(Paragraph('A company with high Z-Score but also high debt is riskier than Z-Score alone suggests.', body))
story.append(PageBreak())

# ============================================================================
# 7. TEAM CONTRIBUTIONS
# ============================================================================
story.append(Paragraph('7. Team Contributions', h1))

story.append(Paragraph('7.1 Rohan & Jonathan: ML Module & Backend', h2))
story.append(Paragraph('<b>Responsibilities:</b>', h3))
story.append(Paragraph('XGBoost model architecture and hyperparameter tuning', bullet))
story.append(Paragraph('Feature engineering (12 to 41 features)', bullet))
story.append(Paragraph('SHAP explainability integration', bullet))
story.append(Paragraph('Altman Z-Score calculation and zone classification', bullet))
story.append(Paragraph('FastAPI backend development', bullet))
story.append(Paragraph('Pydantic schema validation', bullet))
story.append(Paragraph('Model training, evaluation, and comparison', bullet))
story.append(Paragraph('<b>Key Files:</b> insolvency_predictor_v2.py, main.py, schemas.py, train_model_v2.py, model_comparison_v2.py', body))

story.append(Paragraph('7.2 Neha: Data Preparation & Frontend', h2))
story.append(Paragraph('<b>Responsibilities:</b>', h3))
story.append(Paragraph('Dataset generation (10,000 companies across 30 industries)', bullet))
story.append(Paragraph('Industry-specific financial characteristics', bullet))
story.append(Paragraph('Economic cycle simulation', bullet))
story.append(Paragraph('CSV parsing and validation', bullet))
story.append(Paragraph('API service layer (api.ts with Axios)', bullet))
story.append(Paragraph('FileUpload component (drag-and-drop)', bullet))
story.append(Paragraph('DataTable component (sortable, searchable)', bullet))
story.append(Paragraph('<b>Key Files:</b> generate_large_dataset.py, api.ts, FileUpload.tsx, DataTable.tsx', body))

story.append(Paragraph('7.3 Mariya: Frontend Development & UI/UX', h2))
story.append(Paragraph('<b>Responsibilities:</b>', h3))
story.append(Paragraph('React page components', bullet))
story.append(Paragraph('InsolvencyAnalysis page (main analysis interface)', bullet))
story.append(Paragraph('SHAP visualization using Recharts', bullet))
story.append(Paragraph('RiskGauge component (circular probability display)', bullet))
story.append(Paragraph('TailwindCSS styling and dark theme', bullet))
story.append(Paragraph('Responsive design for all screen sizes', bullet))
story.append(Paragraph('Toast notification system', bullet))
story.append(Paragraph('<b>Key Files:</b> InsolvencyAnalysis.tsx, RiskGauge.tsx, ToastContext.tsx, tailwind.config.js', body))

story.append(Paragraph('7.4 All Team Members: Integration', h2))
story.append(Paragraph('Frontend-backend integration via Vite proxy', bullet))
story.append(Paragraph('End-to-end testing', bullet))
story.append(Paragraph('Error handling and user feedback', bullet))
story.append(Paragraph('Performance optimization', bullet))
story.append(Paragraph('Documentation', bullet))
story.append(PageBreak())

# ============================================================================
# 8. CONCLUSION
# ============================================================================
story.append(Paragraph('8. Conclusion', h1))

story.append(Paragraph('SolvencyInsight demonstrates the practical application of machine learning to financial risk assessment. The system combines:', body))

story.append(Paragraph('<b>Traditional Finance:</b> Altman Z-Score provides an interpretable, academically-validated baseline that financial professionals trust.', bullet))
story.append(Paragraph('<b>Modern ML:</b> XGBoost captures non-linear patterns in financial data that traditional methods miss, achieving 97.97% ROC-AUC.', bullet))
story.append(Paragraph('<b>Explainable AI:</b> SHAP values make predictions transparent and auditable, critical for regulatory compliance.', bullet))
story.append(Paragraph('<b>User-Friendly Interface:</b> React frontend makes complex analysis accessible to non-technical users.', bullet))

story.append(Spacer(1, 0.3*inch))

story.append(Paragraph('<b>Key Achievements:</b>', h3))
achievements = [
    ['Metric', 'Value'],
    ['Model Accuracy', '91.15%'],
    ['ROC-AUC Score', '97.97%'],
    ['Cross-Validation Mean', '98.14%'],
    ['Dataset Size', '10,000 companies'],
    ['Engineered Features', '41'],
    ['Industries Covered', '30'],
]
ach_table = Table(achievements, colWidths=[2.5*inch, 2*inch])
ach_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
]))
story.append(ach_table)

story.append(Spacer(1, 0.5*inch))
story.append(Paragraph('<b>RECOMMENDATION:</b> Deploy XGBoost V2 with feature engineering for production use. The models combination of high accuracy, robust cross-validation performance, built-in regularization, and SHAP explainability makes it ideal for financial distress prediction applications.', body))

# Build PDF
doc.build(story)
print('PDF created: SolvencyInsight_Complete_Documentation.pdf')
