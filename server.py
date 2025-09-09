import os
import sys
print("Python executable:", sys.executable)
print("sys.path:", sys.path)
import json
from typing import Optional, List, Dict, Any

import httpx
from fastapi import FastAPI
from dotenv import load_dotenv

from mcp.server import Server

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
    raise RuntimeError("Missing GOOGLE_API_KEY or GOOGLE_CSE_ID in environment.")

# Create the MCP server
mcp = Server("google-search-mcp")

# Register a single tool: google.search
async def google_search(
    query: str,
    num: int = 5,
    start: int = 1,
    safe: str = "off",
    lr: Optional[str] = None,
    gl: Optional[str] = None,
    cr: Optional[str] = None,
    siteSearch: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Calls Google Custom Search API and returns a compact JSON with results.
    """
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": num,
        "start": start,
        "safe": safe,
    }
    if lr: params["lr"] = lr
    if gl: params["gl"] = gl
    if cr: params["cr"] = cr
    if siteSearch: params["siteSearch"] = siteSearch

    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get("https://www.googleapis.com/customsearch/v1", params=params)
        r.raise_for_status()
        data = r.json()

    items = data.get("items", [])
    results = [
        {
            "title": it.get("title"),
            "link": it.get("link"),
            "snippet": it.get("snippet"),
            "displayLink": it.get("displayLink"),
        }
        for it in items
    ]

    return {
        "query": query,
        "totalResults": int(data.get("searchInformation", {}).get("totalResults", 0)),
        "results": results,
        "nextStart": (start + num) if len(results) == num else None
    }

# Wire the MCP server into FastAPI (HTTP transport)
app = FastAPI(title="Google Search MCP Server")

# Optional health check route
@app.get("/")
def health():
    return {"ok": True, "server": "google-search-mcp"}

# Expose google_search via FastAPI POST
@app.post("/google-search")
async def google_search_api(payload: dict):
    return await google_search(**payload)
