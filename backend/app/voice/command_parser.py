import openai
import json
from typing import Dict, Any, Optional
from .schemas import VoiceCommand, ParsedCommand, CommandType

class CommandParser:
    def __init__(self, api_key: Optional[str] = None):
        self.client = openai.OpenAI(api_key=api_key) if api_key else None
    
    async def parse_command(self, voice_command: VoiceCommand) -> ParsedCommand:
        """Parse natural language voice command into structured action"""
        
        if not self.client:
            # Fallback to simple keyword parsing if no API key
            return self._simple_parse(voice_command.text)
        
        try:
            response = await self._call_openai(voice_command.text)
            return self._parse_openai_response(response)
        except Exception as e:
            print(f"OpenAI parsing failed: {e}")
            return self._simple_parse(voice_command.text)
    
    async def _call_openai(self, command_text: str) -> Dict[str, Any]:
        """Call OpenAI API to parse the command"""
        prompt = f"""
        Parse this voice command into a structured browser action. Return JSON only.
        
        Command: "{command_text}"
        
        Available command types: navigate, click, type, search, fill_form, read_page, scroll
        
        Return format:
        {{
            "type": "command_type",
            "action": "human_readable_action",
            "target": "element_to_target_or_null",
            "value": "text_to_enter_or_null",
            "parameters": {{"key": "value"}}
        }}
        
        Examples:
        - "Go to Google" -> {{"type": "navigate", "action": "Navigate to Google", "target": "https://google.com", "value": null}}
        - "Click the login button" -> {{"type": "click", "action": "Click login button", "target": "login button", "value": null}}
        - "Type my name John" -> {{"type": "type", "action": "Type John", "target": null, "value": "John"}}
        - "Search for wireless headphones" -> {{"type": "search", "action": "Search for wireless headphones", "target": "search", "value": "wireless headphones"}}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
    
    def _parse_openai_response(self, response: Dict[str, Any]) -> ParsedCommand:
        """Convert OpenAI response to ParsedCommand"""
        return ParsedCommand(
            type=CommandType(response.get("type", "navigate")),
            action=response.get("action", ""),
            target=response.get("target"),
            value=response.get("value"),
            parameters=response.get("parameters", {})
        )
    
    def _simple_parse(self, command_text: str) -> ParsedCommand:
        """Simple keyword-based parsing as fallback"""
        text = command_text.lower().strip()
        
        # Navigation commands
        if any(word in text for word in ["go to", "navigate to", "open", "visit"]):
            if "google" in text:
                return ParsedCommand(
                    type=CommandType.NAVIGATE,
                    action="Navigate to Google",
                    target="https://google.com"
                )
            elif "amazon" in text:
                return ParsedCommand(
                    type=CommandType.NAVIGATE,
                    action="Navigate to Amazon",
                    target="https://amazon.com"
                )
            else:
                return ParsedCommand(
                    type=CommandType.NAVIGATE,
                    action=f"Navigate to {text}",
                    target=text
                )
        
        # Search commands
        elif any(word in text for word in ["search for", "find", "look for"]):
            search_term = text.replace("search for", "").replace("find", "").replace("look for", "").strip()
            return ParsedCommand(
                type=CommandType.SEARCH,
                action=f"Search for {search_term}",
                target="search",
                value=search_term
            )
        
        # Click commands
        elif any(word in text for word in ["click", "press", "tap"]):
            target = text.replace("click", "").replace("press", "").replace("tap", "").replace("the", "").strip()
            return ParsedCommand(
                type=CommandType.CLICK,
                action=f"Click {target}",
                target=target
            )
        
        # Type commands
        elif any(word in text for word in ["type", "enter", "write"]):
            # Extract the text to type
            for word in ["type", "enter", "write"]:
                if word in text:
                    value = text.split(word, 1)[1].strip()
                    return ParsedCommand(
                        type=CommandType.TYPE,
                        action=f"Type {value}",
                        value=value
                    )
        
        # Read commands
        elif any(word in text for word in ["read", "tell me", "what does it say"]):
            return ParsedCommand(
                type=CommandType.READ_PAGE,
                action="Read page content"
            )
        
        # Default fallback
        return ParsedCommand(
            type=CommandType.NAVIGATE,
            action=f"Process command: {text}",
            target=text
        )