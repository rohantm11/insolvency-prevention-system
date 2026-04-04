"""
Market Intelligence Service for Insolvency Prevention System.

Provides live market research capabilities:
- Industry news sentiment analysis
- Sector performance tracking
- Competitor health monitoring
- Economic indicator integration

Uses free APIs (NewsAPI, Alpha Vantage, FRED) and web scraping fallbacks.
"""

import os
import re
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field
import httpx
from bs4 import BeautifulSoup


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class NewsArticle:
    """Represents a news article with sentiment."""
    title: str
    source: str
    url: str
    published_at: datetime
    summary: str
    sentiment_score: float  # -1 (negative) to 1 (positive)
    relevance_score: float  # 0 to 1


@dataclass
class SectorData:
    """Sector performance metrics."""
    sector: str
    performance_1d: float
    performance_1w: float
    performance_1m: float
    performance_ytd: float
    trend: str  # "bullish", "bearish", "neutral"


@dataclass
class EconomicIndicators:
    """Key economic indicators."""
    gdp_growth: Optional[float] = None
    unemployment_rate: Optional[float] = None
    inflation_rate: Optional[float] = None
    interest_rate: Optional[float] = None
    consumer_confidence: Optional[float] = None
    pmi: Optional[float] = None  # Purchasing Managers Index


@dataclass
class MarketIntelligenceReport:
    """Complete market intelligence report."""
    company_name: str
    industry: str
    sector: str
    generated_at: datetime
    news_articles: list[NewsArticle] = field(default_factory=list)
    overall_news_sentiment: float = 0.0
    sector_data: Optional[SectorData] = None
    economic_indicators: Optional[EconomicIndicators] = None
    competitor_signals: list[dict] = field(default_factory=list)
    risk_adjustment: float = 0.0  # -0.2 to 0.2 adjustment to base risk
    market_summary: str = ""


# =============================================================================
# Industry Classification
# =============================================================================

INDUSTRY_KEYWORDS = {
    "retail": {
        "keywords": ["retail", "store", "shop", "consumer", "merchandise", "e-commerce", "supermarket", "mall"],
        "sector": "Consumer Discretionary",
        "related_sectors": ["Consumer Staples", "Technology"],
        "news_terms": ["retail sales", "consumer spending", "e-commerce growth", "store closures"]
    },
    "technology": {
        "keywords": ["tech", "software", "hardware", "cloud", "saas", "digital", "it services", "computing"],
        "sector": "Technology",
        "related_sectors": ["Communication Services", "Industrials"],
        "news_terms": ["tech sector", "software market", "cloud computing", "AI adoption"]
    },
    "healthcare": {
        "keywords": ["health", "medical", "pharma", "biotech", "hospital", "clinic", "drug", "therapeutic"],
        "sector": "Healthcare",
        "related_sectors": ["Biotechnology", "Life Sciences"],
        "news_terms": ["healthcare costs", "drug approval", "medical devices", "health insurance"]
    },
    "financial": {
        "keywords": ["bank", "finance", "insurance", "investment", "lending", "credit", "capital", "asset management"],
        "sector": "Financials",
        "related_sectors": ["Real Estate", "Insurance"],
        "news_terms": ["interest rates", "bank earnings", "credit markets", "financial regulation"]
    },
    "manufacturing": {
        "keywords": ["manufacturing", "industrial", "factory", "production", "assembly", "machinery", "equipment"],
        "sector": "Industrials",
        "related_sectors": ["Materials", "Technology"],
        "news_terms": ["manufacturing output", "supply chain", "industrial production", "factory orders"]
    },
    "energy": {
        "keywords": ["energy", "oil", "gas", "renewable", "solar", "wind", "utility", "power"],
        "sector": "Energy",
        "related_sectors": ["Utilities", "Materials"],
        "news_terms": ["oil prices", "energy demand", "renewable energy", "power generation"]
    },
    "real_estate": {
        "keywords": ["real estate", "property", "reit", "commercial property", "residential", "development"],
        "sector": "Real Estate",
        "related_sectors": ["Financials", "Materials"],
        "news_terms": ["property market", "housing prices", "commercial real estate", "mortgage rates"]
    },
    "transportation": {
        "keywords": ["transport", "logistics", "shipping", "airline", "freight", "delivery", "trucking"],
        "sector": "Industrials",
        "related_sectors": ["Energy", "Technology"],
        "news_terms": ["shipping rates", "freight demand", "airline traffic", "logistics costs"]
    },
    "hospitality": {
        "keywords": ["hotel", "restaurant", "travel", "tourism", "hospitality", "leisure", "entertainment"],
        "sector": "Consumer Discretionary",
        "related_sectors": ["Real Estate", "Transportation"],
        "news_terms": ["travel demand", "hotel occupancy", "restaurant sales", "tourism spending"]
    },
    "construction": {
        "keywords": ["construction", "building", "contractor", "infrastructure", "engineering"],
        "sector": "Industrials",
        "related_sectors": ["Materials", "Real Estate"],
        "news_terms": ["construction spending", "building permits", "infrastructure investment"]
    }
}


