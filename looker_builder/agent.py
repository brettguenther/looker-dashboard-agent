"""Looker Dashboard Builder Agent with ADK Support and Query Verification Loop."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from looker_builder.config import LookerProfile, load_profile
from looker_builder.generator import LookMLDashboardGenerator
from looker_builder.importer import ImportedDashboardResult, LookerDashboardImporter
from looker_builder.mcp_client import LookerMCPClient
from looker_builder.verifier import DashboardVerificationReport, DashboardVerifier


@dataclass
class BuildDashboardResult:
    dashboard_id: str
    dashboard_title: str
    dashboard_slug: str
    dashboard_url: str
    lookml_yaml: str
    verification_report: Optional[DashboardVerificationReport] = None
    folder_id: Optional[str] = None
    folder_name: Optional[str] = None


class LookerDashboardAgent:
    """End-to-End Agent that discovers MCP metadata, generates LookML, verifies query elements, and imports dashboards."""

    def __init__(
        self,
        profile_name: Optional[str] = None,
        project_id: Optional[str] = None,
        skills_dir: Optional[str] = None,
    ):
        self.profile: LookerProfile = load_profile(profile_name)
        self.mcp_client = LookerMCPClient(self.profile)
        self.importer = LookerDashboardImporter(self.profile)
        self.generator = LookMLDashboardGenerator(project_id=project_id, skills_dir=skills_dir)
        self.verifier = DashboardVerifier(self.mcp_client)

    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Looker MCP and API."""
        init_res = self.mcp_client.initialize()
        tools = self.mcp_client.list_tools()
        models = self.mcp_client.get_models()
        return {
            "status": "connected",
            "profile": self.profile.name,
            "host": self.profile.host,
            "mcp_url": self.profile.mcp_url,
            "server_info": init_res.get("serverInfo", {}),
            "tool_count": len(tools),
            "available_models": [m.get("name") for m in models],
        }

    def get_models(self) -> List[Dict[str, Any]]:
        """List all available LookML models."""
        return self.mcp_client.get_models()

    def get_explores(self, model: str) -> List[Dict[str, Any]]:
        """List explores in a model."""
        return self.mcp_client.get_explores(model)

    def get_explore_fields(self, model: str, explore: str) -> Dict[str, Any]:
        """Get dimensions, measures, and filters for an explore."""
        return self.mcp_client.get_explore_metadata(model, explore)

    def verify_lookml(self, lookml_yaml: str) -> DashboardVerificationReport:
        """Verify each query element in a LookML dashboard against Looker MCP."""
        return self.verifier.verify_lookml(lookml_yaml)

    def build_and_import_dashboard(
        self,
        prompt: str,
        model: Optional[str] = None,
        explore: Optional[str] = None,
        title: Optional[str] = None,
        folder_id: Optional[str] = None,
        preferred_slug: Optional[str] = None,
        llm_model: Optional[str] = None,
        verify_queries: bool = True,
        use_llm: bool = True,
    ) -> BuildDashboardResult:
        """Create a dashboard from a prompt, verify query elements, and import into Looker."""
        # 1. Resolve Model and Explore
        if not model or not explore:
            models = self.mcp_client.get_models()
            if not models:
                raise ValueError("No models found in Looker instance.")
            if not model:
                model = models[0].get("name")
            explores = self.mcp_client.get_explores(model)
            if not explores:
                raise ValueError(f"No explores found for model '{model}'.")
            if not explore:
                explore = explores[0].get("name")

        # 2. Fetch Explore Metadata from Looker Managed MCP
        metadata = self.mcp_client.get_explore_metadata(model, explore)

        # 3. Generate Initial LookML Dashboard YAML
        if use_llm:
            lookml_yaml = self.generator.generate(
                prompt=prompt,
                explore_metadata=metadata,
                dashboard_title=title,
                preferred_slug=preferred_slug,
                model_name=llm_model,
            )
        else:
            lookml_yaml = self.generator.generate_template(
                explore_metadata=metadata,
                title=title or "Automated Looker Dashboard",
                preferred_slug=preferred_slug,
            )

        # 4. Query Element Verification Loop (Auto-Remediation)
        verification_report = None
        if verify_queries:
            lookml_yaml, verification_report = self.verifier.verify_and_remediate(
                lookml_yaml=lookml_yaml,
                prompt=prompt,
                explore_metadata=metadata,
                generator=self.generator,
                preferred_slug=preferred_slug,
                max_retries=2,
            )

        # 5. Import Dashboard into Looker via import_dashboard_from_lookml API
        import_res: ImportedDashboardResult = self.importer.import_lookml(
            lookml_yaml=lookml_yaml,
            folder_id=folder_id,
            preferred_slug=preferred_slug,
        )

        return BuildDashboardResult(
            dashboard_id=import_res.id,
            dashboard_title=import_res.title,
            dashboard_slug=import_res.slug,
            dashboard_url=import_res.url,
            lookml_yaml=lookml_yaml,
            verification_report=verification_report,
            folder_id=import_res.folder_id,
            folder_name=import_res.folder_name,
        )

    def edit_and_update_dashboard(
        self,
        preferred_slug: str,
        edit_instructions: str,
        current_lookml: Optional[str] = None,
        model: Optional[str] = None,
        explore: Optional[str] = None,
        llm_model: Optional[str] = None,
        verify_queries: bool = True,
    ) -> BuildDashboardResult:
        """Edit an existing Looker dashboard in-place, verify queries, and update Looker."""
        if not model or not explore:
            models = self.mcp_client.get_models()
            if not model:
                model = models[0]["name"] if models else "basic_ecomm"
            explores = self.mcp_client.get_explores(model)
            if not explore:
                explore = explores[0]["name"] if explores else "basic_order_items"

        metadata = self.mcp_client.get_explore_metadata(model, explore)

        if not current_lookml:
            lookml_yaml = self.generator.generate(
                prompt=edit_instructions,
                explore_metadata=metadata,
                preferred_slug=preferred_slug,
                model_name=llm_model,
            )
        else:
            lookml_yaml = self.generator.generate_edit(
                current_lookml=current_lookml,
                edit_instructions=edit_instructions,
                explore_metadata=metadata,
                preferred_slug=preferred_slug,
                model_name=llm_model,
            )

        verification_report = None
        if verify_queries:
            lookml_yaml, verification_report = self.verifier.verify_and_remediate(
                lookml_yaml=lookml_yaml,
                prompt=edit_instructions,
                explore_metadata=metadata,
                generator=self.generator,
                preferred_slug=preferred_slug,
                max_retries=2,
            )

        import_res = self.importer.import_lookml(
            lookml_yaml=lookml_yaml,
            preferred_slug=preferred_slug,
        )

        return BuildDashboardResult(
            dashboard_id=import_res.id,
            dashboard_title=import_res.title,
            dashboard_slug=import_res.slug,
            dashboard_url=import_res.url,
            lookml_yaml=lookml_yaml,
            verification_report=verification_report,
            folder_id=import_res.folder_id,
            folder_name=import_res.folder_name,
        )
