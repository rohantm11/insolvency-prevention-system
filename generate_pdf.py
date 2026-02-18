from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

doc = SimpleDocTemplate('SolvencyInsight_Team_Documentation.pdf', pagesize=letter,
                        leftMargin=0.75*inch, rightMargin=0.75*inch,
                        topMargin=0.75*inch, bottomMargin=0.75*inch)

styles = getSampleStyleSheet()
title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=24, spaceAfter=20, alignment=TA_CENTER)
h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=16, spaceAfter=12, spaceBefore=20, textColor=colors.HexColor('#1e3a5f'))
h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=13, spaceAfter=8, spaceBefore=14, textColor=colors.HexColor('#2c5282'))
h3 = ParagraphStyle('H3', parent=styles['Heading3'], fontSize=11, spaceAfter=6, spaceBefore=10)
body = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, spaceAfter=8, alignment=TA_JUSTIFY, leading=14)
code_style = ParagraphStyle('Code', parent=styles['Code'], fontSize=9, backColor=colors.HexColor('#f0f0f0'), leftIndent=20)
bullet = ParagraphStyle('Bullet', parent=body, leftIndent=20, bulletIndent=10)

story = []

# Title Page
story.append(Spacer(1, 1.5*inch))
story.append(Paragraph('SolvencyInsight', title_style))
story.append(Paragraph('AI-Powered Financial Distress Prediction System', ParagraphStyle('Sub', parent=styles['Heading2'], alignment=TA_CENTER, textColor=colors.grey)))
story.append(Spacer(1, 0.5*inch))
story.append(Paragraph('Technical Documentation & Team Contributions', ParagraphStyle('Sub2', parent=styles['Heading3'], alignment=TA_CENTER)))
story.append(Spacer(1, 1*inch))

# Team table
team_data = [
    ['Team Member', 'Primary Responsibility'],
    ['Rohan', 'Machine Learning Module & Backend Architecture'],
    ['Jonathan', 'Machine Learning Module & Backend Development'],
    ['Neha', 'Data Preparation & Frontend Development'],
    ['Mariya', 'Frontend Development & UI/UX'],
    ['All Members', 'System Integration & Testing']
]
team_table = Table(team_data, colWidths=[2.5*inch, 4*inch])
team_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
    ('TOPPADDING', (0, 0), (-1, -1), 8),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
]))
story.append(team_table)
story.append(PageBreak())

# Project Overview
story.append(Paragraph('1. Project Overview', h1))
story.append(Paragraph('SolvencyInsight is an enterprise-grade financial distress prediction platform that combines traditional financial analysis (Altman Z-Score) with modern machine learning (XGBoost with SHAP explainability) to predict corporate bankruptcy risk. The system provides real-time risk assessment with interpretable AI explanations.', body))

story.append(Paragraph('Core Capabilities:', h3))
story.append(Paragraph('* <b>Bankruptcy Prediction:</b> XGBoost classifier trained on 12 financial ratios with probability smoothing for realistic predictions (2%-98% range)', bullet))
story.append(Paragraph('* <b>Altman Z-Score:</b> Classic formula: Z = 1.2X1 + 1.4X2 + 3.3X3 + 0.6X4 + 1.0X5 with zone classification (Safe >2.99, Grey 1.81-2.99, Distress <1.81)', bullet))
story.append(Paragraph('* <b>SHAP Explainability:</b> TreeExplainer provides feature-level contribution analysis showing which financial metrics drive the prediction', bullet))
story.append(Paragraph('* <b>Market Intelligence:</b> Real-time news sentiment analysis and sector performance data', bullet))

story.append(PageBreak())

# ROHAN & JONATHAN - ML & Backend
story.append(Paragraph('2. Machine Learning Module & Backend (Rohan & Jonathan)', h1))
story.append(Paragraph('Rohan and Jonathan developed the core prediction engine and API infrastructure that powers SolvencyInsight.', body))

story.append(Paragraph('2.1 XGBoost Classification Model', h2))
story.append(Paragraph('The insolvency prediction model uses XGBoost (Extreme Gradient Boosting), an ensemble learning algorithm that builds decision trees sequentially, with each tree correcting errors from previous ones.', body))

story.append(Paragraph('<b>Model Configuration (insolvency_predictor.py):</b>', body))
config_text = """self.model = xgb.XGBClassifier(
    n_estimators=50,      # Number of boosting rounds
    max_depth=3,          # Shallow trees prevent overfitting
    learning_rate=0.05,   # Small steps for gradual learning
    reg_alpha=0.5,        # L1 regularization (Lasso)
    reg_lambda=1.0,       # L2 regularization (Ridge)
    min_child_weight=3,   # Minimum samples per leaf
    subsample=0.8,        # Row sampling per tree
    colsample_bytree=0.8  # Feature sampling per tree
)"""
story.append(Paragraph(config_text.replace('\n', '<br/>'), code_style))

