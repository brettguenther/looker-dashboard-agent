"""Configuration loader for Looker CLI profile, MCP credentials, and token auto-refresh."""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class LookerProfile:
    name: str
    host: str
    port: int = 443
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expiration: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    ssl: bool = True

    @property
    def base_url(self) -> str:
        protocol = "https" if self.ssl else "http"
        if (self.ssl and self.port == 443) or (not self.ssl and self.port == 80):
            return f"{protocol}://{self.host}"
        return f"{protocol}://{self.host}:{self.port}"

    @property
    def mcp_url(self) -> str:
        return f"{self.base_url}/mcp"

    @property
    def api_base_url(self) -> str:
        return f"{self.base_url}/api/4.0"

    def get_auth_headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def refresh_session_if_needed(self) -> None:
        """Attempt to refresh OAuth session via looker-cli if available."""
        try:
            cmd = ["looker-cli", "user", "me", "--profile", self.name]
            proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=15)
            if proc.returncode == 0:
                # Reload updated profile from config
                refreshed = load_profile(self.name)
                self.access_token = refreshed.access_token
                self.refresh_token = refreshed.refresh_token
                self.expiration = refreshed.expiration
        except Exception:
            pass


def get_config_path() -> Path:
    config_dir = os.environ.get("LOOKER_CLI_CONFIG_DIR")
    if config_dir:
        return Path(config_dir) / "config.yaml"
    return Path.home() / ".config" / "looker-cli" / "config.yaml"


def get_mcp_token_paths() -> List[Path]:
    """Candidate paths for Antigravity MCP OAuth token files."""
    home = Path.home()
    return [
        home / ".gemini" / "antigravity" / "mcp_oauth_tokens.json",
        home / ".gemini" / "antigravity-cli" / "mcp_oauth_tokens.json",
        home / ".gemini" / "config" / "mcp_oauth_tokens.json",
    ]


def list_profiles() -> List[str]:
    config_file = get_config_path()
    if not config_file.exists():
        return []
    with open(config_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return list(data.get("profiles", {}).keys())


def load_profile(profile_name: Optional[str] = None) -> LookerProfile:
    """Load Looker profile with multi-source token discovery.
    
    Priority:
    1. ~/.config/looker-cli/config.yaml (Looker CLI active profile)
    2. ~/.gemini/antigravity/mcp_oauth_tokens.json (Antigravity MCP token cache)
    3. Environment variables (LOOKER_HOST, LOOKER_ACCESS_TOKEN)
    """
    # 1. Check looker-cli config.yaml
    config_file = get_config_path()
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        profiles = data.get("profiles", {})
        target_profile = profile_name or data.get("default")
        if not target_profile and profiles:
            target_profile = next(iter(profiles))

        if target_profile and target_profile in profiles:
            pdata = profiles[target_profile]
            port_val = pdata.get("port", 443)
            try:
                port = int(port_val)
            except (ValueError, TypeError):
                port = 443

            return LookerProfile(
                name=target_profile,
                host=pdata.get("host", "localhost"),
                port=port,
                access_token=pdata.get("access_token"),
                refresh_token=pdata.get("refresh_token"),
                expiration=pdata.get("expiration"),
                client_id=pdata.get("client_id"),
                client_secret=pdata.get("client_secret"),
                ssl=pdata.get("ssl", True),
            )

    # 2. Check Antigravity MCP OAuth Token Cache
    for token_path in get_mcp_token_paths():
        if token_path.exists():
            try:
                tokens_data = json.loads(token_path.read_text(encoding="utf-8"))
                for key, val in tokens_data.items():
                    if isinstance(val, dict) and "access_token" in val:
                        host = os.environ.get("LOOKER_HOST", "localhost")
                        return LookerProfile(
                            name="mcp_token_cache",
                            host=host,
                            access_token=val.get("access_token"),
                            refresh_token=val.get("refresh_token"),
                            expiration=val.get("expires_at"),
                        )
            except Exception:
                pass

    # 3. Fallback to Environment Variables
    host = os.environ.get("LOOKER_HOST", "localhost")
    token = os.environ.get("LOOKER_ACCESS_TOKEN")
    return LookerProfile(
        name="env",
        host=host,
        access_token=token,
    )
