"""
Test script for Market Intelligence functionality.

Tests the market intelligence module standalone (without API server).

Usage:
    python scripts/test_market_intelligence.py
"""

import sys
from pathlib import Path
import asyncio

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'backend'))

from app.services.market_intelligence import (
    MarketIntelligenceService,
    classify_industry,
    analyze_sentiment,
    INDUSTRY_KEYWORDS
)
from app.services.enhanced_prediction import EnhancedPredictionService


def print_banner(text, char="="):
    """Print a banner."""
    width = 70
    print("\n" + char * width)
    print(f" {text}")
    print(char * width)


def print_section(text):
    """Print a section header."""
    print(f"\n>>> {text}")
    print("-" * 50)


async def test_industry_classification():
    """Test industry classification."""
    print_section("Industry Classification")

    test_cases = [
        ("Target Corporation", "Major retail chain", "retail"),
        ("Microsoft", "Software and cloud computing", "technology"),
        ("Goldman Sachs", "Investment banking", "financial"),
        ("Pfizer Inc", "Pharmaceutical company", "healthcare"),
        ("ExxonMobil", "Oil and gas company", "energy"),
        ("Generic Company LLC", "", "general"),
    ]

    for name, description, expected_industry in test_cases:
        industry, sector = classify_industry(name, description)
        status = "[OK]" if industry == expected_industry else "[!!]"
        print(f"  {status} {name[:25]:<25} -> {industry:<15} ({sector})")


def test_sentiment_analysis():
    """Test sentiment analysis."""
    print_section("Sentiment Analysis")

    test_texts = [
        ("Company reports record profits and strong growth", 0.5),
        ("Stock plunges amid bankruptcy fears and losses", -0.5),
        ("Market remains stable with neutral outlook", 0.0),
        ("Layoffs announced as sales dramatically decline", -0.5),
        ("Innovation breakthrough drives optimistic forecasts", 0.5),
        ("Not a bad quarter despite some concerns", 0.0),
    ]

    for text, expected_direction in test_texts:
        score = analyze_sentiment(text)
        if expected_direction > 0:
            status = "[OK]" if score > 0 else "[!!]"
        elif expected_direction < 0:
            status = "[OK]" if score < 0 else "[!!]"
        else:
            status = "[OK]" if abs(score) < 0.3 else "[!!]"

        print(f"  {status} Score: {score:+.2f} | \"{text[:50]}...\"")


async def test_market_intelligence():
    """Test market intelligence service."""
    print_section("Market Intelligence Service")

    service = MarketIntelligenceService()

    # Test with a retail company
    print("\n  Testing with: Target Corporation (Retail)")
    print("  " + "-" * 40)

    try:
        report = await service.generate_report(
            company_name="Target Corporation",
            industry="retail",
            description="Major retail chain"
        )

        print(f"  Industry: {report.industry}")
        print(f"  Sector: {report.sector}")
        print(f"  News Articles Found: {len(report.news_articles)}")
        print(f"  Overall Sentiment: {report.overall_news_sentiment:+.3f}")
        print(f"  Risk Adjustment: {report.risk_adjustment:+.3f}")

        if report.sector_data:
            print(f"\n  Sector Performance:")
            print(f"    - 1 Day: {report.sector_data.performance_1d*100:+.2f}%")
            print(f"    - 1 Month: {report.sector_data.performance_1m*100:+.2f}%")
            print(f"    - YTD: {report.sector_data.performance_ytd*100:+.2f}%")
            print(f"    - Trend: {report.sector_data.trend}")

        if report.economic_indicators:
            print(f"\n  Economic Indicators:")
            if report.economic_indicators.unemployment_rate:
                print(f"    - Unemployment: {report.economic_indicators.unemployment_rate:.1f}%")
            if report.economic_indicators.inflation_rate:
                print(f"    - Inflation: {report.economic_indicators.inflation_rate:.1f}%")
            if report.economic_indicators.interest_rate:
                print(f"    - Interest Rate: {report.economic_indicators.interest_rate:.2f}%")

        print(f"\n  Market Summary:")
        print(f"    {report.market_summary[:200]}...")

        if report.news_articles:
            print(f"\n  Sample News (first 3):")
            for i, article in enumerate(report.news_articles[:3], 1):
                sentiment = "+" if article.sentiment_score > 0.1 else ("-" if article.sentiment_score < -0.1 else "=")
                print(f"    {i}. [{sentiment}] {article.title[:60]}...")

    except Exception as e:
        print(f"  [ERROR] Market intelligence failed: {e}")


