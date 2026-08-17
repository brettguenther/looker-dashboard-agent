"""CLI Interface for Looker LookML Dashboard Builder Agent with Dynamic Model Selection and Comparison."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.table import Table

from looker_builder.agent import LookerDashboardAgent
from looker_builder.config import list_profiles, load_profile
from looker_builder.importer import LookerDashboardImporter

app = typer.Typer(
    name="looker-builder",
    help="AI-powered Looker LookML Dashboard Builder CLI with Multi-Model Support (Gemini, Claude) and Query Verification.",
    add_completion=False,
)
console = Console()


def print_verification_table(report) -> None:
    """Renders a formatted table of element query verification results."""
    if not report or not report.results:
        return
    table = Table(title="🔍 Query Element Verification Results", border_style="cyan")
    table.add_column("Tile Name", style="white bold")
    table.add_column("Type", style="yellow")
    table.add_column("Queried Fields", style="dim")
    table.add_column("Status", style="bold")
    table.add_column("Latency", style="magenta")

    for r in report.results:
        status = "[green]✅ PASS[/green]" if r.passed else f"[red]❌ FAIL ({r.error_message})[/red]"
        lat = f"{r.latency_ms:.0f}ms" if r.latency_ms > 0 else "-"
        table.add_row(r.element_title, r.element_type, ", ".join(r.fields[:3]), status, lat)

    console.print(table)


@app.command("status")
def status_cmd(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Looker CLI profile to use"),
):
    """Check connectivity to Looker Managed MCP and API."""
    with console.status("[bold green]Connecting to Looker Managed MCP..."):
        try:
            agent = LookerDashboardAgent(profile_name=profile)
            info = agent.test_connection()
        except Exception as e:
            console.print(f"[bold red]Connection failed:[/bold red] {e}")
            raise typer.Exit(1)

    table = Table(title="Looker MCP Connection Status", show_header=False)
    table.add_row("Profile", f"[cyan]{info['profile']}[/cyan]")
    table.add_row("Host", f"[green]{info['host']}[/green]")
    table.add_row("MCP URL", f"[blue]{info['mcp_url']}[/blue]")
    table.add_row("Server", f"{info['server_info'].get('name', 'Toolbox')} v{info['server_info'].get('version', '')}")
    table.add_row("Tools Available", f"[yellow]{info['tool_count']}[/yellow]")
    table.add_row("Available Models", ", ".join(info["available_models"]))

    console.print(Panel(table, title="[bold]Looker MCP Status[/bold]", border_style="green"))


@app.command("models")
def list_models_cmd(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Looker CLI profile to use"),
):
    """List available LookML models from Looker MCP."""
    with console.status("[bold green]Fetching models from MCP..."):
        try:
            agent = LookerDashboardAgent(profile_name=profile)
            models = agent.get_models()
        except Exception as e:
            console.print(f"[bold red]Failed to fetch models:[/bold red] {e}")
            raise typer.Exit(1)

    table = Table(title="Available LookML Models")
    table.add_column("Model Name", style="cyan bold")
    table.add_column("Label", style="white")
    table.add_column("Project", style="magenta")

    for m in models:
        table.add_row(m.get("name", ""), m.get("label", ""), m.get("project_name", ""))

    console.print(table)


@app.command("explores")
def list_explores_cmd(
    model: str = typer.Argument(..., help="Model name"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Looker CLI profile to use"),
):
    """List explores for a specific model from Looker MCP."""
    with console.status(f"[bold green]Fetching explores for model '{model}'..."):
        try:
            agent = LookerDashboardAgent(profile_name=profile)
            explores = agent.get_explores(model)
        except Exception as e:
            console.print(f"[bold red]Failed to fetch explores:[/bold red] {e}")
            raise typer.Exit(1)

    table = Table(title=f"Explores in Model '{model}'")
    table.add_column("Explore Name", style="cyan bold")
    table.add_column("Label", style="white")
    table.add_column("Group Label", style="dim")

    for e in explores:
        table.add_row(e.get("name", ""), e.get("label", ""), e.get("group_label", ""))

    console.print(table)


@app.command("fields")
def list_fields_cmd(
    model: str = typer.Argument(..., help="Model name"),
    explore: str = typer.Argument(..., help="Explore name"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Looker CLI profile to use"),
):
    """Inspect dimensions and measures for an explore from Looker MCP."""
    with console.status(f"[bold green]Fetching fields for '{model}/{explore}'..."):
        try:
            agent = LookerDashboardAgent(profile_name=profile)
            meta = agent.get_explore_fields(model, explore)
        except Exception as e:
            console.print(f"[bold red]Failed to fetch fields:[/bold red] {e}")
            raise typer.Exit(1)

    meas_table = Table(title=f"Measures in '{model}/{explore}'")
    meas_table.add_column("Measure Name", style="green bold")
    meas_table.add_column("Type", style="yellow")
    meas_table.add_column("Label", style="white")

    for m in meta.get("measures", []):
        meas_table.add_row(m.get("name", ""), m.get("type", ""), m.get("label", ""))

    console.print(meas_table)

    dim_table = Table(title=f"Dimensions in '{model}/{explore}' (Top 30)")
    dim_table.add_column("Dimension Name", style="cyan bold")
    dim_table.add_column("Type", style="yellow")
    dim_table.add_column("Label", style="white")

    for d in meta.get("dimensions", [])[:30]:
        dim_table.add_row(d.get("name", ""), d.get("type", ""), d.get("label", ""))

    console.print(dim_table)


@app.command("generate")
def generate_cmd(
    prompt: str = typer.Argument(..., help="Natural language description of the dashboard to create"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Target LookML model"),
    explore: Optional[str] = typer.Option(None, "--explore", "-e", help="Target Explore"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Dashboard title"),
    preferred_slug: Optional[str] = typer.Option(None, "--preferred-slug", "-s", help="Preferred slug for in-place updates"),
    llm_model: Optional[str] = typer.Option(None, "--llm-model", "-L", help="LLM model (e.g. gemini-3.6-flash, gemini-2.5-pro, claude-3-7-sonnet@20250219)"),
    folder_id: Optional[str] = typer.Option(None, "--folder-id", "-f", help="Folder ID to place dashboard in"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Looker CLI profile to use"),
    skip_verify: bool = typer.Option(False, "--skip-verify", help="Skip running test queries for each tile"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Generate and verify LookML without importing"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Save generated LookML to file"),
):
    """Generate a LookML dashboard with AI (Gemini or Claude), verify tile queries live against Looker, and import in-place."""
    agent = LookerDashboardAgent(profile_name=profile)
    active_llm = llm_model or "gemini-3.6-flash"

    with console.status(f"[bold green]Discovering schema, generating LookML with {active_llm} & verifying queries..."):
        try:
            if not model:
                models = agent.get_models()
                model = models[0]["name"] if models else "basic_ecomm"
            if not explore:
                explores = agent.get_explores(model)
                explore = explores[0]["name"] if explores else "basic_order_items"

            metadata = agent.get_explore_fields(model, explore)
            lookml_yaml = agent.generator.generate(
                prompt=prompt,
                explore_metadata=metadata,
                dashboard_title=title,
                preferred_slug=preferred_slug,
                model_name=active_llm,
            )

            # Verification Loop
            verification_report = None
            if not skip_verify:
                lookml_yaml, verification_report = agent.verifier.verify_and_remediate(
                    lookml_yaml=lookml_yaml,
                    prompt=prompt,
                    explore_metadata=metadata,
                    generator=agent.generator,
                    preferred_slug=preferred_slug,
                )
        except Exception as e:
            console.print(f"[bold red]Generation / Verification error:[/bold red] {e}")
            raise typer.Exit(1)

    print_verification_table(verification_report)

    console.print(Panel(Syntax(lookml_yaml, "yaml", theme="monokai", line_numbers=True), title=f"[bold]Verified LookML Dashboard ({active_llm})[/bold]"))

    if output_file:
        output_file.write_text(lookml_yaml, encoding="utf-8")
        console.print(f"[green]Saved LookML to {output_file}[/green]")

    if dry_run:
        console.print("[yellow]Dry-run mode: Skipped import.[/yellow]")
        return

    with console.status("[bold green]Importing verified dashboard into Looker..."):
        try:
            res = agent.importer.import_lookml(lookml_yaml, folder_id=folder_id, preferred_slug=preferred_slug)
        except Exception as e:
            console.print(f"[bold red]Import error:[/bold red] {e}")
            raise typer.Exit(1)

    success_table = Table(show_header=False, border_style="green")
    success_table.add_row("Dashboard ID", f"[bold cyan]{res.id}[/bold cyan]")
    success_table.add_row("Title", f"[bold white]{res.title}[/bold white]")
    success_table.add_row("LLM Model", f"[magenta]{active_llm}[/magenta]")
    success_table.add_row("Slug", f"[yellow]{res.slug}[/yellow]")
    success_table.add_row("Folder", f"{res.folder_name or 'Personal'} (ID: {res.folder_id})")
    success_table.add_row("Live URL", f"[bold underline green]{res.url}[/bold underline green]")

    header_title = "[bold green]✅ Dashboard Successfully Updated In-Place![/bold green]" if preferred_slug else "[bold green]✅ Dashboard Successfully Verified & Imported![/bold green]"
    console.print(Panel(success_table, title=header_title, border_style="green"))


@app.command("edit")
def edit_cmd(
    slug: str = typer.Argument(..., help="Dashboard slug to update in-place"),
    instructions: str = typer.Argument(..., help="Edit instructions for modifying the dashboard"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Target LookML model"),
    explore: Optional[str] = typer.Option(None, "--explore", "-e", help="Target Explore"),
    llm_model: Optional[str] = typer.Option(None, "--llm-model", "-L", help="LLM model to use"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Looker CLI profile to use"),
    skip_verify: bool = typer.Option(False, "--skip-verify", help="Skip running test queries"),
):
    """Edit an existing Looker dashboard in-place with query verification."""
    agent = LookerDashboardAgent(profile_name=profile)
    active_llm = llm_model or "gemini-3.6-flash"

    with console.status(f"[bold green]Generating & verifying in-place update with {active_llm} for dashboard '{slug}'..."):
        try:
            res = agent.edit_and_update_dashboard(
                preferred_slug=slug,
                edit_instructions=instructions,
                model=model,
                explore=explore,
                llm_model=active_llm,
                verify_queries=not skip_verify,
            )
        except Exception as e:
            console.print(f"[bold red]Edit failed:[/bold red] {e}")
            raise typer.Exit(1)

    print_verification_table(res.verification_report)

    success_table = Table(show_header=False, border_style="green")
    success_table.add_row("Dashboard ID", f"[bold cyan]{res.dashboard_id}[/bold cyan]")
    success_table.add_row("Title", f"[bold white]{res.dashboard_title}[/bold white]")
    success_table.add_row("LLM Model", f"[magenta]{active_llm}[/magenta]")
    success_table.add_row("Slug", f"[yellow]{res.dashboard_slug}[/yellow]")
    success_table.add_row("Live URL", f"[bold underline green]{res.dashboard_url}[/bold underline green]")

    console.print(Panel(success_table, title="[bold green]✅ Dashboard Verified & Updated In-Place![/bold green]", border_style="green"))


@app.command("compare")
def compare_cmd(
    prompt: str = typer.Argument(..., help="Prompt to test on multiple LLM models"),
    model1: str = typer.Option("gemini-3.6-flash", "--model1", help="First model name"),
    model2: str = typer.Option("gemini-2.5-pro", "--model2", help="Second model name"),
    looker_model: Optional[str] = typer.Option(None, "--model", "-m", help="Target LookML model"),
    explore: Optional[str] = typer.Option(None, "--explore", "-e", help="Target Explore"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Looker CLI profile to use"),
):
    """Generate, verify, and import dashboards from two different LLM models for side-by-side comparison."""
    agent = LookerDashboardAgent(profile_name=profile)

    if not looker_model:
        models = agent.get_models()
        looker_model = models[0]["name"] if models else "basic_ecomm"
    if not explore:
        explores = agent.get_explores(looker_model)
        explore = explores[0]["name"] if explores else "basic_order_items"

    console.print(Panel.fit(
        f"[bold cyan]🔍 Model Comparison Run[/bold cyan]\n"
        f"• Prompt: [white]{prompt}[/white]\n"
        f"• Model 1: [magenta]{model1}[/magenta]\n"
        f"• Model 2: [magenta]{model2}[/magenta]\n"
        f"• Explore: [green]{looker_model}/{explore}[/green]",
        border_style="cyan"
    ))

    # 1. Run Model 1
    console.print(f"\n[bold green]🚀 Running Model 1 ({model1})...[/bold green]")
    try:
        res1 = agent.build_and_import_dashboard(
            prompt=prompt,
            model=looker_model,
            explore=explore,
            title=f"Comparison: {model1}",
            llm_model=model1,
        )
        print_verification_table(res1.verification_report)
        console.print(f"[green]Model 1 Dashboard ID: {res1.dashboard_id} | URL: {res1.dashboard_url}[/green]")
    except Exception as e:
        console.print(f"[bold red]Model 1 failed:[/bold red] {e}")
        res1 = None

    # 2. Run Model 2
    console.print(f"\n[bold green]🚀 Running Model 2 ({model2})...[/bold green]")
    try:
        res2 = agent.build_and_import_dashboard(
            prompt=prompt,
            model=looker_model,
            explore=explore,
            title=f"Comparison: {model2}",
            llm_model=model2,
        )
        print_verification_table(res2.verification_report)
        console.print(f"[green]Model 2 Dashboard ID: {res2.dashboard_id} | URL: {res2.dashboard_url}[/green]")
    except Exception as e:
        console.print(f"[bold red]Model 2 failed:[/bold red] {e}")
        res2 = None

    # 3. Output Comparison Summary
    summary_table = Table(title="📊 Side-by-Side Model Comparison Results", border_style="cyan")
    summary_table.add_column("Metric", style="white bold")
    summary_table.add_column(f"Model 1: {model1}", style="cyan")
    summary_table.add_column(f"Model 2: {model2}", style="magenta")

    if res1 and res2:
        rep1 = res1.verification_report
        rep2 = res2.verification_report
        summary_table.add_row("Dashboard ID", str(res1.dashboard_id), str(res2.dashboard_id))
        summary_table.add_row("Total Tiles", str(rep1.total_elements if rep1 else "-"), str(rep2.total_elements if rep2 else "-"))
        summary_table.add_row("Query Elements Verified", f"{rep1.passed_elements}/{rep1.query_elements}" if rep1 else "-", f"{rep2.passed_elements}/{rep2.query_elements}" if rep2 else "-")
        summary_table.add_row("Verification Rate", f"{(rep1.passed_elements/rep1.query_elements*100):.0f}%" if (rep1 and rep1.query_elements) else "-", f"{(rep2.passed_elements/rep2.query_elements*100):.0f}%" if (rep2 and rep2.query_elements) else "-")
        summary_table.add_row("Live URL", res1.dashboard_url, res2.dashboard_url)
        console.print(summary_table)


@app.command("verify")
def verify_cmd(
    file_path: Path = typer.Argument(..., help="Path to LookML dashboard YAML file", exists=True),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Looker CLI profile to use"),
):
    """Run test queries against Looker MCP for all tiles in a LookML YAML file."""
    lookml_yaml = file_path.read_text(encoding="utf-8")
    agent = LookerDashboardAgent(profile_name=profile)

    with console.status(f"[bold green]Verifying query tiles in '{file_path.name}' via Looker MCP..."):
        report = agent.verify_lookml(lookml_yaml)

    print_verification_table(report)


@app.command("interactive")
def interactive_cmd(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Looker CLI profile to use"),
):
    """Interactive wizard to design, verify, import, and iteratively refine Looker dashboards in-place."""
    console.print(Panel.fit("[bold cyan]🚀 Looker LookML Dashboard Builder Agent[/bold cyan]\nInteractive Generation, Multi-Model Selection & In-Place Refinement", border_style="cyan"))

    agent = LookerDashboardAgent(profile_name=profile)

    # 1. Select Model
    with console.status("[bold green]Discovering models via Looker MCP..."):
        models = agent.get_models()

    if not models:
        console.print("[bold red]No models found.[/bold red]")
        raise typer.Exit(1)

    console.print("\n[bold]Select a LookML Model:[/bold]")
    for i, m in enumerate(models, 1):
        console.print(f"  [cyan]{i}[/cyan]. [bold]{m.get('name')}[/bold] ({m.get('label')})")
    
    m_choice = Prompt.ask("Choose model number", default="1")
    try:
        selected_model = models[int(m_choice) - 1]["name"]
    except Exception:
        selected_model = models[0]["name"]
    console.print(f"Selected model: [bold cyan]{selected_model}[/bold cyan]\n")

    # 2. Select Explore
    with console.status(f"[bold green]Discovering explores for '{selected_model}'..."):
        explores = agent.get_explores(selected_model)

    if not explores:
        console.print("[bold red]No explores found.[/bold red]")
        raise typer.Exit(1)

    console.print("\n[bold]Select an Explore:[/bold]")
    for i, e in enumerate(explores, 1):
        console.print(f"  [cyan]{i}[/cyan]. [bold]{e.get('name')}[/bold] ({e.get('label')})")

    e_choice = Prompt.ask("Choose explore number", default="1")
    try:
        selected_explore = explores[int(e_choice) - 1]["name"]
    except Exception:
        selected_explore = explores[0]["name"]
    console.print(f"Selected explore: [bold cyan]{selected_explore}[/bold cyan]\n")

    # 3. Get Explore metadata
    with console.status(f"[bold green]Fetching dimensions and measures via MCP..."):
        metadata = agent.get_explore_fields(selected_model, selected_explore)

    console.print(f"Found [green]{len(metadata.get('measures', []))} measures[/green] and [cyan]{len(metadata.get('dimensions', []))} dimensions[/cyan].")

    # 4. LLM Selection & User Prompt
    llm_choice = Prompt.ask("\nSelect LLM Model", default="gemini-3.6-flash")
    dash_title = Prompt.ask("Dashboard Title", default="Executive Overview")
    user_prompt = Prompt.ask("Describe what you want on the dashboard (metrics, charts, breakdowns)", default="KPIs for main measures, monthly trend chart, category breakdown, and summary table")

    # 5. Generate & Verify
    with console.status(f"[bold green]Generating LookML with {llm_choice} & executing live verification queries..."):
        lookml_yaml = agent.generator.generate(
            prompt=user_prompt,
            explore_metadata=metadata,
            dashboard_title=dash_title,
            model_name=llm_choice,
        )
        lookml_yaml, report = agent.verifier.verify_and_remediate(
            lookml_yaml=lookml_yaml,
            prompt=user_prompt,
            explore_metadata=metadata,
            generator=agent.generator,
        )

    print_verification_table(report)
    console.print(Panel(Syntax(lookml_yaml, "yaml", theme="monokai", line_numbers=True), title=f"[bold]Verified LookML ({dash_title})[/bold]"))

    active_slug = None
    if Confirm.ask("\nImport this verified dashboard into Looker now?", default=True):
        with console.status("[bold green]Importing into Looker..."):
            res = agent.importer.import_lookml(lookml_yaml)
            active_slug = res.slug

        console.print(Panel(
            f"[bold green]🎉 Dashboard Live in Looker![/bold green]\n\n"
            f"• [bold]ID:[/bold] {res.id}\n"
            f"• [bold]Title:[/bold] {res.title}\n"
            f"• [bold]LLM:[/bold] {llm_choice}\n"
            f"• [bold]Slug:[/bold] [yellow]{res.slug}[/yellow]\n"
            f"• [bold]Folder:[/bold] {res.folder_name or 'Personal'} (ID: {res.folder_id})\n"
            f"• [bold]URL:[/bold] [bold underline green]{res.url}[/bold underline green]",
            title="Import Success",
            border_style="green",
        ))

    # 6. Iterative In-Place Refinement Loop
    while active_slug:
        if not Confirm.ask(f"\nWould you like to refine or modify this dashboard in-place (slug: {active_slug})?", default=False):
            break
        edit_prompt = Prompt.ask("Describe your modifications")
        with console.status(f"[bold green]Updating & verifying dashboard '{active_slug}' in-place..."):
            try:
                res = agent.edit_and_update_dashboard(
                    preferred_slug=active_slug,
                    edit_instructions=edit_prompt,
                    model=selected_model,
                    explore=selected_explore,
                    llm_model=llm_choice,
                    verify_queries=True,
                )
                print_verification_table(res.verification_report)
                console.print(Panel(
                    f"[bold green]✅ In-Place Update Complete![/bold green]\n\n"
                    f"• [bold]ID:[/bold] {res.dashboard_id}\n"
                    f"• [bold]Title:[/bold] {res.dashboard_title}\n"
                    f"• [bold]URL:[/bold] [bold underline green]{res.dashboard_url}[/bold underline green]",
                    title="Update Success",
                    border_style="green",
                ))
            except Exception as e:
                console.print(f"[bold red]Update failed:[/bold red] {e}")


def main():
    app()


if __name__ == "__main__":
    main()