def classify_industry(company_name: str, description: str = "") -> tuple[str, str]:
    """
    Classify company industry based on name and description.
    Returns (industry, sector).
    """
    text = f"{company_name} {description}".lower()

    best_match = None
    best_score = 0

    for industry, data in INDUSTRY_KEYWORDS.items():
        score = sum(1 for kw in data["keywords"] if kw in text)
        if score > best_score:
            best_score = score
            best_match = industry

    if best_match:
        return best_match, INDUSTRY_KEYWORDS[best_match]["sector"]

    # Default to general business
    return "general", "Diversified"


# =============================================================================
# Sentiment Analysis (Simple Rule-Based)
# =============================================================================

POSITIVE_WORDS = {
    "growth", "profit", "surge", "gain", "rise", "boost", "strong", "success",
    "optimistic", "recovery", "expansion", "positive", "beat", "exceed", "upgrade",
    "bullish", "rally", "soar", "momentum", "record", "breakthrough", "innovation"
}

NEGATIVE_WORDS = {
    "loss", "decline", "drop", "fall", "weak", "struggle", "bankruptcy", "default",
    "crisis", "recession", "layoff", "closure", "warning", "concern", "risk",
    "bearish", "crash", "plunge", "slump", "miss", "downgrade", "fraud", "debt"
}

INTENSIFIERS = {"very", "extremely", "significantly", "sharply", "dramatically"}
NEGATORS = {"not", "no", "never", "neither", "without", "hardly"}


def analyze_sentiment(text: str) -> float:
    """
    Analyze sentiment of text using rule-based approach.
    Returns score from -1 (very negative) to 1 (very positive).
    """
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)

    positive_count = 0
    negative_count = 0

    for i, word in enumerate(words):
        # Check for negation in previous 3 words
        negated = any(words[max(0, i-3):i].count(neg) > 0 for neg in NEGATORS)

        # Check for intensifier in previous 2 words
        intensified = any(words[max(0, i-2):i].count(intens) > 0 for intens in INTENSIFIERS)
        multiplier = 1.5 if intensified else 1.0

        if word in POSITIVE_WORDS:
            if negated:
                negative_count += multiplier
            else:
                positive_count += multiplier
        elif word in NEGATIVE_WORDS:
            if negated:
                positive_count += multiplier * 0.5  # Negated negative is weakly positive
            else:
                negative_count += multiplier

    total = positive_count + negative_count
    if total == 0:
        return 0.0

    # Calculate sentiment score
    score = (positive_count - negative_count) / total
    return max(-1.0, min(1.0, score))


# =============================================================================
# News Fetching
# =============================================================================