async def test_enhanced_prediction():
    """Test enhanced prediction service."""
    print_section("Enhanced Prediction Service")

    try:
        service = EnhancedPredictionService()

        # Test with a company at moderate risk
        company_data = {
            'company_name': 'TestRetail Corp',
            'industry': 'retail',
            'description': 'Mid-size retail chain',
            'working_capital_to_total_assets': 0.10,
            'retained_earnings_to_total_assets': 0.15,
            'ebit_to_total_assets': 0.05,
            'market_value_equity_to_total_liabilities': 1.2,
            'sales_to_total_assets': 0.9,
            'current_ratio': 1.3,
            'quick_ratio': 0.8,
            'debt_to_equity': 1.8,
            'interest_coverage': 2.5,
            'net_profit_margin': 0.02,
            'return_on_assets': 0.04,
            'return_on_equity': 0.08
        }

        print("\n  Testing Enhanced Prediction:")
        print("  Company: TestRetail Corp (Retail)")
        print("  " + "-" * 40)

        # Test without market intelligence
        print("\n  [Without Market Intelligence]")
        result_basic = await service.predict_insolvency_enhanced(
            company_data=company_data,
            include_market_intelligence=False
        )

        print(f"    Base Probability: {result_basic.base_probability:.1%}")
        print(f"    Base Prediction: {result_basic.base_prediction}")
        print(f"    Risk Level: {result_basic.risk_level}")

        # Test with market intelligence
        print("\n  [With Market Intelligence]")
        result_enhanced = await service.predict_insolvency_enhanced(
            company_data=company_data,
            include_market_intelligence=True
        )

        print(f"    Base Probability: {result_enhanced.base_probability:.1%}")
        print(f"    Market Adjustment: {result_enhanced.market_contribution:+.3f}")
        print(f"    Adjusted Probability: {result_enhanced.adjusted_probability:.1%}")
        print(f"    Adjusted Prediction: {result_enhanced.adjusted_prediction}")
        print(f"    Risk Level: {result_enhanced.risk_level}")

        if result_enhanced.risk_factors:
            print(f"\n  Risk Factors Identified: {len(result_enhanced.risk_factors)}")
            for factor in result_enhanced.risk_factors[:3]:
                print(f"    - [{factor['severity'].upper()}] {factor['message']}")

        if result_enhanced.recommendations:
            print(f"\n  Recommendations:")
            for rec in result_enhanced.recommendations[:3]:
                print(f"    - {rec}")

    except Exception as e:
        print(f"  [ERROR] Enhanced prediction failed: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests."""
    print_banner("MARKET INTELLIGENCE TEST SUITE", char="#")

    # Test individual components
    await test_industry_classification()
    test_sentiment_analysis()

    # Test services
    await test_market_intelligence()
    await test_enhanced_prediction()

    print_banner("TEST COMPLETE", char="#")
    print("""
  Summary:
  - Industry classification: Maps company to industry/sector
  - Sentiment analysis: Analyzes news headline sentiment
  - Market intelligence: Fetches and analyzes market data
  - Enhanced prediction: Combines ML + market signals

  Note: If no API keys are configured, the system uses
  simulated/fallback data for demo purposes.
    """)


if __name__ == '__main__':
    asyncio.run(main())
