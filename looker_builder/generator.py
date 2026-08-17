"""Multi-Model LookML Dashboard Generator supporting Gemini and Anthropic Claude."""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional
import yaml

from looker_builder.skills_loader import LookMLSkillsKnowledgeBase


class LookMLDashboardGenerator:
    """Generates LookML dashboards dynamically using Vertex AI Gemini or Anthropic Claude."""

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        skills_dir: Optional[str] = None,
    ):
        self.project_id = (
            project_id
            or os.environ.get("VERTEXAI_PROJECT")
            or os.environ.get("GOOGLE_CLOUD_PROJECT")
        )
        self.location = location or os.environ.get("VERTEXAI_LOCATION", "global")
        self.knowledge_base = LookMLSkillsKnowledgeBase(skills_dir)
        self._system_prompt = self.knowledge_base.compile_full_system_prompt()
        self._gemini_client = None
        self._anthropic_vertex_client = None
        self._anthropic_direct_client = None

    @property
    def loaded_skills_summary(self) -> Dict[str, int]:
        return self.knowledge_base.get_summary()

    def _get_gemini_client(self):
        if self._gemini_client is None:
            try:
                from google import genai
                self._gemini_client = genai.Client(
                    vertexai=True,
                    project=self.project_id,
                    location=self.location,
                )
            except Exception:
                import vertexai
                vertexai.init(project=self.project_id, location=self.location)
                self._gemini_client = "vertexai_sdk"
        return self._gemini_client

    def _get_anthropic_client(self, region: Optional[str] = None):
        """Resolves Anthropic client (Vertex AI Model Garden or Direct API)."""
        target_region = region or os.environ.get("ANTHROPIC_VERTEX_REGION", "us-east5")
        try:
            from anthropic import AnthropicVertex
            return AnthropicVertex(region=target_region, project_id=self.project_id)
        except Exception:
            from anthropic import Anthropic
            return Anthropic()

    def generate(
        self,
        prompt: str,
        explore_metadata: Dict[str, Any],
        dashboard_title: Optional[str] = None,
        preferred_slug: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> str:
        """Generate LookML dashboard YAML using specified dynamic model (Gemini or Claude)."""
        target_model = (
            model_name
            or os.environ.get("LOOKER_BUILDER_LLM_MODEL")
            or "gemini-3.6-flash"
        )
        model = explore_metadata["model"]
        explore = explore_metadata["explore"]
        dimensions = explore_metadata.get("dimensions", [])
        measures = explore_metadata.get("measures", [])
        filters = explore_metadata.get("filters", [])
        parameters = explore_metadata.get("parameters", [])

        dim_list = [f"  - {d.get('name')} (type: {d.get('type')}, label: \"{d.get('label')}\")" for d in dimensions]
        meas_list = [f"  - {m.get('name')} (type: {m.get('type')}, label: \"{m.get('label')}\")" for m in measures]
        filter_list = [f"  - {f.get('name')} (label: \"{f.get('label')}\")" for f in filters] if filters else []
        param_list = [f"  - {p.get('name')} (label: \"{p.get('label')}\")" for p in parameters] if parameters else []

        user_content = f"""USER DASHBOARD REQUEST:
{prompt}

CONTEXT & SCHEMA:
- LookML Model: {model}
- LookML Explore: {explore}
- Proposed Title: {dashboard_title or 'Auto-generated'}
{f'- Preferred Slug (for in-place update): {preferred_slug}' if preferred_slug else ''}

VERIFIED EXPLORE FIELDS (from Looker Managed MCP):
=== MEASURES ({len(measures)}) ===
{chr(10).join(meas_list) if meas_list else '  (None)'}

=== DIMENSIONS ({len(dimensions)}) ===
{chr(10).join(dim_list) if dim_list else '  (None)'}
"""
        if filter_list:
            user_content += f"\n=== FILTER-ONLY FIELDS ===\n{chr(10).join(filter_list)}\n"
        if param_list:
            user_content += f"\n=== PARAMETERS ===\n{chr(10).join(param_list)}\n"

        if preferred_slug:
            user_content += f"\nIMPORTANT: Set `preferred_slug: \"{preferred_slug}\"` under the top-level `- dashboard:` declaration."

        user_content += "\nGenerate the complete, production-ready LookML Dashboard YAML for this request. Strictly follow all layout, element, table calculation, and filter listener specifications from the system instructions."

        raw_text = self._call_model(target_model, user_content)

        yaml_content = self._extract_yaml(raw_text)
        if preferred_slug and "preferred_slug:" not in yaml_content:
            from looker_builder.importer import inject_preferred_slug
            yaml_content = inject_preferred_slug(yaml_content, preferred_slug)

        self._validate_yaml(yaml_content)
        return yaml_content

    def generate_edit(
        self,
        current_lookml: str,
        edit_instructions: str,
        explore_metadata: Dict[str, Any],
        preferred_slug: str,
        model_name: Optional[str] = None,
    ) -> str:
        """Modify an existing LookML dashboard YAML based on user edit instructions."""
        target_model = (
            model_name
            or os.environ.get("LOOKER_BUILDER_LLM_MODEL")
            or "gemini-3.6-flash"
        )
        model = explore_metadata["model"]
        explore = explore_metadata["explore"]
        dimensions = explore_metadata.get("dimensions", [])
        measures = explore_metadata.get("measures", [])

        dim_list = [f"  - {d.get('name')} (type: {d.get('type')}, label: \"{d.get('label')}\")" for d in dimensions]
        meas_list = [f"  - {m.get('name')} (type: {m.get('type')}, label: \"{m.get('label')}\")" for m in measures]

        user_content = f"""USER EDIT INSTRUCTIONS:
{edit_instructions}

CURRENT LOOKML DASHBOARD TO MODIFY:
```yaml
{current_lookml}
```

CONTEXT & SCHEMA:
- LookML Model: {model}
- LookML Explore: {explore}
- Required Preferred Slug: {preferred_slug}

VERIFIED EXPLORE FIELDS:
=== MEASURES ===
{chr(10).join(meas_list)}

=== DIMENSIONS ===
{chr(10).join(dim_list)}

Apply the requested modifications to the dashboard. Preserve the newspaper layout, existing functional tiles (unless asked to change), and ensure `preferred_slug: "{preferred_slug}"` remains set under `- dashboard:`. Output the complete updated LookML YAML."""

        raw_text = self._call_model(target_model, user_content)

        yaml_content = self._extract_yaml(raw_text)
        from looker_builder.importer import inject_preferred_slug
        yaml_content = inject_preferred_slug(yaml_content, preferred_slug)
        self._validate_yaml(yaml_content)
        return yaml_content

    def _call_model(self, model_name: str, user_content: str) -> str:
        """Route generation call dynamically to Gemini or Claude (Vertex AI / Direct)."""
        if model_name.startswith("claude"):
            # 1. Try Vertex AI global/regional rawPredict
            try:
                import google.auth
                from google.auth.transport.requests import Request
                import requests

                creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
                creds.refresh(Request())
                project_id = self.project_id or project or "stellar-cumulus-449523-b8"
                location = os.environ.get("ANTHROPIC_VERTEX_REGION", "global")
                
                if location == "global":
                    url = f"https://aiplatform.googleapis.com/v1/projects/{project_id}/locations/global/publishers/anthropic/models/{model_name}:rawPredict"
                else:
                    url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/anthropic/models/{model_name}:rawPredict"

                headers = {
                    "Authorization": f"Bearer {creds.token}",
                    "Content-Type": "application/json; charset=utf-8",
                }
                payload = {
                    "anthropic_version": "vertex-2023-10-16",
                    "system": self._system_prompt,
                    "messages": [{"role": "user", "content": user_content}],
                    "max_tokens": 8192,
                    "thinking": {"type": "disabled"},
                }
                resp = requests.post(url, headers=headers, json=payload, timeout=120)
                if resp.status_code == 200:
                    data = resp.json()
                    text_parts = [b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"]
                    if text_parts:
                        return "".join(text_parts)
            except Exception:
                pass

            # 2. Fallback to Anthropic SDK / AnthropicVertex
            anthropic_client = self._get_anthropic_client()
            resp = anthropic_client.messages.create(
                model=model_name,
                max_tokens=8192,
                system=self._system_prompt,
                messages=[{"role": "user", "content": user_content}],
            )
            return resp.content[0].text
        else:
            # Google Gemini model via Vertex AI
            client = self._get_gemini_client()
            if client == "vertexai_sdk":
                from vertexai.generative_models import GenerativeModel
                gmodel = GenerativeModel(model_name, system_instruction=self._system_prompt)
                resp = gmodel.generate_content(user_content)
                return resp.text
            else:
                resp = client.models.generate_content(
                    model=model_name,
                    contents=user_content,
                    config={"system_instruction": self._system_prompt},
                )
                return resp.text

    def _extract_yaml(self, text: str) -> str:
        """Extract YAML block from LLM response."""
        match = re.search(r"```(?:yaml|lookml)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        if match:
            return match.group(1).strip()

        cleaned = text.strip()
        if cleaned.startswith("```yaml"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```lookml"):
            cleaned = cleaned[9:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return cleaned.strip()

    def _validate_yaml(self, yaml_str: str) -> None:
        """Validate YAML syntax and structure."""
        try:
            parsed = yaml.safe_load(yaml_str)
            if not isinstance(parsed, list) or len(parsed) == 0:
                raise ValueError("LookML dashboard must be a YAML list starting with '- dashboard: ...'")
            if "dashboard" not in parsed[0]:
                raise ValueError("First element in LookML dashboard YAML must have 'dashboard' key")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML syntax generated: {e}")

    def generate_template(
        self,
        explore_metadata: Dict[str, Any],
        title: str = "Overview Dashboard",
        preferred_slug: Optional[str] = None,
    ) -> str:
        """Generate a deterministic baseline dashboard without LLM."""
        model = explore_metadata["model"]
        explore = explore_metadata["explore"]
        dimensions = explore_metadata.get("dimensions", [])
        measures = explore_metadata.get("measures", [])

        date_dim = next((d["name"] for d in dimensions if "date" in d["name"] or "created" in d["name"]), None)
        cat_dim = next((d["name"] for d in dimensions if "category" in d["name"] or "status" in d["name"] or "brand" in d["name"]), None)
        if not cat_dim and dimensions:
            cat_dim = dimensions[0]["name"]

        dash_slug = re.sub(r"[^a-zA-Z0-9_]", "_", title.lower())

        elements = []
        col = 0

        # KPI tiles
        for i, m in enumerate(measures[:4]):
            tile_title = m.get("label", m["name"].split(".")[-1].replace("_", " ").title())
            elem = {
                "title": tile_title,
                "name": f"kpi_{i+1}",
                "model": model,
                "explore": explore,
                "type": "single_value",
                "fields": [m["name"]],
                "row": 0,
                "col": col,
                "width": 6,
                "height": 4,
            }
            if date_dim:
                elem["listen"] = {"date_filter": date_dim}
            elements.append(elem)
            col += 6

        row = 4

        # Trend Chart
        if date_dim and measures:
            month_dim = next((d["name"] for d in dimensions if "month" in d["name"]), date_dim)
            elem = {
                "title": f"Trend by {month_dim.split('.')[-1].replace('_', ' ').title()}",
                "name": "trend_chart",
                "model": model,
                "explore": explore,
                "type": "looker_line",
                "fields": [month_dim, measures[0]["name"]],
                "sorts": [month_dim],
                "row": row,
                "col": 0,
                "width": 14,
                "height": 8,
            }
            if date_dim:
                elem["listen"] = {"date_filter": date_dim}
            elements.append(elem)

        # Breakdown Chart
        if cat_dim and measures:
            elem = {
                "title": f"Distribution by {cat_dim.split('.')[-1].replace('_', ' ').title()}",
                "name": "breakdown_chart",
                "model": model,
                "explore": explore,
                "type": "looker_column",
                "fields": [cat_dim, measures[0]["name"]],
                "sorts": [f"{measures[0]['name']} desc"],
                "limit": 10,
                "row": row,
                "col": 14 if (date_dim and measures) else 0,
                "width": 10 if (date_dim and measures) else 24,
                "height": 8,
            }
            if date_dim:
                elem["listen"] = {"date_filter": date_dim}
            elements.append(elem)

        row += 8

        # Detailed Table
        table_fields = [cat_dim] if cat_dim else []
        table_fields += [m["name"] for m in measures[:3]]
        elem = {
            "title": "Detailed Breakdown",
            "name": "detail_table",
            "model": model,
            "explore": explore,
            "type": "looker_grid",
            "fields": table_fields,
            "show_totals": True,
            "limit": 25,
            "row": row,
            "col": 0,
            "width": 24,
            "height": 8,
        }
        if date_dim:
            elem["listen"] = {"date_filter": date_dim}
        elements.append(elem)

        dash_obj = {
            "dashboard": dash_slug,
            "title": title,
            "description": f"Automated dashboard for {model}/{explore}",
            "layout": "newspaper",
            "preferred_viewer": "dashboards-next",
            "crossfilter_enabled": True,
        }
        if preferred_slug:
            dash_obj["preferred_slug"] = preferred_slug
        if date_dim:
            dash_obj["filters"] = [
                {
                    "name": "date_filter",
                    "title": "Date Range",
                    "type": "date_filter",
                    "default_value": "30 days",
                    "ui_config": {"type": "relative_timeframes", "display": "inline"},
                }
            ]
        dash_obj["elements"] = elements

        return yaml.dump([dash_obj], sort_keys=False)