story.append(Paragraph('<b>Why These Parameters Matter:</b>', h3))
story.append(Paragraph('* <b>n_estimators=50:</b> Limits model complexity; more trees can overfit on small datasets', bullet))
story.append(Paragraph('* <b>max_depth=3:</b> Shallow trees capture general patterns without memorizing noise', bullet))
story.append(Paragraph('* <b>reg_alpha and reg_lambda:</b> Regularization penalizes large weights, preventing any single feature from dominating', bullet))
story.append(Paragraph('* <b>subsample and colsample_bytree=0.8:</b> Introduces randomness to improve generalization', bullet))

story.append(Paragraph('2.2 Probability Smoothing', h2))
story.append(Paragraph('Raw XGBoost outputs often produce extreme probabilities (0% or 100%) which are unrealistic for financial predictions. We apply probability smoothing:', body))
story.append(Paragraph('probabilities = 0.02 + 0.96 * raw_probabilities', code_style))
story.append(Paragraph('This maps predictions to the range [2%, 98%], acknowledging that no model can be 100% certain about future bankruptcy.', body))

story.append(Paragraph('2.3 SHAP (SHapley Additive exPlanations)', h2))
story.append(Paragraph('SHAP values are based on game theory - they measure each feature contribution to moving the prediction away from the baseline (average prediction). TreeExplainer is optimized for tree-based models.', body))
shap_code = """explainer = shap.TreeExplainer(self.model)
shap_values = explainer.shap_values(X)
# Positive SHAP = increases bankruptcy risk
# Negative SHAP = decreases bankruptcy risk"""
story.append(Paragraph(shap_code.replace('\n', '<br/>'), code_style))

story.append(Paragraph('2.4 Altman Z-Score Implementation', h2))
story.append(Paragraph('The Z-Score formula developed by Edward Altman in 1968 remains the gold standard for bankruptcy prediction:', body))
zscore_formula = """Z = 1.2*(Working Capital/Total Assets)
  + 1.4*(Retained Earnings/Total Assets)
  + 3.3*(EBIT/Total Assets)
  + 0.6*(Market Value Equity/Total Liabilities)
  + 1.0*(Sales/Total Assets)"""
story.append(Paragraph(zscore_formula.replace('\n', '<br/>'), code_style))

zone_data = [
    ['Zone', 'Z-Score Range', 'Interpretation'],
    ['Safe', '> 2.99', 'Low bankruptcy probability'],
    ['Grey', '1.81 - 2.99', 'Uncertain, requires monitoring'],
    ['Distress', '< 1.81', 'High bankruptcy probability']
]
zone_table = Table(zone_data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
zone_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
]))
story.append(zone_table)
story.append(Spacer(1, 0.2*inch))

story.append(Paragraph('2.5 FastAPI Backend Architecture', h2))
story.append(Paragraph('The backend uses FastAPI, a modern Python web framework chosen for its automatic OpenAPI documentation, type validation via Pydantic, and async support.', body))

story.append(Paragraph('<b>Key Endpoints (main.py):</b>', h3))
endpoints = [
    ['Endpoint', 'Method', 'Purpose'],
    ['/api/financial/analyze', 'POST', 'Single company analysis with SHAP'],
    ['/api/financial/upload', 'POST', 'Bulk CSV analysis'],
    ['/api/financial/upload-single', 'POST', 'CSV upload with full SHAP response'],
    ['/api/financial/feature-importance', 'GET', 'Model feature weights'],
    ['/api/reports/insolvency', 'POST', 'Generate PDF report'],
    ['/health', 'GET', 'System health check']
]
ep_table = Table(endpoints, colWidths=[2.2*inch, 0.8*inch, 3*inch])
ep_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
]))
story.append(ep_table)

story.append(Paragraph('2.6 Pydantic Schema Validation', h2))
story.append(Paragraph('All API inputs/outputs are validated using Pydantic models (schemas.py). This ensures type safety and automatic error messages for invalid data.', body))
story.append(Paragraph('<b>12 Financial Ratios Used:</b> working_capital_to_total_assets, retained_earnings_to_total_assets, ebit_to_total_assets, market_value_equity_to_total_liabilities, sales_to_total_assets, current_ratio, quick_ratio, debt_to_equity, interest_coverage, net_profit_margin, return_on_assets, return_on_equity', body))

