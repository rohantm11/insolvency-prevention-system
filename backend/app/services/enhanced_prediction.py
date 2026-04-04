"""
Enhanced Prediction Service for Insolvency Prevention System.

Combines ML model predictions with live market intelligence
for more accurate and contextual risk assessments.
"""

import pickle
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import pandas as pd

from .market_intelligence import (
    MarketIntelligenceService,
    MarketIntelligenceReport,
)


@dataclass
class EnhancedPredictionResult:
    """Enhanced prediction with market context."""
    # Base model prediction
    base_probability: float
    base_prediction: str

    # Market-adjusted prediction
    adjusted_probability: float
    adjusted_prediction: str
    risk_level: str

    # Market intelligence
    market_report: Optional[MarketIntelligenceReport] = None

    # Breakdown
    model_contribution: float = 0.0
    market_contribution: float = 0.0

    # Recommendations
    risk_factors: list = None
    recommendations: list = None

    def __post_init__(self):
        if self.risk_factors is None:
            self.risk_factors = []
        if self.recommendations is None:
            self.recommendations = []


class EnhancedPredictionService:
    """
    Service that combines ML predictions with market intelligence.
    """

    def __init__(self, models_dir: Optional[Path] = None):
        if models_dir is None:
            # Default path relative to backend
            models_dir = Path(__file__).parent.parent.parent.parent / 'ml_models' / 'trained_models'

        self.models_dir = models_dir
        self.market_service = MarketIntelligenceService()

        # Load models
        self.insolvency_model = None
        self.insolvency_features = None
        self.employee_model = None
        self.employee_features = None
        self.employee_encoders = None

        self._load_models()

    def _load_models(self):
        """Load trained ML models."""
        # Insolvency model
        insolvency_path = self.models_dir / 'insolvency_model.pkl'
        if insolvency_path.exists():
            with open(insolvency_path, 'rb') as f:
                data = pickle.load(f)
                self.insolvency_model = data['model']
                self.insolvency_features = data['feature_names']

        # Employee model
        employee_path = self.models_dir / 'employee_model.pkl'
        if employee_path.exists():
            with open(employee_path, 'rb') as f:
                data = pickle.load(f)
                self.employee_model = data['model']
                self.employee_features = data['feature_names']
                self.employee_encoders = data.get('label_encoders', {})

    async def predict_insolvency_enhanced(
        self,
        company_data: dict,
        include_market_intelligence: bool = True
    ) -> EnhancedPredictionResult:
        """
        Make enhanced insolvency prediction with market intelligence.
        """
        if self.insolvency_model is None:
            raise RuntimeError("Insolvency model not loaded")

        # Get base model prediction
        features = pd.DataFrame([company_data])[self.insolvency_features]
        features = features.fillna(features.median())

        base_prob = self.insolvency_model.predict_proba(features)[0, 1]
        base_pred = "Bankrupt" if base_prob >= 0.5 else "Healthy"

        # Get market intelligence if requested
        market_report = None
        market_adjustment = 0.0

        if include_market_intelligence:
            company_name = company_data.get('company_name', 'Unknown Company')
            industry = company_data.get('industry', None)
            description = company_data.get('description', '')

            try:
                market_report = await self.market_service.generate_report(
                    company_name=company_name,
                    industry=industry,
                    description=description
                )
                market_adjustment = market_report.risk_adjustment
            except Exception as e:
                print(f"Market intelligence error: {e}")
                market_adjustment = 0.0

        # Calculate adjusted probability
        # Formula: adjusted = base + (base * adjustment) + (adjustment * 0.5)
        # This ensures market conditions affect prediction but don't dominate
        adjusted_prob = base_prob + (base_prob * market_adjustment * 0.5) + (market_adjustment * 0.3)
        adjusted_prob = max(0.0, min(1.0, adjusted_prob))

        adjusted_pred = "Bankrupt" if adjusted_prob >= 0.5 else "Healthy"

        # Determine risk level
        if adjusted_prob < 0.2:
            risk_level = "LOW"
        elif adjusted_prob < 0.4:
            risk_level = "MODERATE"
        elif adjusted_prob < 0.6:
            risk_level = "ELEVATED"
        elif adjusted_prob < 0.8:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

        # Identify risk factors
        risk_factors = self._identify_risk_factors(company_data, market_report)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            risk_level, risk_factors, market_report
        )

        return EnhancedPredictionResult(
            base_probability=base_prob,
            base_prediction=base_pred,
            adjusted_probability=adjusted_prob,
            adjusted_prediction=adjusted_pred,
            risk_level=risk_level,
            market_report=market_report,
            model_contribution=base_prob,
            market_contribution=market_adjustment,
            risk_factors=risk_factors,
            recommendations=recommendations
        )

    def _identify_risk_factors(
        self,
        company_data: dict,
        market_report: Optional[MarketIntelligenceReport]
    ) -> list[dict]:
        """Identify specific risk factors from data and market conditions."""
        factors = []

        # Financial ratio analysis
        thresholds = {
            'current_ratio': (1.0, 'below', 'Low liquidity - current ratio below 1.0'),
            'debt_to_equity': (3.0, 'above', 'High leverage - debt-to-equity ratio above 3.0'),
            'interest_coverage': (1.5, 'below', 'Weak debt servicing - interest coverage below 1.5'),
            'net_profit_margin': (0.0, 'below', 'Unprofitable - negative net profit margin'),
            'return_on_assets': (0.0, 'below', 'Negative return on assets'),
            'working_capital_to_total_assets': (0.0, 'below', 'Negative working capital'),
            'retained_earnings_to_total_assets': (-0.1, 'below', 'Accumulated losses indicated'),
        }

        for metric, (threshold, direction, message) in thresholds.items():
            value = company_data.get(metric)
            if value is not None:
                if direction == 'below' and value < threshold:
                    factors.append({
                        'type': 'financial',
                        'metric': metric,
                        'value': value,
                        'threshold': threshold,
                        'message': message,
                        'severity': 'high' if abs(value - threshold) > threshold * 0.5 else 'medium'
                    })
                elif direction == 'above' and value > threshold:
                    factors.append({
                        'type': 'financial',
                        'metric': metric,
                        'value': value,
                        'threshold': threshold,
                        'message': message,
                        'severity': 'high' if abs(value - threshold) > threshold * 0.5 else 'medium'
                    })

        # Market-based risk factors
        if market_report:
            # Negative news sentiment
            if market_report.overall_news_sentiment < -0.2:
                factors.append({
                    'type': 'market',
                    'metric': 'news_sentiment',
                    'value': market_report.overall_news_sentiment,
                    'message': 'Negative news coverage detected for company/industry',
                    'severity': 'medium'
                })

            # Sector decline
            if market_report.sector_data and market_report.sector_data.performance_1m < -0.05:
                factors.append({
                    'type': 'market',
                    'metric': 'sector_performance',
                    'value': market_report.sector_data.performance_1m,
                    'message': f'{market_report.sector} sector declining over past month',
                    'severity': 'medium'
                })

            # Economic headwinds
            if market_report.economic_indicators:
                econ = market_report.economic_indicators
                if econ.unemployment_rate and econ.unemployment_rate > 5.5:
                    factors.append({
                        'type': 'economic',
                        'metric': 'unemployment',
                        'value': econ.unemployment_rate,
                        'message': 'Elevated unemployment rate indicates economic stress',
                        'severity': 'low'
                    })
                if econ.interest_rate and econ.interest_rate > 5.0:
                    factors.append({
                        'type': 'economic',
                        'metric': 'interest_rate',
                        'value': econ.interest_rate,
                        'message': 'High interest rates increase borrowing costs',
                        'severity': 'low'
                    })

        return factors

    def _generate_recommendations(
        self,
        risk_level: str,
        risk_factors: list[dict],
        market_report: Optional[MarketIntelligenceReport]
    ) -> list[str]:
        """Generate actionable recommendations based on risk assessment."""
        recommendations = []

        # Risk level based recommendations
        if risk_level in ['HIGH', 'CRITICAL']:
            recommendations.append("Conduct immediate financial review and cash flow analysis")
            recommendations.append("Consider engaging financial restructuring advisors")
            recommendations.append("Review and renegotiate credit facilities if possible")
        elif risk_level == 'ELEVATED':
            recommendations.append("Increase monitoring frequency of key financial metrics")
            recommendations.append("Develop contingency plans for potential cash flow issues")
            recommendations.append("Review cost structure for optimization opportunities")
        elif risk_level == 'MODERATE':
            recommendations.append("Continue regular monitoring of financial health indicators")
            recommendations.append("Consider building additional liquidity reserves")

        # Factor-specific recommendations
        financial_factors = [f for f in risk_factors if f['type'] == 'financial']

        for factor in financial_factors:
            if factor['metric'] == 'current_ratio':
                recommendations.append("Improve working capital management - consider inventory reduction or faster receivables collection")
            elif factor['metric'] == 'debt_to_equity':
                recommendations.append("Consider debt reduction strategies or equity injection")
            elif factor['metric'] == 'interest_coverage':
                recommendations.append("Focus on improving operating income or refinancing debt at lower rates")
            elif factor['metric'] == 'net_profit_margin':
                recommendations.append("Review pricing strategy and cost structure to restore profitability")

        # Market-based recommendations
        if market_report:
            if market_report.overall_news_sentiment < -0.2:
                recommendations.append("Monitor industry developments closely and prepare for potential sector-wide challenges")

            if market_report.sector_data and market_report.sector_data.trend == 'bearish':
                recommendations.append(f"Consider diversification as {market_report.sector} sector shows weakness")

        # Deduplicate
        return list(dict.fromkeys(recommendations))[:5]  # Top 5 unique recommendations


# =============================================================================
# Singleton instance for API use
# =============================================================================

_service_instance: Optional[EnhancedPredictionService] = None


def get_prediction_service() -> EnhancedPredictionService:
    """Get or create the prediction service singleton."""
    global _service_instance
    if _service_instance is None:
        _service_instance = EnhancedPredictionService()
    return _service_instance