class NewsService:
    """Fetches news from multiple sources."""

    def __init__(self, news_api_key: Optional[str] = None):
        self.news_api_key = news_api_key or os.getenv("NEWS_API_KEY")
        self.cache = {}
        self.cache_ttl = timedelta(minutes=15)

    def _get_cache_key(self, query: str) -> str:
        return hashlib.md5(query.encode()).hexdigest()

    def _is_cache_valid(self, key: str) -> bool:
        if key not in self.cache:
            return False
        cached_time = self.cache[key].get("timestamp")
        return datetime.now() - cached_time < self.cache_ttl

    async def fetch_news(self, query: str, days: int = 7) -> list[NewsArticle]:
        """Fetch news articles for a query."""
        cache_key = self._get_cache_key(query)

        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["articles"]

        articles = []

        # Try NewsAPI first
        if self.news_api_key:
            articles = await self._fetch_from_newsapi(query, days)

        # Fallback to web scraping if no results
        if not articles:
            articles = await self._scrape_news(query)

        # Cache results
        self.cache[cache_key] = {
            "articles": articles,
            "timestamp": datetime.now()
        }

        return articles

    async def _fetch_from_newsapi(self, query: str, days: int) -> list[NewsArticle]:
        """Fetch from NewsAPI.org (free tier: 100 requests/day)."""
        articles = []
        from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "from": from_date,
            "sortBy": "relevancy",
            "language": "en",
            "pageSize": 10,
            "apiKey": self.news_api_key
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("articles", []):
                        title = item.get("title", "")
                        description = item.get("description", "") or ""

                        sentiment = analyze_sentiment(f"{title} {description}")

                        articles.append(NewsArticle(
                            title=title,
                            source=item.get("source", {}).get("name", "Unknown"),
                            url=item.get("url", ""),
                            published_at=datetime.fromisoformat(
                                item.get("publishedAt", "").replace("Z", "+00:00")
                            ) if item.get("publishedAt") else datetime.now(),
                            summary=description[:300],
                            sentiment_score=sentiment,
                            relevance_score=0.8  # NewsAPI already filters by relevance
                        ))
        except Exception as e:
            print(f"NewsAPI error: {e}")

        return articles

    async def _scrape_news(self, query: str) -> list[NewsArticle]:
        """Fallback: scrape news from Google News RSS."""
        articles = []

        # Use Google News RSS feed
        url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'xml')
                    items = soup.find_all('item')[:10]

                    for item in items:
                        title = item.find('title').text if item.find('title') else ""
                        link = item.find('link').text if item.find('link') else ""
                        pub_date = item.find('pubDate').text if item.find('pubDate') else ""
                        source = item.find('source').text if item.find('source') else "Unknown"

                        sentiment = analyze_sentiment(title)

                        # Parse date
                        try:
                            published = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
                        except ValueError:
                            published = datetime.now()

                        articles.append(NewsArticle(
                            title=title,
                            source=source,
                            url=link,
                            published_at=published,
                            summary=title,  # RSS doesn't include full description
                            sentiment_score=sentiment,
                            relevance_score=0.6
                        ))
        except Exception as e:
            print(f"Scraping error: {e}")

        return articles


# =============================================================================
# Economic Data (FRED API)
# =============================================================================

