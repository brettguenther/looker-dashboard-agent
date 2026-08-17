"""ADK-Powered Autonomous Looker Dashboard Architect (Google Agent Development Kit)."""

from __future__ import annotations

import asyncio
import os
from typing import Any, Dict, List, Optional

from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import InMemoryRunner
from google.adk.tools.function_tool import FunctionTool

from looker_builder.config import LookerProfile, load_profile
from looker_builder.generator import LookMLDashboardGenerator
from looker_builder.importer import LookerDashboardImporter
from looker_builder.mcp_client import LookerMCPClient
from looker_builder.verifier import DashboardVerifier


class ADKLookerDashboardAgent:
    """Autonomous Agent powered by Google ADK to discover schemas, design, verify, and deploy Looker dashboards."""

    def __init__(
        self,
        profile_name: Optional[str] = None,
        project_id: Optional[str] = None,
        model_name: str = "gemini-2.5-flash",
    ):
        self.profile: LookerProfile = load_profile(profile_name)
        self.mcp_client = LookerMCPClient(self.profile)
        self.importer = LookerDashboardImporter(self.profile)
        self.generator = LookMLDashboardGenerator(project_id=project_id)
        self.verifier = DashboardVerifier(self.mcp_client)
        self.model_name = model_name

        # Ensure Vertex AI environment variables are active for Google ADK
        gcp_project = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT") or "stellar-cumulus-449523-b8"
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
        os.environ["GOOGLE_CLOUD_PROJECT"] = gcp_project
        os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

        # 1. Register ADK Function Tools
        self.tools = [
            FunctionTool(self.tool_list_available_models),
            FunctionTool(self.tool_list_explores_in_model),
            FunctionTool(self.tool_inspect_explore_schema),
            FunctionTool(self.tool_generate_lookml_dashboard),
            FunctionTool(self.tool_verify_dashboard_queries),
            FunctionTool(self.tool_import_dashboard_lookml),
        ]

        # 2. Initialize ADK LlmAgent
        self.agent = LlmAgent(
            name="autonomous_looker_architect",
            model=self.model_name,
            instruction="""You are an expert autonomous Looker BI Architect powered by Google ADK.
Your goal is to satisfy the user's high-level business request by discovering models,
inspecting explores, selecting the optimal schema, generating production LookML YAML,
verifying all queries against Looker, and deploying the dashboard.
Follow these steps:
1. Call tool_list_available_models to see what datasets exist.
2. Call tool_list_explores_in_model for the most relevant model.
3. Call tool_inspect_explore_schema for the selected explore.
4. Call tool_generate_lookml_dashboard with a comprehensive prompt.
5. Call tool_verify_dashboard_queries to test all query tiles live against Looker.
6. Once verified, call tool_import_dashboard_lookml to make it live in Looker.""",
            tools=self.tools,
        )
        self.runner = InMemoryRunner(agent=self.agent)

    def tool_list_available_models(self) -> List[Dict[str, Any]]:
        """Get all available LookML models from Looker MCP."""
        models = self.mcp_client.get_models()
        return [{"name": m.get("name"), "label": m.get("label")} for m in models]

    def tool_list_explores_in_model(self, model_name: str) -> List[Dict[str, Any]]:
        """Get explores for a specific model from Looker MCP."""
        explores = self.mcp_client.get_explores(model_name)
        return [{"name": e.get("name"), "label": e.get("label")} for e in explores]

    def tool_inspect_explore_schema(self, model_name: str, explore_name: str) -> Dict[str, Any]:
        """Get dimensions, measures, and filters for a Looker explore."""
        meta = self.mcp_client.get_explore_metadata(model_name, explore_name)
        return {
            "model": model_name,
            "explore": explore_name,
            "measures": [{"name": m.get("name"), "type": m.get("type"), "label": m.get("label")} for m in meta.get("measures", [])],
            "dimensions": [{"name": d.get("name"), "type": d.get("type"), "label": d.get("label")} for d in meta.get("dimensions", [])[:25]],
        }

    def tool_generate_lookml_dashboard(
        self,
        prompt: str,
        model_name: str,
        explore_name: str,
        title: str,
        preferred_slug: Optional[str] = None,
    ) -> str:
        """Generate complete, verified LookML dashboard YAML."""
        meta = self.mcp_client.get_explore_metadata(model_name, explore_name)
        return self.generator.generate(
            prompt=prompt,
            explore_metadata=meta,
            dashboard_title=title,
            preferred_slug=preferred_slug,
        )

    def tool_verify_dashboard_queries(self, lookml_yaml: str) -> Dict[str, Any]:
        """Execute live queries for all tiles in LookML YAML against Looker MCP."""
        report = self.verifier.verify_lookml(lookml_yaml)
        return {
            "all_passed": report.all_passed,
            "passed_count": report.passed_elements,
            "total_count": report.query_elements,
            "results": [
                {
                    "element": r.element_name,
                    "title": r.element_title,
                    "type": r.element_type,
                    "passed": r.passed,
                    "error": r.error_message,
                    "latency_ms": r.latency_ms,
                }
                for r in report.results
            ],
        }

    def tool_import_dashboard_lookml(
        self,
        lookml_yaml: str,
        folder_id: Optional[str] = None,
        preferred_slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Import verified LookML YAML into Looker via Looker REST API."""
        res = self.importer.import_lookml(lookml_yaml, folder_id=folder_id, preferred_slug=preferred_slug)
        return {
            "id": res.id,
            "title": res.title,
            "slug": res.slug,
            "url": res.url,
            "folder_id": res.folder_id,
        }

    async def run_goal_async(self, goal_prompt: str) -> List[Any]:
        """Run an autonomous open-ended goal using ADK Runner."""
        return await self.runner.run_debug(goal_prompt, verbose=True)

    def run_goal(self, goal_prompt: str) -> List[Any]:
        """Synchronous wrapper for running an autonomous ADK goal."""
        return asyncio.run(self.run_goal_async(goal_prompt))
