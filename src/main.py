#!/usr/bin/env python3
"""ASCII Canvas AI - Main CLI Application"""

import os
import sys
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown

from agents.design_recommender import DesignRecommenderAgent, SystemDesign
from agents.ascii_artist import AsciiArtistAgent


console = Console()


def load_environment():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        console.print("[yellow]Warning: No .env file found. Please create one from .env.example[/yellow]")


def display_banner():
    """Display application banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║           ASCII CANVAS AI                             ║
    ║      System Design Diagram Generator                  ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def get_multiline_input(prompt_text: str) -> str:
    """Get multiline input from user"""
    console.print(f"\n[bold]{prompt_text}[/bold]")
    console.print("[dim](Press Ctrl+D or Ctrl+Z when done, or type 'END' on a new line)[/dim]\n")
    
    lines = []
    try:
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
    except EOFError:
        pass
    
    return "\n".join(lines)


def save_diagram(diagram: str, filename: Optional[str] = None):
    """Save diagram to file"""
    output_dir = Path(__file__).parent.parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    if not filename:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"diagram_{timestamp}.txt"
    
    output_path = output_dir / filename
    output_path.write_text(diagram)
    console.print(f"\n[green]✓ Diagram saved to: {output_path}[/green]")


def interactive_mode():
    """Run the application in interactive mode"""
    display_banner()
    
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]Error: OPENAI_API_KEY not found in environment[/red]")
        console.print("Please set it in your .env file or environment variables")
        sys.exit(1)
    
    # Initialize agents
    console.print("\n[cyan]Initializing AI agents...[/cyan]")
    design_agent = DesignRecommenderAgent()
    ascii_agent = AsciiArtistAgent()
    
    console.print("[green]✓ Agents ready![/green]\n")
    
    # Get user's system description
    description = get_multiline_input(
        "📝 Describe your system or application:"
    )
    
    if not description.strip():
        console.print("[red]No description provided. Exiting.[/red]")
        return
    
    # Generate system design
    console.print("\n[cyan]🤖 Agent 1: Analyzing your description and designing system architecture...[/cyan]")
    try:
        system_design = design_agent.recommend_design(description)
    except Exception as e:
        console.print(f"[red]Error generating design: {e}[/red]")
        return
    
    # Display system design
    console.print("\n" + "="*70)
    console.print(Panel(
        f"[bold]{system_design.title}[/bold]\n\n{system_design.description}",
        title="System Design",
        border_style="green"
    ))
    
    console.print("\n[bold]Components:[/bold]")
    for comp in system_design.components:
        console.print(f"  • {comp.name} ({comp.type}): {comp.description}")
    
    console.print("\n[bold]Connections:[/bold]")
    for conn in system_design.connections:
        console.print(f"  • {conn.from_component} → {conn.to_component} ({conn.connection_type})")
        console.print(f"    {conn.description}")
    
    if system_design.notes:
        console.print("\n[bold]Notes:[/bold]")
        for note in system_design.notes:
            console.print(f"  • {note}")
    
    console.print("="*70 + "\n")
    
    # Ask if user wants to refine design
    if Confirm.ask("Would you like to refine this design?", default=False):
        feedback = get_multiline_input("What would you like to change?")
        console.print("\n[cyan]🤖 Refining design...[/cyan]")
        system_design = design_agent.refine_design(system_design, feedback)
        console.print("[green]✓ Design updated![/green]\n")
    
    # Generate ASCII diagram
    console.print("[cyan]🎨 Agent 2: Creating ASCII art diagram...[/cyan]")
    
    style = Prompt.ask(
        "Choose diagram style",
        choices=["detailed", "compact", "flowchart"],
        default="detailed"
    )
    
    try:
        ascii_diagram = ascii_agent.create_ascii_diagram(
            system_design.model_dump(),
            style=style
        )
    except Exception as e:
        console.print(f"[yellow]Anthropic API error: {e}[/yellow]")
        console.print("[cyan]Trying with OpenAI fallback...[/cyan]")
        try:
            ascii_diagram = ascii_agent.create_with_openai_fallback(
                system_design.model_dump(),
                style=style
            )
        except Exception as e2:
            console.print(f"[red]Error generating ASCII diagram: {e2}[/red]")
            return
    
    # Display ASCII diagram
    console.print("\n" + "="*70)
    console.print(ascii_diagram)
    console.print("="*70 + "\n")
    
    # Save option
    if Confirm.ask("Would you like to save this diagram?", default=True):
        filename = Prompt.ask("Enter filename (or press Enter for auto-generated)", default="")
        if filename and not filename.endswith(".txt"):
            filename += ".txt"
        save_diagram(ascii_diagram, filename if filename else None)
    
    console.print("\n[bold green]✨ Done! Thank you for using ASCII Canvas AI[/bold green]\n")


def batch_mode(description_file: str, output_file: Optional[str] = None):
    """Run in batch mode with file input"""
    load_environment()
    
    description_path = Path(description_file)
    if not description_path.exists():
        console.print(f"[red]Error: File not found: {description_file}[/red]")
        sys.exit(1)
    
    description = description_path.read_text()
    
    console.print("[cyan]Initializing agents...[/cyan]")
    design_agent = DesignRecommenderAgent()
    ascii_agent = AsciiArtistAgent()
    
    console.print("[cyan]Generating design...[/cyan]")
    system_design = design_agent.recommend_design(description)
    
    console.print("[cyan]Creating ASCII diagram...[/cyan]")
    ascii_diagram = ascii_agent.create_ascii_diagram(system_design.model_dump())
    
    if output_file:
        Path(output_file).write_text(ascii_diagram)
        console.print(f"[green]✓ Saved to: {output_file}[/green]")
    else:
        console.print("\n" + ascii_diagram)


def main():
    """Main entry point"""
    load_environment()
    
    if len(sys.argv) > 1:
        # Batch mode
        description_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        batch_mode(description_file, output_file)
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
