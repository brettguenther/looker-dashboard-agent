"""Looker Managed MCP Client (JSON-RPC over HTTP)."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
import requests

from looker_builder.config import LookerProfile, load_profile


class LookerMCPClient:
    """Client for interacting with Looker-Managed MCP Server."""

    def __init__(self, profile: Optional[LookerProfile] = None):
        self.profile = profile or load_profile()
        self._request_id = 0

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def _post_jsonrpc(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = self.profile.mcp_url
        headers = self.profile.get_auth_headers()
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params or {},
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 401:
            self.profile.refresh_session_if_needed()
            headers = self.profile.get_auth_headers()
            resp = requests.post(url, headers=headers, json=payload, timeout=30)

        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            err = data["error"]
            raise RuntimeError(f"MCP Error ({err.get('code')}): {err.get('message')}")
        return data.get("result", {})

    def initialize(self) -> Dict[str, Any]:
        """Perform MCP initialize handshake."""
        return self._post_jsonrpc(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "looker-dashboard-builder-agent", "version": "0.1.0"},
            },
        )

    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools exposed by the Looker MCP server."""
        res = self._post_jsonrpc("tools/list", {})
        return res.get("tools", [])

    def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> List[Any]:
        """Call an MCP tool and return parsed items."""
        res = self._post_jsonrpc("tools/call", {"name": name, "arguments": arguments or {}})
        if res.get("isError"):
            err_msg = ""
            for item in res.get("content", []):
                err_msg += item.get("text", "")
            raise RuntimeError(f"Looker MCP tool '{name}' failed: {err_msg}")

        contents = res.get("content", [])
        parsed_results: List[Any] = []
        for item in contents:
            if item.get("type") == "text":
                text = item.get("text", "")
                try:
                    parsed = json.loads(text)
                    parsed_results.append(parsed)
                except Exception:
                    parsed_results.append(text)
            else:
                parsed_results.append(item)
        return parsed_results

    def get_models(self) -> List[Dict[str, Any]]:
        """List available LookML models."""
        return self.call_tool("get_models")

    def get_explores(self, model: str) -> List[Dict[str, Any]]:
        """List explores in a model."""
        return self.call_tool("get_explores", {"model": model})

    def get_dimensions(self, model: str, explore: str) -> List[Dict[str, Any]]:
        """List dimensions for an explore."""
        return self.call_tool("get_dimensions", {"model": model, "explore": explore})

    def get_measures(self, model: str, explore: str) -> List[Dict[str, Any]]:
        """List measures for an explore."""
        return self.call_tool("get_measures", {"model": model, "explore": explore})

    def get_filters(self, model: str, explore: str) -> List[Dict[str, Any]]:
        """List filter-only fields for an explore."""
        return self.call_tool("get_filters", {"model": model, "explore": explore})

    def get_parameters(self, model: str, explore: str) -> List[Dict[str, Any]]:
        """List parameters for an explore."""
        return self.call_tool("get_parameters", {"model": model, "explore": explore})

    def get_explore_metadata(self, model: str, explore: str) -> Dict[str, Any]:
        """Retrieve full metadata for an explore (dimensions, measures, filters)."""
        dims = self.get_dimensions(model, explore)
        meas = self.get_measures(model, explore)
        filters = self.get_filters(model, explore)
        params = self.get_parameters(model, explore)
        return {
            "model": model,
            "explore": explore,
            "dimensions": dims,
            "measures": meas,
            "filters": filters,
            "parameters": params,
        }

    def query(
        self,
        model: str,
        explore: str,
        fields: List[str],
        filters: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[str]] = None,
        limit: Optional[int] = 5,
    ) -> List[Any]:
        """Execute a query via Looker MCP."""
        args: Dict[str, Any] = {
            "model": model,
            "explore": explore,
            "fields": fields,
        }
        if filters:
            args["filters"] = filters
        if sorts:
            args["sorts"] = sorts
        if limit is not None:
            try:
                args["limit"] = int(limit)
            except Exception:
                args["limit"] = 5
        return self.call_tool("query", args)