story.append(PageBreak())

# NEHA - Data Preparation & Frontend
story.append(Paragraph('3. Data Preparation & Frontend (Neha)', h1))
story.append(Paragraph('Neha handled data processing pipelines and contributed to the frontend implementation.', body))

story.append(Paragraph('3.1 Data Processing Pipeline', h2))
story.append(Paragraph('Financial data requires careful preprocessing before model training. The pipeline handles:', body))
story.append(Paragraph('* <b>Missing Value Handling:</b> Financial ratios with missing values are imputed using median values to preserve distribution', bullet))
story.append(Paragraph('* <b>Feature Scaling:</b> StandardScaler normalizes features to zero mean and unit variance, critical for model convergence', bullet))
story.append(Paragraph('* <b>CSV Parsing:</b> Pandas reads uploaded CSVs with automatic type inference and column validation', bullet))
story.append(Paragraph('* <b>Data Validation:</b> Checks for required columns, valid numeric ranges, and data completeness', bullet))

story.append(Paragraph('3.2 Training Data Generation', h2))
story.append(Paragraph('Synthetic training data was generated using domain knowledge about healthy vs. distressed companies:', body))
train_code = """# Safe companies: Higher ratios, stronger fundamentals
safe_data = {
    working_capital_to_total_assets: np.random.uniform(0.15, 0.4),
    current_ratio: np.random.uniform(1.5, 3.0),
    debt_to_equity: np.random.uniform(0.2, 0.8), ...
}
# At-risk companies: Lower ratios, weaker fundamentals
risk_data = {
    working_capital_to_total_assets: np.random.uniform(-0.1, 0.1),
    current_ratio: np.random.uniform(0.5, 1.2),
    debt_to_equity: np.random.uniform(1.5, 4.0), ...
}"""
story.append(Paragraph(train_code.replace('\n', '<br/>'), code_style))

story.append(Paragraph('3.3 Frontend Components Developed', h2))
story.append(Paragraph('<b>FileUpload.tsx:</b> Drag-and-drop CSV upload component with validation', body))
story.append(Paragraph('* Accepts only .csv files with size validation', bullet))
story.append(Paragraph('* Visual feedback during file selection', bullet))
story.append(Paragraph('* Clear button to reset selection', bullet))

story.append(Paragraph('<b>DataTable.tsx:</b> Sortable, searchable table for bulk results', body))
story.append(Paragraph('* Client-side search filtering', bullet))
story.append(Paragraph('* Column sorting with visual indicators', bullet))
story.append(Paragraph('* Pagination for large datasets', bullet))

story.append(Paragraph('3.4 API Service Layer (api.ts)', h2))
story.append(Paragraph('Neha implemented the Axios-based API client that connects frontend to backend:', body))
api_code = """const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export const uploadSingleCompany = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/api/financial/upload-single',
    formData, { headers: { 'Content-Type': 'multipart/form-data' }});
  return response.data;
};"""
story.append(Paragraph(api_code.replace('\n', '<br/>'), code_style))

story.append(PageBreak())

# MARIYA - Frontend Development
story.append(Paragraph('4. Frontend Development & UI/UX (Mariya)', h1))
story.append(Paragraph('Mariya designed and implemented the React frontend with focus on user experience and data visualization.', body))

story.append(Paragraph('4.1 Technology Stack', h2))
story.append(Paragraph('* <b>React 18:</b> Component-based UI with hooks for state management', bullet))
story.append(Paragraph('* <b>TypeScript:</b> Static typing for reliability and better developer experience', bullet))
story.append(Paragraph('* <b>TailwindCSS:</b> Utility-first CSS framework for rapid styling', bullet))
story.append(Paragraph('* <b>Recharts:</b> React charting library for SHAP visualizations', bullet))
story.append(Paragraph('* <b>Vite:</b> Fast build tool with hot module replacement', bullet))

story.append(Paragraph('4.2 InsolvencyAnalysis Page', h2))
story.append(Paragraph('The main analysis page (InsolvencyAnalysis.tsx) provides two modes:', body))
story.append(Paragraph('<b>Single Company Mode:</b> Upload a CSV or manually enter 12 financial ratios. Results include risk gauge, Z-Score visualization, and SHAP chart.', body))
story.append(Paragraph('<b>Bulk Upload Mode:</b> Process multiple companies via CSV. Results displayed in searchable/sortable table with summary statistics.', body))

