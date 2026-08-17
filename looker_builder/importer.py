"""Looker Dashboard Importer using LookML import API and preferred_slug in-place updates."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, Optional
import requests
import yaml

from looker_builder.config import LookerProfile, load_profile


@dataclass
class ImportedDashboardResult:
    id: str
    title: str
    slug: str
    folder_id: Optional[str]
    folder_name: Optional[str]
    url: str
    api_url: str
    raw_response: Dict[str, Any]


def sanitize_lookml_yaml(lookml_yaml: str, preferred_slug: Optional[str] = None) -> str:
    """Sanitize LookML YAML, removing invalid top-level slug fields and ensuring valid preferred_slug."""
    try:
        data = yaml.safe_load(lookml_yaml)
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            # Remove invalid top-level 'slug' which causes API 422
            data[0].pop("slug", None)
            if preferred_slug and re.match(r"^[A-Za-z0-9]{15,30}$", preferred_slug):
                data[0]["preferred_slug"] = str(preferred_slug)
            elif "preferred_slug" in data[0] and not re.match(r"^[A-Za-z0-9]{15,30}$", str(data[0]["preferred_slug"])):
                data[0].pop("preferred_slug", None)
            return yaml.dump(data, sort_keys=False)
    except Exception:
        pass

    # Regex cleanup fallback
    lookml_yaml = re.sub(r"\n\s+slug:\s*[^\n]+", "", lookml_yaml)
    if preferred_slug and re.match(r"^[A-Za-z0-9]{15,30}$", preferred_slug) and "preferred_slug:" not in lookml_yaml:
        lookml_yaml = re.sub(
            r"(-\s*dashboard:\s*[^\n]+)",
            rf'\1\n  preferred_slug: "{preferred_slug}"',
            lookml_yaml,
            count=1,
        )
    return lookml_yaml


def inject_preferred_slug(lookml_yaml: str, preferred_slug: Optional[str]) -> str:
    return sanitize_lookml_yaml(lookml_yaml, preferred_slug)


class LookerDashboardImporter:
    """Imports LookML dashboard YAML into Looker as an interactive User-Defined Dashboard (UDD)."""

    def __init__(self, profile: Optional[LookerProfile] = None):
        self.profile = profile or load_profile()

    def import_lookml(
        self,
        lookml_yaml: str,
        folder_id: Optional[str] = None,
        preferred_slug: Optional[str] = None,
        use_cli_fallback: bool = True,
    ) -> ImportedDashboardResult:
        """Import LookML dashboard string into Looker.
        
        If preferred_slug is provided, Looker overwrites the existing dashboard in-place.
        """
        if preferred_slug:
            lookml_yaml = inject_preferred_slug(lookml_yaml, preferred_slug)

        payload: Dict[str, Any] = {"lookml": lookml_yaml}
        if folder_id:
            payload["folder_id"] = str(folder_id)

        # 1. Try REST API endpoint: POST /api/4.0/dashboards/lookml
        url = f"{self.profile.api_base_url}/dashboards/lookml"

        def _do_request():
            headers = self.profile.get_auth_headers()
            return requests.post(url, headers=headers, json=payload, timeout=45)

        try:
            resp = _do_request()
            if resp.status_code == 401:
                # Refresh session and retry
                self.profile.refresh_session_if_needed()
                resp = _do_request()

            if resp.status_code == 200:
                data = resp.json()
                dash_id = str(data.get("id"))
                slug = data.get("slug") or dash_id
                folder_info = data.get("folder", {})
                folder_id_res = str(data.get("folder_id") or folder_info.get("id") or "")
                folder_name = folder_info.get("name")

                return ImportedDashboardResult(
                    id=dash_id,
                    title=data.get("title", "Untitled Dashboard"),
                    slug=slug,
                    folder_id=folder_id_res,
                    folder_name=folder_name,
                    url=f"{self.profile.base_url}/dashboards/{slug}",
                    api_url=f"{self.profile.api_base_url}/dashboards/{dash_id}",
                    raw_response=data,
                )
            elif not use_cli_fallback:
                resp.raise_for_status()
        except Exception as e:
            if not use_cli_fallback:
                raise e

        # 2. Fallback via looker-cli
        return self._import_via_cli(payload)

    def _import_via_cli(self, payload: Dict[str, Any]) -> ImportedDashboardResult:
        """Execute dashboard import via looker-cli command."""
        cmd = [
            "looker-cli",
            "api",
            "dashboard",
            "import_dashboard_from_lookml",
            "-",
            "--profile",
            self.profile.name,
        ]
        proc = subprocess.run(
            cmd,
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"looker-cli import failed (code {proc.returncode}): {proc.stderr}\n{proc.stdout}")

        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError:
            raise RuntimeError(f"Failed to parse looker-cli JSON output: {proc.stdout}")

        dash_id = str(data.get("id"))
        slug = data.get("slug") or dash_id
        folder_info = data.get("folder", {})
        folder_id_res = str(data.get("folder_id") or folder_info.get("id") or "")
        folder_name = folder_info.get("name")

        return ImportedDashboardResult(
            id=dash_id,
            title=data.get("title", "Untitled Dashboard"),
            slug=slug,
            folder_id=folder_id_res,
            folder_name=folder_name,
            url=f"{self.profile.base_url}/dashboards/{slug}",
            api_url=f"{self.profile.api_base_url}/dashboards/{dash_id}",
            raw_response=data,
        )
