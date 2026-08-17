"""LookML Dashboard Query Element Verification Engine."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import yaml

from looker_builder.mcp_client import LookerMCPClient


@dataclass
class ElementVerificationResult:
    element_name: str
    element_title: str
    element_type: str
    fields: List[str]
    passed: bool
    error_message: Optional[str] = None
    sample_data: Optional[Any] = None
    latency_ms: float = 0.0


@dataclass
class DashboardVerificationReport:
    all_passed: bool
    total_elements: int
    query_elements: int
    passed_elements: int
    failed_elements: int
    results: List[ElementVerificationResult] = field(default_factory=list)

    def format_summary(self) -> str:
        lines = [
            f"Verification: {self.passed_elements}/{self.query_elements} query elements verified successfully."
        ]
        for r in self.results:
            status = "✅ PASS" if r.passed else f"❌ FAIL ({r.error_message})"
            lines.append(f"  - [{r.element_type}] '{r.element_title}' ({r.element_name}): {status}")
        return "\n".join(lines)


class DashboardVerifier:
    """Verifies that all query tiles in a generated LookML dashboard execute cleanly in Looker."""

    def __init__(self, mcp_client: LookerMCPClient):
        self.mcp_client = mcp_client

    def verify_lookml(self, lookml_yaml: str) -> DashboardVerificationReport:
        """Verify each query element in the LookML YAML against Looker MCP."""
        try:
            parsed = yaml.safe_load(lookml_yaml)
            if not isinstance(parsed, list) or len(parsed) == 0:
                return DashboardVerificationReport(
                    all_passed=False,
                    total_elements=0,
                    query_elements=0,
                    passed_elements=0,
                    failed_elements=1,
                    results=[ElementVerificationResult(
                        element_name="dashboard_root",
                        element_title="YAML Structure",
                        element_type="syntax",
                        fields=[],
                        passed=False,
                        error_message="YAML is not a list starting with '- dashboard:'"
                    )]
                )
            dash_obj = parsed[0]
            elements = dash_obj.get("elements", [])
        except Exception as e:
            return DashboardVerificationReport(
                all_passed=False,
                total_elements=0,
                query_elements=0,
                passed_elements=0,
                failed_elements=1,
                results=[ElementVerificationResult(
                    element_name="dashboard_root",
                    element_title="YAML Parser",
                    element_type="syntax",
                    fields=[],
                    passed=False,
                    error_message=f"YAML parse error: {e}"
                )]
            )

        results: List[ElementVerificationResult] = []
        query_elements_count = 0

        for elem in elements:
            elem_type = elem.get("type", "unknown")
            elem_name = elem.get("name", "unnamed_tile")
            elem_title = elem.get("title", elem_name)

            # Skip text / markdown header tiles
            if elem_type == "text" or "fields" not in elem:
                continue

            query_elements_count += 1
            raw_fields = elem.get("fields", [])
            model = elem.get("model", dash_obj.get("model"))
            explore = elem.get("explore", dash_obj.get("explore"))

            # Filter fields: exclude dynamic_fields table calculations if declared
            dynamic_calc_names = set()
            for df in elem.get("dynamic_fields", []):
                if isinstance(df, dict) and "table_calculation" in df:
                    dynamic_calc_names.add(df["table_calculation"])

            query_fields = [f for f in raw_fields if f not in dynamic_calc_names]

            if not model or not explore or not query_fields:
                results.append(ElementVerificationResult(
                    element_name=elem_name,
                    element_title=elem_title,
                    element_type=elem_type,
                    fields=raw_fields,
                    passed=False,
                    error_message=f"Missing model/explore or valid query fields (model={model}, explore={explore}, fields={query_fields})"
                ))
                continue

            # Run test query via Looker MCP
            start_t = time.time()
            try:
                query_res = self.mcp_client.query(
                    model=model,
                    explore=explore,
                    fields=query_fields,
                    limit=1,
                )
                latency = (time.time() - start_t) * 1000
                results.append(ElementVerificationResult(
                    element_name=elem_name,
                    element_title=elem_title,
                    element_type=elem_type,
                    fields=query_fields,
                    passed=True,
                    sample_data=query_res,
                    latency_ms=latency,
                ))
            except Exception as e:
                latency = (time.time() - start_t) * 1000
                err_msg = str(e)
                results.append(ElementVerificationResult(
                    element_name=elem_name,
                    element_title=elem_title,
                    element_type=elem_type,
                    fields=query_fields,
                    passed=False,
                    error_message=err_msg,
                    latency_ms=latency,
                ))

        passed_count = sum(1 for r in results if r.passed)
        failed_count = len(results) - passed_count
        all_passed = (failed_count == 0) and (query_elements_count > 0)

        return DashboardVerificationReport(
            all_passed=all_passed,
            total_elements=len(elements),
            query_elements=query_elements_count,
            passed_elements=passed_count,
            failed_elements=failed_count,
            results=results,
        )

    def verify_and_remediate(
        self,
        lookml_yaml: str,
        prompt: str,
        explore_metadata: Dict[str, Any],
        generator: Any,
        preferred_slug: Optional[str] = None,
        max_retries: int = 2,
    ) -> Tuple[str, DashboardVerificationReport]:
        """Runs the verification loop and automatically remediates failed queries with the generator."""
        current_yaml = lookml_yaml
        report = self.verify_lookml(current_yaml)

        attempts = 0
        while not report.all_passed and attempts < max_retries:
            attempts += 1
            failing_errors = [
                f"Element '{r.element_name}' ({r.element_title}): Error: {r.error_message}. Attempted fields: {r.fields}"
                for r in report.results if not r.passed
            ]
            remediation_prompt = (
                f"{prompt}\n\n"
                f"PREVIOUS ATTEMPT QUERY VERIFICATION ERRORS:\n"
                + "\n".join(failing_errors)
                + "\n\nPlease fix these queries by selecting strictly valid dimension and measure fields from the schema."
            )
            current_yaml = generator.generate(
                prompt=remediation_prompt,
                explore_metadata=explore_metadata,
                preferred_slug=preferred_slug,
            )
            report = self.verify_lookml(current_yaml)

        return current_yaml, report
