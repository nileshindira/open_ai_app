from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List, Optional
import os

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
BASE_URL = os.getenv("BASE_URL", "").rstrip("/")  # set in prod (see README)

def _inline_asset(name: str) -> str:
    """Read an asset by filename from assets/."""
    path = ASSETS_DIR / name
    return path.read_text(encoding="utf-8")

def output_template_html(html_text: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build the `_meta.openai.outputTemplate` payload Apps SDK expects (per examples).
    Returns metadata the ChatGPT client uses to render a widget inline.
    """
    return {
        "openai": {
            "outputTemplate": {
                "html": html_text,
                # This `data` is available to the widget JS to hydrate the UI
                "data": data
            }
        }
    }

def stock_news_carousel_template(data: Dict[str, Any]) -> Dict[str, Any]:
    html = _inline_asset("stock-carousel.html")
    return output_template_html(html, data)

def analysis_carousel_template(data: Dict[str, Any]) -> Dict[str, Any]:
    html = _inline_asset("analysis-carousel.html")
    return output_template_html(html, data)
