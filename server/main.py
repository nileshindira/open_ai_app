from __future__ import annotations
import os
from typing import Dict, Any, List, Literal, Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi import FastAPI
from fastmcp import FastMCP

from server.widgets import stock_news_carousel_template, analysis_carousel_template

app = FastAPI(title="Stocks Carousel MCP Server")
mcp = FastMCP(app, version="1.0.0")


# ---------- Schemas ----------

class ShowNewsArgs(BaseModel):
    """
    Show a 2-card news carousel with buttons for 'Technical' and 'Fundamental'.
    """
    market: Literal["IN", "US"] = Field(default="IN", description="Market region for dummy context")

class AnalyzeArgs(BaseModel):
    """
    Return a follow-on carousel of dummy analysis based on `mode` for a given symbol.
    """
    symbol: str = Field(..., description="Ticker symbol (e.g., TCS, INFY, AAPL)")
    mode: Literal["technical", "fundamental"] = Field(..., description="Analysis type")

# ---------- Fake data ----------

def _dummy_news(market: str) -> List[Dict[str, Any]]:
    # two cards only, as requested
    if market == "US":
        return [
            {
                "symbol": "AAPL",
                "headline": "Apple unveils AI features; services revenue climbs",
                "summary": "Investors weigh margin impact vs ecosystem lock-in.",
                "image": "https://placehold.co/600x340?text=AAPL",
            },
            {
                "symbol": "NVDA",
                "headline": "NVIDIA announces next-gen accelerator roadmap",
                "summary": "Hyperscalers guide continued capex strength.",
                "image": "https://placehold.co/600x340?text=NVDA",
            },
        ]
    # default IN
    return [
        {
            "symbol": "TCS",
            "headline": "TCS wins large banking transformation deal",
            "summary": "Deal pipeline commentary turns positive QoQ.",
            "image": "https://placehold.co/600x340?text=TCS",
        },
        {
            "symbol": "RELIANCE",
            "headline": "Reliance Retail expands premium format footprint",
            "summary": "O2C stable; retail + Jio drive growth.",
            "image": "https://placehold.co/600x340?text=RELIANCE",
        },
    ]

def _dummy_technical(symbol: str) -> List[Dict[str, Any]]:
    return [
        {"title": f"{symbol}: Trend", "subtitle": "Higher highs, EMA(50)>EMA(200)", "image": "https://placehold.co/600x340?text=Trend"},
        {"title": f"{symbol}: Momentum", "subtitle": "RSI 62, MACD > 0, ADX 24", "image": "https://placehold.co/600x340?text=Momentum"},
        {"title": f"{symbol}: Levels", "subtitle": "S/R: 1480 / 1545 / 1600", "image": "https://placehold.co/600x340?text=Levels"},
    ]

def _dummy_fundamental(symbol: str) -> List[Dict[str, Any]]:
    return [
        {"title": f"{symbol}: Valuation", "subtitle": "PE 26x vs sector 24x; EV/EBITDA 13x", "image": "https://placehold.co/600x340?text=Valuation"},
        {"title": f"{symbol}: Growth", "subtitle": "3Y CAGR: Rev 12%, EPS 15%", "image": "https://placehold.co/600x340?text=Growth"},
        {"title": f"{symbol}: Quality", "subtitle": "ROCE 21%, FCF yield 3.1%", "image": "https://placehold.co/600x340?text=Quality"},
    ]

# ---------- Tools ----------

@mcp.tool("show_stock_news", description="Show two stock news items as a carousel with action buttons.")
def show_stock_news(args: ShowNewsArgs) -> Dict[str, Any]:
    cards = _dummy_news(args.market)
    # Widget data understood by our HTML/JS to render buttons
    widget_data = {
        "heading": "Today’s Stock Highlights",
        "cards": [
            {
                "image": c["image"],
                "title": f"{c['symbol']}: {c['headline']}",
                "subtitle": c["summary"],
                # Button config tells ChatGPT+Apps SDK what follow-up tool to call
                "actions": [
                    {"label": "Technical analysis", "tool": "analyze_stock", "args": {"symbol": c["symbol"], "mode": "technical"}},
                    {"label": "Fundamental analysis", "tool": "analyze_stock", "args": {"symbol": c["symbol"], "mode": "fundamental"}},
                ],
            }
            for c in cards
        ],
    }

    meta = {"_meta": stock_news_carousel_template(widget_data)}
    # Plain content + structured result (good practice from examples)
    return {
        "content": [
            {"type": "text", "text": "Here are two stock headlines. Pick an analysis to continue."},
            {"type": "json", "data": {"cards": cards}},
        ],
        **meta
    }

@mcp.tool("analyze_stock", description="Return a carousel with dummy technical or fundamental analysis for a symbol.")
def analyze_stock(args: AnalyzeArgs) -> Dict[str, Any]:
    cards = _dummy_technical(args.symbol) if args.mode == "technical" else _dummy_fundamental(args.symbol)
    widget_data = {
        "heading": f"{args.symbol} — {args.mode.capitalize()} view",
        "cards": [
            {
                "image": c["image"],
                "title": c["title"],
                "subtitle": c["subtitle"],
                # You could add next-step actions here as well (e.g., 'Open chart', 'Compare peers')
                "actions": []
            } for c in cards
        ],
        "back": {"label": "⬅️ Back to news", "tool": "show_stock_news", "args": {"market": "IN"}}
    }
    meta = {"_meta": analysis_carousel_template(widget_data)}
    return {
        "content": [
            {"type": "text", "text": f"Showing {args.mode} analysis for {args.symbol} (dummy)."},
            {"type": "json", "data": {"mode": args.mode, "symbol": args.symbol}},
        ],
        **meta
    }

# Optional health check
@app.get("/")
def home():
    return {"status": "ok", "name": "stocks_carousel_mcp", "version": "1.0.0"}
