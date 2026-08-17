"""Loader and compiler for LookML Dashboard Skills."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional


def find_skills_directory(custom_path: Optional[str] = None) -> Path:
    """Find the lookml-dashboards skill directory."""
    # 1. Custom path or environment override
    env_path = os.environ.get("LOOKML_SKILLS_DIR")
    target = custom_path or env_path
    if target:
        p = Path(target)
        if p.exists():
            return p

    # 2. Primary: Package internal resources
    pkg_res = Path(__file__).parent / "resources" / "skills" / "lookml-dashboards"
    if pkg_res.exists():
        return pkg_res

    # 3. Fallback: Local .agents workspace directory
    cwd_agents = Path.cwd() / ".agents" / "skills" / "lookml-dashboards"
    if cwd_agents.exists():
        return cwd_agents

    ws_agents = Path(__file__).parent.parent / ".agents" / "skills" / "lookml-dashboards"
    if ws_agents.exists():
        return ws_agents

    raise FileNotFoundError("Could not find 'lookml-dashboards' skill directory.")


class LookMLSkillsKnowledgeBase:
    """Loads and provides access to the full LookML dashboard design skills."""

    def __init__(self, skills_dir: Optional[str] = None):
        self.skills_dir = find_skills_directory(skills_dir)
        self.documents: Dict[str, str] = {}
        self._load_all_documents()

    def _load_all_documents(self) -> None:
        """Load all markdown documentation from the skill folder."""
        for root, _, files in os.walk(self.skills_dir):
            for file in sorted(files):
                if file.endswith(".md"):
                    full_path = Path(root) / file
                    rel_path = full_path.relative_to(self.skills_dir)
                    try:
                        content = full_path.read_text(encoding="utf-8")
                        self.documents[str(rel_path)] = content
                    except Exception as e:
                        print(f"Warning: failed to read skill doc {full_path}: {e}")

    def get_summary(self) -> Dict[str, int]:
        """Return document names and character counts."""
        return {doc: len(content) for doc, content in self.documents.items()}

    def compile_full_system_prompt(self) -> str:
        """Compile all skill documentation into a comprehensive prompt knowledge base."""
        parts: List[str] = [
            "# MASTER LOOKER LOOKML DASHBOARD DESIGN SPECIFICATION",
            "You are an expert Looker LookML Dashboard Engineer. Generate high-quality, production-ready LookML Dashboard YAML.",
            "You MUST strictly adhere to the following official LookML Dashboard specifications, element visualization parameters, and best practices:\n",
        ]

        # 1. Main skill guide
        if "SKILL.md" in self.documents:
            parts.append("## 1. CORE BEST PRACTICES & STRUCTURAL GUIDELINES\n")
            parts.append(self.documents["SKILL.md"])
            parts.append("\n---\n")

        # 2. Boilerplate & Parameters
        if "references/dashboard_parameters.md" in self.documents:
            parts.append("## 2. DASHBOARD PARAMETERS REFERENCE\n")
            parts.append(self.documents["references/dashboard_parameters.md"])
            parts.append("\n---\n")

        if "references/boilerplate_dashboard.md" in self.documents:
            parts.append("## 3. BOILERPLATE DASHBOARD TEMPLATE\n")
            parts.append(self.documents["references/boilerplate_dashboard.md"])
            parts.append("\n---\n")

        # 3. Table Calculations & Dynamic Fields
        if "references/table_calculations.md" in self.documents:
            parts.append("## 4. TABLE CALCULATIONS & DYNAMIC FIELDS REFERENCE\n")
            parts.append(self.documents["references/table_calculations.md"])
            parts.append("\n---\n")

        # 4. Element Visualization References
        parts.append("## 5. ELEMENT VISUALIZATION PARAMETER SPECIFICATIONS\n")
        elem_keys = [k for k in self.documents if k.startswith("references/elements/")]
        for k in sorted(elem_keys):
            elem_name = Path(k).stem.upper()
            parts.append(f"### 5.{elem_name} VISUALIZATION RULES ({k})\n")
            parts.append(self.documents[k])
            parts.append("\n")

        # 5. Markdown & HTML Templates
        if "references/markdown_html_templates.md" in self.documents:
            parts.append("## 6. MARKDOWN & HTML SECTION HEADER TEMPLATES\n")
            parts.append(self.documents["references/markdown_html_templates.md"])
            parts.append("\n---\n")

        # 6. Critical Reminders
        parts.append("""
## 7. CRITICAL SYNTAX CHECKLIST
- Top-level YAML MUST be a list: `- dashboard: <unique_name>`
- Layout MUST be `layout: newspaper`
- Preferred viewer MUST be `preferred_viewer: dashboards-next`
- Crossfiltering: `crossfilter_enabled: true`
- Each tile MUST include: `model`, `explore`, `type`, `fields`, `row`, `col`, `width`, `height`
- Col must be within 0-23 (24-column grid)
- ONLY use fields from the provided schema! Fully qualified `view_name.field_name`
- In `y_axes`, the nested `series` parameter MUST contain objects `series: [{id: "view.measure_name"}]`, NEVER strings!
- For global filters in `filters:`, each applicable tile must define `listen:`
- Return ONLY valid YAML inside a ```yaml ... ``` code block.
""")

        return "\n".join(parts)