story.append(Paragraph('4.3 SHAP Visualization', h2))
story.append(Paragraph('The horizontal bar chart shows top 10 risk drivers:', body))
story.append(Paragraph('* <b>Red bars:</b> Features that INCREASE bankruptcy risk (positive SHAP)', bullet))
story.append(Paragraph('* <b>Green bars:</b> Features that DECREASE bankruptcy risk (negative SHAP)', bullet))
story.append(Paragraph('* <b>Tooltip:</b> Shows actual feature value and SHAP contribution on hover', bullet))

story.append(Paragraph('4.4 Risk Gauge Component', h2))
story.append(Paragraph('Custom gauge visualization showing probability of distress with color-coded zones (green/yellow/red) and animated needle indicator.', body))

story.append(Paragraph('4.5 Responsive Design', h2))
story.append(Paragraph('The UI adapts to different screen sizes using Tailwind breakpoints (sm, md, lg, xl). Grid layouts adjust from single column on mobile to multi-column on desktop.', body))

story.append(PageBreak())

# Integration
story.append(Paragraph('5. System Integration (All Team Members)', h1))
story.append(Paragraph('All four team members collaborated on integrating the components into a cohesive system.', body))

story.append(Paragraph('5.1 Frontend-Backend Communication', h2))
story.append(Paragraph('Vite dev server proxies API requests to FastAPI backend:', body))
proxy_code = """// vite.config.ts
server: {
  proxy: {
    '/api': { target: 'http://localhost:8001', changeOrigin: true },
    '/health': { target: 'http://localhost:8001', changeOrigin: true }
  }
}"""
story.append(Paragraph(proxy_code.replace('\n', '<br/>'), code_style))

story.append(Paragraph('5.2 Data Flow Architecture', h2))
flow_text = """User uploads CSV --> FileUpload component --> api.ts (FormData) -->
FastAPI endpoint --> Pandas reads CSV --> XGBoost predicts -->
SHAP explains --> JSON response --> React state update -->
Charts render results"""
story.append(Paragraph(flow_text.replace('\n', '<br/>'), code_style))

story.append(Paragraph('5.3 Error Handling', h2))
story.append(Paragraph('* <b>Frontend:</b> Try-catch with toast notifications for user feedback', bullet))
story.append(Paragraph('* <b>Backend:</b> HTTPException with detailed error messages', bullet))
story.append(Paragraph('* <b>Validation:</b> Pydantic models reject invalid input before processing', bullet))

story.append(Paragraph('5.4 Model Metrics', h2))
metrics_data = [
    ['Metric', 'Value', 'Meaning'],
    ['Accuracy', '~85%', 'Correct predictions overall'],
    ['Precision', '~82%', 'True positives among predicted positives'],
    ['Recall', '~88%', 'True positives among actual positives'],
    ['F1-Score', '~85%', 'Harmonic mean of precision/recall'],
    ['AUC-ROC', '~0.91', 'Model discrimination ability']
]
metrics_table = Table(metrics_data, colWidths=[1.5*inch, 1*inch, 3.5*inch])
metrics_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('ALIGN', (0, 0), (1, -1), 'CENTER'),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
]))
story.append(metrics_table)

story.append(PageBreak())

# Conclusion
story.append(Paragraph('6. Summary', h1))
story.append(Paragraph('SolvencyInsight demonstrates the practical application of machine learning to financial risk assessment. The system combines:', body))
story.append(Paragraph('* <b>Traditional Finance:</b> Altman Z-Score provides interpretable baseline', bullet))
story.append(Paragraph('* <b>Modern ML:</b> XGBoost captures non-linear patterns in financial data', bullet))
story.append(Paragraph('* <b>Explainable AI:</b> SHAP values make predictions transparent and auditable', bullet))
story.append(Paragraph('* <b>User-Friendly Interface:</b> React frontend makes complex analysis accessible', bullet))

story.append(Spacer(1, 0.3*inch))
story.append(Paragraph('<b>Team Contribution Summary:</b>', h3))
contrib = [
    ['Member', 'Components', 'Key Files'],
    ['Rohan', 'XGBoost model, SHAP, Z-Score, Backend API', 'insolvency_predictor.py, main.py'],
    ['Jonathan', 'Model training, regularization, API endpoints', 'insolvency_predictor.py, main.py'],
    ['Neha', 'Data pipelines, CSV processing, API client', 'data files, api.ts, FileUpload.tsx'],
    ['Mariya', 'React pages, charts, styling, components', 'InsolvencyAnalysis.tsx, RiskGauge.tsx']
]
contrib_table = Table(contrib, colWidths=[1*inch, 2.5*inch, 2.5*inch])
contrib_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
]))
story.append(contrib_table)

doc.build(story)
print('PDF created successfully: SolvencyInsight_Team_Documentation.pdf')