class EconomicDataService:
    """Fetches economic indicators from FRED (Federal Reserve Economic Data)."""

    INDICATORS = {
        "GDP": "GDP",  # Gross Domestic Product
        "UNRATE": "unemployment_rate",  # Unemployment Rate
        "CPIAUCSL": "inflation_rate",  # Consumer Price Index
        "FEDFUNDS": "interest_rate",  # Federal Funds Rate
        "UMCSENT": "consumer_confidence",  # Consumer Sentiment
        "MANEMP": "manufacturing_employment"  # Manufacturing Employment
    }

    def __init__(self, fred_api_key: Optional[str] = None):
        self.api_key = fred_api_key or os.getenv("FRED_API_KEY")
        self.cache = {}
        self.cache_ttl = timedelta(hours=6)  # Economic data doesn't change often

    async def get_indicators(self) -> EconomicIndicators:
        """Fetch key economic indicators."""
        cache_key = "economic_indicators"

        if cache_key in self.cache:
            cached_time = self.cache[cache_key].get("timestamp")
            if datetime.now() - cached_time < self.cache_ttl:
                return self.cache[cache_key]["data"]

        indicators = EconomicIndicators()

        if not self.api_key:
            # Return reasonable defaults if no API key
            indicators.gdp_growth = 2.5
            indicators.unemployment_rate = 4.0
            indicators.inflation_rate = 3.2
            indicators.interest_rate = 5.25
            indicators.consumer_confidence = 68.0
            return indicators

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                for series_id, attr_name in self.INDICATORS.items():
                    url = "https://api.stlouisfed.org/fred/series/observations"
                    params = {
                        "series_id": series_id,
                        "api_key": self.api_key,
                        "file_type": "json",
                        "sort_order": "desc",
                        "limit": 1
                    }

                    response = await client.get(url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        observations = data.get("observations", [])
                        if observations:
                            value = observations[0].get("value")
                            if value and value != ".":
                                setattr(indicators, attr_name, float(value))
        except Exception as e:
            print(f"FRED API error: {e}")

        self.cache[cache_key] = {
            "data": indicators,
            "timestamp": datetime.now()
        }

        return indicators


# =============================================================================
# Sector Performance (Alpha Vantage)
# =============================================================================

class SectorService:
    """Fetches sector performance data."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY")
        self.cache = {}
        self.cache_ttl = timedelta(hours=1)

    async def get_sector_performance(self, sector: str) -> Optional[SectorData]:
        """Get performance data for a sector."""
        cache_key = f"sector_{sector}"

        if cache_key in self.cache:
            cached_time = self.cache[cache_key].get("timestamp")
            if datetime.now() - cached_time < self.cache_ttl:
                return self.cache[cache_key]["data"]

        if not self.api_key:
            # Return simulated data if no API key
            return self._get_simulated_sector_data(sector)

        try:
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "SECTOR",
                "apikey": self.api_key
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()

                    # Map our sector names to Alpha Vantage sector names
                    sector_mapping = {
                        "Technology": "Information Technology",
                        "Healthcare": "Health Care",
                        "Financials": "Financials",
                        "Consumer Discretionary": "Consumer Discretionary",
                        "Consumer Staples": "Consumer Staples",
                        "Energy": "Energy",
                        "Industrials": "Industrials",
                        "Materials": "Materials",
                        "Real Estate": "Real Estate",
                        "Utilities": "Utilities"
                    }

                    av_sector = sector_mapping.get(sector, sector)

                    perf_1d = data.get("Rank A: Real-Time Performance", {}).get(av_sector, "0%")
                    perf_1w = data.get("Rank B: 1 Day Performance", {}).get(av_sector, "0%")
                    perf_1m = data.get("Rank C: 5 Day Performance", {}).get(av_sector, "0%")
                    perf_ytd = data.get("Rank F: Year-to-Date (YTD) Performance", {}).get(av_sector, "0%")

                    def parse_pct(s):
                        return float(s.replace("%", "")) / 100 if s else 0.0

                    perf_1d_val = parse_pct(perf_1d)

                    sector_data = SectorData(
                        sector=sector,
                        performance_1d=perf_1d_val,
                        performance_1w=parse_pct(perf_1w),
                        performance_1m=parse_pct(perf_1m),
                        performance_ytd=parse_pct(perf_ytd),
                        trend="bullish" if perf_1d_val > 0.01 else ("bearish" if perf_1d_val < -0.01 else "neutral")
                    )

                    self.cache[cache_key] = {
                        "data": sector_data,
                        "timestamp": datetime.now()
                    }

                    return sector_data

        except Exception as e:
            print(f"Alpha Vantage error: {e}")

        return self._get_simulated_sector_data(sector)

    def _get_simulated_sector_data(self, sector: str) -> SectorData:
        """Return simulated sector data for demo purposes."""
        import random
        random.seed(hash(sector) % 100)  # Consistent per sector

        perf_1d = random.uniform(-0.02, 0.02)

        return SectorData(
            sector=sector,
            performance_1d=perf_1d,
            performance_1w=random.uniform(-0.05, 0.05),
            performance_1m=random.uniform(-0.10, 0.10),
            performance_ytd=random.uniform(-0.15, 0.25),
            trend="bullish" if perf_1d > 0.005 else ("bearish" if perf_1d < -0.005 else "neutral")
        )


# =============================================================================
# Main Market Intelligence Service
# =============================================================================

class MarketIntelligenceService:
    """
    Main service that combines all market intelligence sources.
    """

    def __init__(
        self,
        news_api_key: Optional[str] = None,
        fred_api_key: Optional[str] = None,
        alpha_vantage_key: Optional[str] = None
    ):
        self.news_service = NewsService(news_api_key)
        self.economic_service = EconomicDataService(fred_api_key)
        self.sector_service = SectorService(alpha_vantage_key)

    async def generate_report(
        self,
        company_name: str,
        industry: Optional[str] = None,
        description: str = ""
    ) -> MarketIntelligenceReport:
        """
        Generate a comprehensive market intelligence report.
        """
        # Classify industry if not provided
        if not industry:
            industry, sector = classify_industry(company_name, description)
        else:
            industry = industry.lower().replace(" ", "_")
            if industry in INDUSTRY_KEYWORDS:
                sector = INDUSTRY_KEYWORDS[industry]["sector"]
            else:
                sector = "Diversified"

        # Get industry-specific news terms
        industry_data = INDUSTRY_KEYWORDS.get(industry, {})
        news_terms = industry_data.get("news_terms", [industry])

        # Build search queries
        queries = [
            f"{company_name} financial news",
            f"{sector} sector outlook",
            *[f"{term}" for term in news_terms[:2]]
        ]

        # Fetch data concurrently
        news_tasks = [self.news_service.fetch_news(q) for q in queries]
        sector_task = self.sector_service.get_sector_performance(sector)
        economic_task = self.economic_service.get_indicators()

        results = await asyncio.gather(
            *news_tasks,
            sector_task,
            economic_task,
            return_exceptions=True
        )

        # Process news results
        all_articles = []
        for result in results[:-2]:  # All but last two are news
            if isinstance(result, list):
                all_articles.extend(result)

        # Deduplicate by title
        seen_titles = set()
        unique_articles = []
        for article in all_articles:
            title_key = article.title.lower()[:50]
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)

        # Sort by relevance and recency
        unique_articles.sort(
            key=lambda a: (a.relevance_score, a.published_at),
            reverse=True
        )
        unique_articles = unique_articles[:15]  # Keep top 15

        # Calculate overall sentiment
        if unique_articles:
            total_sentiment = sum(a.sentiment_score * a.relevance_score for a in unique_articles)
            total_weight = sum(a.relevance_score for a in unique_articles)
            overall_sentiment = total_sentiment / total_weight if total_weight > 0 else 0
        else:
            overall_sentiment = 0

        # Get sector and economic data
        sector_data = results[-2] if not isinstance(results[-2], Exception) else None
        economic_data = results[-1] if not isinstance(results[-1], Exception) else EconomicIndicators()

        # Calculate risk adjustment based on market conditions
        risk_adjustment = self._calculate_risk_adjustment(
            overall_sentiment,
            sector_data,
            economic_data
        )

        # Generate market summary
        market_summary = self._generate_summary(
            company_name,
            industry,
            sector,
            overall_sentiment,
            sector_data,
            economic_data,
            unique_articles
        )

        return MarketIntelligenceReport(
            company_name=company_name,
            industry=industry,
            sector=sector,
            generated_at=datetime.now(),
            news_articles=unique_articles,
            overall_news_sentiment=overall_sentiment,
            sector_data=sector_data,
            economic_indicators=economic_data,
            competitor_signals=[],  # TODO: Add competitor analysis
            risk_adjustment=risk_adjustment,
            market_summary=market_summary
        )

    def _calculate_risk_adjustment(
        self,
        sentiment: float,
        sector_data: Optional[SectorData],
        economic_data: Optional[EconomicIndicators]
    ) -> float:
        """
        Calculate risk adjustment factor based on market conditions.
        Returns value between -0.2 (reduce risk) and 0.2 (increase risk).
        """
        adjustment = 0.0

        # News sentiment impact (max +/- 0.08)
        adjustment += sentiment * -0.08  # Negative sentiment increases risk

        # Sector performance impact (max +/- 0.06)
        if sector_data:
            if sector_data.performance_1m < -0.05:
                adjustment += 0.06  # Sector declining, increase risk
            elif sector_data.performance_1m > 0.05:
                adjustment -= 0.04  # Sector growing, decrease risk

        # Economic indicators impact (max +/- 0.06)
        if economic_data:
            # High unemployment increases risk
            if economic_data.unemployment_rate and economic_data.unemployment_rate > 5.0:
                adjustment += 0.03

            # High inflation increases risk
            if economic_data.inflation_rate and economic_data.inflation_rate > 4.0:
                adjustment += 0.02

            # Low consumer confidence increases risk
            if economic_data.consumer_confidence and economic_data.consumer_confidence < 60:
                adjustment += 0.03

        return max(-0.2, min(0.2, adjustment))

    def _generate_summary(
        self,
        company_name: str,
        industry: str,
        sector: str,
        sentiment: float,
        sector_data: Optional[SectorData],
        economic_data: Optional[EconomicIndicators],
        articles: list[NewsArticle]
    ) -> str:
        """Generate a human-readable market summary."""
        parts = []

        # Industry context
        industry_display = industry.replace("_", " ").title()
        parts.append(f"Market analysis for {company_name} in the {industry_display} industry ({sector} sector).")

        # Sentiment summary
        if sentiment > 0.3:
            sentiment_desc = "predominantly positive"
        elif sentiment > 0.1:
            sentiment_desc = "slightly positive"
        elif sentiment > -0.1:
            sentiment_desc = "neutral"
        elif sentiment > -0.3:
            sentiment_desc = "slightly negative"
        else:
            sentiment_desc = "predominantly negative"

        parts.append(f"Recent news sentiment is {sentiment_desc} (score: {sentiment:.2f}).")

        # Sector performance
        if sector_data:
            trend_desc = {
                "bullish": "showing positive momentum",
                "bearish": "under pressure",
                "neutral": "trading sideways"
            }.get(sector_data.trend, "stable")

            parts.append(
                f"The {sector} sector is {trend_desc} "
                f"(1-month: {sector_data.performance_1m*100:+.1f}%, "
                f"YTD: {sector_data.performance_ytd*100:+.1f}%)."
            )

        # Economic context
        if economic_data:
            econ_notes = []
            if economic_data.unemployment_rate:
                econ_notes.append(f"unemployment at {economic_data.unemployment_rate:.1f}%")
            if economic_data.inflation_rate:
                econ_notes.append(f"inflation at {economic_data.inflation_rate:.1f}%")
            if economic_data.interest_rate:
                econ_notes.append(f"interest rates at {economic_data.interest_rate:.2f}%")

            if econ_notes:
                parts.append(f"Economic backdrop: {', '.join(econ_notes)}.")

        # Key headlines
        if articles:
            negative_articles = [a for a in articles if a.sentiment_score < -0.2]
            if negative_articles:
                parts.append(f"Note: {len(negative_articles)} recent article(s) with negative sentiment detected.")

        return " ".join(parts)


# =============================================================================
# Convenience function for quick reports
# =============================================================================

async def get_market_intelligence(
    company_name: str,
    industry: Optional[str] = None,
    description: str = ""
) -> MarketIntelligenceReport:
    """
    Convenience function to get market intelligence report.
    """
    service = MarketIntelligenceService()
    return await service.generate_report(company_name, industry, description)
