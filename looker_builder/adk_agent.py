"""ADK-Powered Looker Dashboard Builder Agent (Google Agent Development Kit)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import yaml

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.function_tool import FunctionTool

from looker_builder.config import LookerProfile, load_profile
from looker_builder.generator import LookMLDashboardGenerator
from looker_builder.importer import LookerDashboardImporter
from looker_builder.mcp_client import LookerMCPClient
from looker_builder.verifier import DashboardVerifier


class ADKLookerDashboardAgent:
    """Agent implemented using Google ADK (Agent Development Kit) to orchestrate control flow."""

    def __init__(
        self,
        profile_name: Optional[str] = None,
        project_id: Optional[str] = None,
    ):
        self.profile: LookerProfile = load_profile(profile_name)
        self.mcp_client = LookerMCPClient(self.profile)
        self.importer = LookerDashboardImporter(self.profile)
        self.generator = LookMLDashboardGenerator(project_id=project_id)
        self.verifier = DashboardVerifier(self.mcp_client)

        # 1. Register ADK Tools
        self.tools = [
            FunctionTool(self.tool_get_models),
            FunctionTool(self.tool_get_explores),
            FunctionTool(self.tool_get_explore_schema),
            FunctionTool(self.tool_verify_dashboard_queries),
            FunctionTool(self.tool_import_dashboard_lookml),
        ]

        # 2. Initialize ADK LlmAgent
        self.adk_agent = LlmAgent(
            name="looker_lookml_dashboard_architect",
            description="Agent that inspects Looker models, designs LookML dashboards, verifies query elements, and imports them in-place.",
            tools=self.tools,
            instruction="You are an autonomous Looker Dashboard Architect. Use the provided tools to inspect schemas, verify tile queries against Looker, and import dashboards.",
        )

    def tool_get_models(self) -> List[Dict[str, Any]]:
        """Get all available LookML models from Looker MCP."""
        return self.mcp_client.get_models()

    def tool_get_explores(self, model: str) -> List[Dict[str, Any]]:
        """Get explores for a specific model from Looker MCP."""
        return self.mcp_client.get_explores(model)

    def tool_get_explore_schema(self, model: str, explore: str) -> Dict[str, Any]:
        """Get dimensions and measures for a Looker explore."""
        return self.mcp_client.get_explore_metadata(model, explore)

    def tool_verify_dashboard_queries(self, lookml_yaml: str) -> Dict[str, Any]:
        """Execute queries for all tiles in LookML YAML against Looker MCP to verify validity."""
        report = self.verifier.verify_lookml(lookml_yaml)
        return {
            "all_passed": report.all_passed,
            "passed_elements": report.passed_elements,
            "failed_elements": report.failed_elements,
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

    def execute_workflow(
        self,
        prompt: str,
        model: Optional[str] = None,
        explore: Optional[str] = None,
        title: Optional[str] = None,
        preferred_slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Orchestrates the complete ADK control flow."""
        # Step 1: Schema Discovery Tool
        if not model:
            models = self.tool_get_models()
            if not models:
                raise ValueError("No models found in Looker instance.")
            model = models[0].get("name")
        if not explore:
            explores = self.tool_get_explores(model)
            if not explores:
                raise ValueError(f"No explores found for model '{model}'.")
            explore = explores[0].get("name")

        metadata = self.tool_get_explore_schema(model, explore)

        # Step 2: Grounded Synthesis
        lookml_yaml = self.generator.generate(
            prompt=prompt,
            explore_metadata=metadata,
            dashboard_title=title,
            preferred_slug=preferred_slug,
        )

        # Step 3: Verification Tool Loop (Auto-Remediation)
        lookml_yaml, report = self.verifier.verify_and_remediate(
            lookml_yaml=lookml_yaml,
            prompt=prompt,
            explore_metadata=metadata,
            generator=self.generator,
            preferred_slug=preferred_slug,
            max_retries=2,
        )

        # Step 4: Import Tool
        import_result = self.tool_import_dashboard_lookml(
            lookml_yaml=lookml_yaml,
            preferred_slug=preferred_slug,
        )

        return {
            "dashboard_id": import_result["id"],
            "title": import_result["title"],
            "slug": import_result["slug"],
            "url": import_result["url"],
            "verification_report": report,
            "lookml_yaml": lookml_yaml,
        }
