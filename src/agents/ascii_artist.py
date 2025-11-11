"""ASCII Artist Agent - Converts system designs to ASCII art diagrams"""

import os
from typing import Optional
from anthropic import Anthropic


class AsciiArtistAgent:
    """AI Agent that converts system designs into beautiful ASCII diagrams"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the ASCII Artist Agent
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Claude model to use (defaults to ASCII_MODEL env var or claude-sonnet-4-5-20250929)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model or os.getenv("ASCII_MODEL", "claude-sonnet-4-5-20250929")
        self.client = Anthropic(api_key=self.api_key)
        
    def create_ascii_diagram(self, system_design: dict, style: str = "detailed") -> str:
        """
        Generate an ASCII art diagram from a system design
        
        Args:
            system_design: Dictionary containing system design (from SystemDesign.model_dump())
            style: Style of diagram ("detailed", "compact", "flowchart")
            
        Returns:
            ASCII art diagram as a string
        """
        import json
        design_json = json.dumps(system_design, indent=2)
        
        style_instructions = {
            "detailed": "Create a detailed, spacious diagram with boxes and clear connections. Use box-drawing characters.",
            "compact": "Create a compact diagram that fits in ~80 characters width. Be space-efficient.",
            "flowchart": "Create a flowchart-style diagram showing the flow of data/requests through the system."
        }
        
        system_prompt = """You are an expert at creating beautiful ASCII art diagrams for system architectures.

Your diagrams should:
- Use box-drawing characters (─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼ ═ ║ ╔ ╗ ╚ ╝)
- Clearly show all components as labeled boxes
- Show connections between components with arrows (→ ← ↔ ↓ ↑)
- Include connection labels where helpful
- Be aesthetically pleasing and easy to understand
- Maintain proper alignment and spacing
- Add a legend if needed for symbols

Be creative but clear. The diagram should be professional and immediately understandable."""

        user_prompt = f"""Create an ASCII art diagram for this system design:

{design_json}

Style preference: {style_instructions.get(style, style_instructions['detailed'])}

Requirements:
1. Show all components from the design
2. Indicate all connections with appropriate arrows
3. Label connection types where space permits
4. Add a title at the top
5. Optionally add notes at the bottom if they're important

Create a beautiful, clear ASCII diagram now:"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=0.8,
            messages=[
                {
                    "role": "user",
                    "content": f"{system_prompt}\n\n{user_prompt}"
                }
            ]
        )
        
        return message.content[0].text
    
    def refine_diagram(self, current_diagram: str, system_design: dict, feedback: str) -> str:
        """
        Refine an existing ASCII diagram based on feedback
        
        Args:
            current_diagram: The current ASCII diagram
            system_design: The system design dict
            feedback: User feedback for refinement
            
        Returns:
            Updated ASCII diagram
        """
        import json
        design_json = json.dumps(system_design, indent=2)
        
        system_prompt = "You are an expert at creating and refining ASCII art diagrams."
        
        user_prompt = f"""Current diagram:
{current_diagram}

System design:
{design_json}

User feedback:
{feedback}

Please update the ASCII diagram based on this feedback while maintaining the quality and clarity.
Create the improved diagram now:"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=0.8,
            messages=[
                {
                    "role": "user", 
                    "content": f"{system_prompt}\n\n{user_prompt}"
                }
            ]
        )
        
        return message.content[0].text
    
    def create_with_openai_fallback(self, system_design: dict, style: str = "detailed") -> str:
        """
        Create ASCII diagram with OpenAI as fallback if Anthropic is not available
        
        Args:
            system_design: Dictionary containing system design
            style: Style of diagram
            
        Returns:
            ASCII art diagram as a string
        """
        try:
            return self.create_ascii_diagram(system_design, style)
        except Exception as e:
            print(f"Anthropic API error: {e}")
            print("Falling back to OpenAI...")
            
            from openai import OpenAI
            openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            import json
            design_json = json.dumps(system_design, indent=2)
            
            style_instructions = {
                "detailed": "Create a detailed, spacious diagram with boxes and clear connections.",
                "compact": "Create a compact diagram that fits in ~80 characters width.",
                "flowchart": "Create a flowchart-style diagram showing data/request flow."
            }
            
            prompt = f"""Create an ASCII art diagram for this system design:

{design_json}

Style: {style_instructions.get(style, style_instructions['detailed'])}

Use box-drawing characters (─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼) and arrows (→ ← ↔ ↓ ↑).
Make it clear, professional, and aesthetically pleasing."""

            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at creating ASCII art diagrams."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8
            )
            
            return response.choices[0].message.content
