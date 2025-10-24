"""
ChatGPT Tools MCP Server implemented with the Python FastMCP helper.
"""

from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, List

import pandas as pd
import mcp.types as types
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, ValidationError
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware

# ---------------------------------------------------------------------
# Tool Metadata
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class ChatGPTTool:
    name: str
    title: str
    description: str
    input_schema: Dict[str, Any]
    read_only: bool
    open_world: bool


TOOLS: List[ChatGPTTool] = [
    ChatGPTTool(
        name="calculate_sum",
        title="Calculate Sum",
        description="Add two numbers together.",
        input_schema={
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"},
            },
            "required": ["a", "b"],
            "additionalProperties": False,
        },
        read_only=True,
        open_world=False,
    ),
    ChatGPTTool(
        name="analyze_csv",
        title="Analyze CSV",
        description="Analyze a CSV file for operations such as sum, average, and count.",
        input_schema={
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Path to the CSV file"},
                "operations": {
                    "type": "array",
                    "items": {"enum": ["sum", "average", "count"]},
                },
            },
            "required": ["filepath", "operations"],
            "additionalProperties": False,
        },
        read_only=False,
        open_world=False,
    ),
]

TOOLS_BY_NAME: Dict[str, ChatGPTTool] = {t.name: t for t in TOOLS}

# ---------------------------------------------------------------------
# Input Schemas
# ---------------------------------------------------------------------

class CalculateSumInput(BaseModel):
    a: float
    b: float
    model_config = ConfigDict(extra="forbid")


class AnalyzeCSVInput(BaseModel):
    filepath: str
    operations: List[str]
    model_config = ConfigDict(extra="forbid")

# ---------------------------------------------------------------------
# MCP Setup
# ---------------------------------------------------------------------

mcp = FastMCP(
    name="chatgpt-tools-python",
    sse_path="/mcp",
    message_path="/mcp/messages",
    stateless_http=True,
)


def _tool_meta(tool: ChatGPTTool) -> Dict[str, Any]:
    return {
        "annotations": {
            "destructiveHint": not tool.read_only,
            "openWorldHint": tool.open_world,
            "readOnlyHint": tool.read_only,
        },
        "openai/resultCanProduceWidget": False,
    }

# ---------------------------------------------------------------------
# MCP Tool Handlers
# ---------------------------------------------------------------------

@mcp._mcp_server.list_tools()
async def _list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name=tool.name,
            title=tool.title,
            description=tool.description,
            inputSchema=deepcopy(tool.input_schema),
            _meta=_tool_meta(tool),
        )
        for tool in TOOLS
    ]


async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
    """Invoke a tool."""
    tool = TOOLS_BY_NAME.get(req.params.name)
    if not tool:
        return types.ServerResult(
            types.CallToolResult(
                content=[types.TextContent(type="text", text=f"Unknown tool: {req.params.name}")],
                isError=True,
            )
        )

    try:
        if tool.name == "calculate_sum":
            payload = CalculateSumInput.model_validate(req.params.arguments)
            result = payload.a + payload.b
            return types.ServerResult(
                types.CallToolResult(
                    content=[types.TextContent(type="text", text=f"Result: {result}")],
                    structuredContent={"a": payload.a, "b": payload.b, "sum": result},
                    _meta=_tool_meta(tool),
                )
            )

        elif tool.name == "analyze_csv":
            payload = AnalyzeCSVInput.model_validate(req.params.arguments)
            df = pd.read_csv(payload.filepath)
            summary = {}
            if "sum" in payload.operations:
                summary["sum"] = df.sum(numeric_only=True).to_dict()
            if "average" in payload.operations:
                summary["average"] = df.mean(numeric_only=True).to_dict()
            if "count" in payload.operations:
                summary["count"] = len(df)
            return types.ServerResult(
                types.CallToolResult(
                    content=[types.TextContent(type="text", text=str(summary))],
                    structuredContent=summary,
                    _meta=_tool_meta(tool),
                )
            )
    except ValidationError as exc:
        return types.ServerResult(
            types.CallToolResult(
                content=[types.TextContent(type="text", text=f"Validation error: {exc.errors()}")],
                isError=True,
            )
        )
    except Exception as e:
        return types.ServerResult(
            types.CallToolResult(
                content=[types.TextContent(type="text", text=f"Error: {str(e)}")],
                isError=True,
            )
        )


mcp._mcp_server.request_handlers[types.CallToolRequest] = _call_tool_request

# ---------------------------------------------------------------------
# HTTP Application
# ---------------------------------------------------------------------

# Create a FastAPI app and mount MCP’s Starlette app under /mcp
base_app = mcp.streamable_http_app()
app = FastAPI(title="ChatGPT Tools MCP Server")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Health endpoint."""
    return HTMLResponse(
        "<h3>✅ ChatGPT Tools MCP Server is running.<br>"
        "Endpoints: <code>/mcp</code> and <code>/mcp/messages</code>.</h3>"
    )

# Mount the MCP Starlette app inside FastAPI
app.mount("/mcp", base_app)

# Allow ChatGPT’s sandbox to reach it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=3000)
