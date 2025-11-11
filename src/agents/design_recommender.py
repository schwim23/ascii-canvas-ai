"""Design Recommender Agent - Converts text descriptions to system designs"""

import os
from typing import Optional
from openai import OpenAI
from pydantic import BaseModel


class SystemComponent(BaseModel):
    """Represents a component in the system design"""
    name: str
    type: str  # e.g., "service", "database", "api", "queue", "cache"
    description: str


class Connection(BaseModel):
    """Represents a connection between components"""
    from_component: str
    to_component: str
    connection_type: str  # e.g., "http", "grpc", "async", "sync"
    description: str


class SystemDesign(BaseModel):
    """Complete system design recommendation"""
    title: str
    description: str
    components: list[SystemComponent]
    connections: list[Connection]
    notes: list[str]


class DesignRecommenderAgent:
    """AI Agent that recommends system designs based on text descriptions"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize the Design Recommender Agent
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: OpenAI model to use
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("DESIGN_MODEL", "gpt-4")
        self.client = OpenAI(api_key=self.api_key)
        
    def recommend_design(self, user_description: str) -> SystemDesign:
        """
        Generate a system design recommendation from user description
        
        Args:
            user_description: Natural language description of the system
            
        Returns:
            SystemDesign object with components and connections
        """
        system_prompt = """You are an expert system architect. Given a description of an application or system,
you must analyze it and recommend a comprehensive system design.

Your response should include:
1. A clear title for the system
2. A summary description
3. All major components (services, databases, APIs, queues, caches, etc.)
4. Connections between components with their types
5. Important architectural notes or considerations

Be thorough but focused on the most important architectural elements.
Think about scalability, reliability, and best practices."""

        user_prompt = f"""Please analyze this system description and provide a detailed system design:

{user_description}

Respond with a JSON object in this exact format:
{{
  "title": "System Title",
  "description": "Brief system description",
  "components": [
    {{
      "name": "Component Name",
      "type": "service|database|api|queue|cache|load_balancer|cdn|storage",
      "description": "What this component does"
    }}
  ],
  "connections": [
    {{
      "from_component": "Source Component Name",
      "to_component": "Target Component Name", 
      "connection_type": "http|grpc|async|sync|websocket",
      "description": "What data/requests flow through this connection"
    }}
  ],
  "notes": [
    "Important architectural consideration 1",
    "Important architectural consideration 2"
  ]
}}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        import json
        design_data = json.loads(response.choices[0].message.content)
        return SystemDesign(**design_data)
    
    def refine_design(self, current_design: SystemDesign, feedback: str) -> SystemDesign:
        """
        Refine an existing design based on user feedback
        
        Args:
            current_design: The current system design
            feedback: User feedback for refinement
            
        Returns:
            Updated SystemDesign
        """
        system_prompt = "You are an expert system architect helping refine a system design based on feedback."
        
        user_prompt = f"""Current design:
{current_design.model_dump_json(indent=2)}

User feedback:
{feedback}

Please update the design based on this feedback. Respond with the complete updated design in the same JSON format."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        import json
        design_data = json.loads(response.choices[0].message.content)
        return SystemDesign(**design_data)
