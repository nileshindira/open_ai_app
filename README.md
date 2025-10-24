# ChatGPT App: Stocks Carousel (FastMCP + Apps SDK)

This app is a Python FastMCP server exposing two tools:
- `show_stock_news` – renders a 2-card news carousel with action buttons.
- `analyze_stock` – renders a follow-on carousel for either technical or fundamental analysis.

The UI is rendered inline in ChatGPT via the Apps SDK using `_meta.openai/outputTemplate` as shown in the official examples.  
References: OpenAI Apps SDK examples repo and docs.  
(Examples & patterns)  
- GitHub examples: https://github.com/openai/openai-apps-sdk-examples  
- Apps SDK → Examples page: https://developers.openai.com/apps-sdk/build/examples  
- Connect your MCP server from ChatGPT: https://developers.openai.com/apps-sdk/deploy/connect-chatgpt  

## Local dev
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r server/requirements.txt
uvicorn server.main:app --port 8000
