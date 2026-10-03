"""
SafePlate CLI: Interactive terminal interface with Rich styling and Sentry trace breakdown.
Windows CP1252 / UTF-8 safe rendering.
"""

import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from safeplate.agent import SafePlateAgent
from safeplate.telemetry import metrics, IS_SENTRY_ENABLED

# Force utf-8 safe console
console = Console(highlight=False, emoji=False)


def run_cli():
    console.print(Panel.fit(
        "[bold cyan]SafePlate: AI Allergy & Histamine Recipe Agent[/bold cyan]\n"
        "[dim]Open-Source AI Agent with Sentry Agent Tracing | Built for Elena[/dim]",
        border_style="cyan"
    ))

    # Standard high-risk test recipe
    recipe_title = "Classic Chicken Parmesan with Creamy Tomato Sauce & Spinach"
    ingredients = [
        "chicken_breast",
        "parmesan",
        "wheat_flour",
        "tomato",
        "spinach",
        "heavy_cream",
        "olive_oil",
        "garlic"
    ]

    console.print(f"\n[bold yellow]Target Patient Profile:[/bold yellow] Elena (Diagnosed Celiac, Histamine Intolerance, Dairy Sensitive)")
    console.print(f"[bold yellow]Incoming Recipe to Remix:[/bold yellow] [white]{recipe_title}[/white]")
    console.print(f"[dim]Ingredients to audit: {', '.join(ingredients)}[/dim]\n")

    agent = SafePlateAgent()
    metrics.reset()

    result = agent.remix_recipe(recipe_title, ingredients)

    # 1. Audit Table
    table = Table(title="[Clinical Ingredient Safety Audit]", header_style="bold magenta")
    table.add_column("Original Ingredient", style="cyan", width=18)
    table.add_column("Status", justify="center", width=10)
    table.add_column("SIGHI Score", justify="center", width=12)
    table.add_column("Flagged Reasons", style="dim", width=35)
    table.add_column("Approved Safe Substitute", style="green", width=35)

    for item in result.flagged_ingredients:
        table.add_row(
            item.ingredient,
            "[red]UNSAFE[/red]",
            f"Level {item.sighi_score}",
            "\n".join(item.reasons),
            f"-> {item.chosen_substitute}"
        )

    for ing in ingredients:
        if not any(f.ingredient == ing for f in result.flagged_ingredients):
            table.add_row(
                ing,
                "[green]SAFE[/green]",
                "Level 0",
                "Verified compliant",
                "-"
            )

    console.print(table)

    # 2. Recipe Output Panel
    recipe_text = f"[bold green]{result.safe_title}[/bold green]\n\n"
    recipe_text += "[bold underline]Safe Ingredients:[/bold underline]\n"
    for ing in result.safe_ingredients:
        recipe_text += f" * {ing}\n"
    recipe_text += "\n[bold underline]Preparation & Cooking Instructions:[/bold underline]\n"
    for idx, step in enumerate(result.cooking_instructions, 1):
        recipe_text += f" {idx}. {step}\n"
    recipe_text += "\n[bold red][!] Histamine Rule:[/bold red] Consume immediately fresh; do not reheat leftovers."

    console.print(Panel(recipe_text, title="[Elena-Safe Recipe Remix]", border_style="green"))

    # 3. Sentry Agent Tracing Telemetry Table
    telemetry_table = Table(title="[Sentry Agent Tracing Telemetry]", header_style="bold cyan")
    telemetry_table.add_column("Metric / Telemetry Dimension", style="white")
    telemetry_table.add_column("Observed Value", style="bold yellow", justify="right")
    telemetry_table.add_column("Sentry Trace Operation", style="dim")

    telemetry_table.add_row("End-to-End Pipeline Latency", f"{result.total_latency_ms} ms", "ai.pipeline")
    telemetry_table.add_row("Total Spans Recorded", str(len(metrics.spans)), "distributed_trace")
    telemetry_table.add_row("Tool Calls Executed", str(result.tool_calls_count), "ai.tool_call")
    telemetry_table.add_row("Total Token Footprint", f"{result.total_tokens} tokens", "ai.chat_completions.create")
    telemetry_table.add_row("Prompt Tokens", f"{metrics.total_prompt_tokens}", "gen_ai.usage.prompt_tokens")
    telemetry_table.add_row("Completion Tokens", f"{metrics.total_completion_tokens}", "gen_ai.usage.completion_tokens")
    telemetry_table.add_row("Inference Cost", "$0.0000 USD (Open-Weights)", "gen_ai.cost")
    telemetry_table.add_row("Sentry Tracing Status", "[CONNECTED]" if IS_SENTRY_ENABLED else "[LOCAL TRACE MODE]", "traces_sample_rate=1.0")

    console.print(telemetry_table)


if __name__ == "__main__":
    run_cli()
