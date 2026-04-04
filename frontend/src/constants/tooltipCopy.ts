/**
 * Plain-English explanations for Z-Score, SHAP, and related terms.
 * Used in tooltips for management and investors (non–data scientists).
 */

export const TOOLTIP_COPY = {
  ALTMAN_Z_SCORE:
    'A classic formula that uses 5 financial ratios to predict bankruptcy risk. Z > 2.99 is safe, 1.81–2.99 is grey zone, < 1.81 is distress.',
  Z_SCORE:
    'A single number summarizing financial health. Higher is safer. Above 2.99 = low risk, 1.81–2.99 = watch, below 1.81 = high distress risk.',
  SHAP_VALUE:
    'SHAP shows how much each factor pushed the prediction up or down. Positive = increases risk, negative = decreases risk. Helps explain why the model said what it did.',
  SHAP:
    'Explainability method that shows which inputs (e.g. debt ratio, profit margin) most influenced this prediction. Every prediction in SolvencyInsight includes SHAP.',
  DISTRESS_PROBABILITY:
    'The model’s estimated chance (0–100%) that the company will face financial distress. Not a guarantee—use it with the Z-Score and your own judgment.',
  RISK_DRIVERS:
    'The financial factors that contributed most to this risk score. Shown as SHAP values: positive = increased risk, negative = decreased risk.',
  RISK_CATEGORY:
    'Summary bucket: Low (typically &lt;30% distress probability), Medium (30–70%), or High (&gt;70%). Based on the ML model and Z-Score.',
  RETENTION_SCORE:
    'A 0–100 score combining performance, satisfaction, and tenure. Higher = more valuable to retain. Used in layoff simulation to prioritize who to keep.',
  LAYOFF_PRIORITY:
    'Suggested order for workforce reduction: High = consider for layoff first, Low = try to retain. Based on retention score and cost.',
} as const;
