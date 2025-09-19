import asyncio
import json
import uuid
from typing import Dict, Any, Set
from .command_parser import CommandParser
from .mock_browser_service import MockBrowserService  # Use mock service for now
from .schemas import VoiceCommand, VoiceResponse, CommandType

class VoiceAccessibilityService:
    def __init__(self, openai_api_key: str = None):
        self.command_parser = CommandParser(openai_api_key)
        self.browser_service = MockBrowserService()  # Use mock service
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
    async def start_session(self, session_id: str = None) -> str:
        """Start a new voice accessibility session"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        self.active_sessions[session_id] = {
            "browser_initialized": False,
            "conversation_history": [],
            "current_context": {}
        }
        
        return session_id
    
    async def end_session(self, session_id: str):
        """End a voice accessibility session"""
        if session_id in self.active_sessions:
            await self.browser_service.close()
            del self.active_sessions[session_id]
    
    async def process_voice_command(self, session_id: str, command_text: str) -> VoiceResponse:
        """Process a voice command and execute the corresponding action"""
        try:
            if session_id not in self.active_sessions:
                return VoiceResponse(
                    message="Session not found. Please start a new session.",
                    success=False
                )
            
            # Parse the voice command
            voice_command = VoiceCommand(text=command_text)
            parsed_command = await self.command_parser.parse_command(voice_command)
            
            # Add to conversation history
            session = self.active_sessions[session_id]
            session["conversation_history"].append({
                "user_input": command_text,
                "parsed_command": parsed_command.dict()
            })
            
            # Initialize browser if needed
            if not session["browser_initialized"]:
                if await self.browser_service.initialize():
                    session["browser_initialized"] = True
                else:
                    return VoiceResponse(
                        message="Failed to initialize browser. Please try again.",
                        success=False
                    )
            
            # Execute the command
            response = await self._execute_command(parsed_command)
            
            # Add response to history
            session["conversation_history"][-1]["response"] = response.dict()
            
            return response
            
        except Exception as e:
            return VoiceResponse(
                message=f"An error occurred: {str(e)}",
                success=False
            )
    
    async def _execute_command(self, command) -> VoiceResponse:
        """Execute a parsed command using the browser service"""
        try:
            if command.type == CommandType.NAVIGATE:
                return await self.browser_service.navigate(command.target or command.value or "")
            
            elif command.type == CommandType.CLICK:
                return await self.browser_service.click_element(command.target or "")
            
            elif command.type == CommandType.TYPE:
                return await self.browser_service.type_text(command.value or "", command.target)
            
            elif command.type == CommandType.SEARCH:
                return await self.browser_service.search(command.value or "")
            
            elif command.type == CommandType.READ_PAGE:
                page_content = await self.browser_service.get_page_content()
                reading_text = self._format_page_for_reading(page_content)
                return VoiceResponse(
                    message=reading_text,
                    success=True,
                    data=page_content.dict()
                )
            
            else:
                return VoiceResponse(
                    message=f"Command type '{command.type}' is not yet implemented.",
                    success=False
                )
                
        except Exception as e:
            return VoiceResponse(
                message=f"Failed to execute command: {str(e)}",
                success=False
            )
    
    def _format_page_for_reading(self, page_content) -> str:
        """Format page content for text-to-speech"""
        reading_parts = []
        
        if hasattr(page_content, 'title') and page_content.title:
            reading_parts.append(f"Page title: {page_content.title}")
        
        if hasattr(page_content, 'text') and page_content.text:
            # Limit text length for better UX
            text = page_content.text[:500]
            if len(page_content.text) > 500:
                text += "... and more content available."
            reading_parts.append(f"Page content: {text}")
        
        if hasattr(page_content, 'links') and page_content.links:
            link_count = len(page_content.links)
            if link_count > 0:
                reading_parts.append(f"Found {link_count} links on this page.")
                # Read first 3 links
                for i, link in enumerate(page_content.links[:3]):
                    if isinstance(link, dict) and link.get("text"):
                        reading_parts.append(f"Link {i+1}: {link['text']}")
        
        return " ".join(reading_parts) if reading_parts else "No content found on this page."
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get the status of a voice accessibility session"""
        if session_id not in self.active_sessions:
            return {"status": "not_found"}
        
        session = self.active_sessions[session_id]
        return {
            "status": "active",
            "browser_initialized": session["browser_initialized"],
            "conversation_count": len(session["conversation_history"]),
            "current_url": self.browser_service.current_url if self.browser_service.page else None
        }

class WebSocketVoiceHandler:
    def __init__(self, voice_service: VoiceAccessibilityService):
        self.voice_service = voice_service
        self.connected_clients: Set = set()
    
    async def register_client(self, websocket):
        """Register a new WebSocket client"""
        try:
            self.connected_clients.add(websocket)
            
            # Start a new session for this client
            session_id = await self.voice_service.start_session()
            
            # Send session info to client
            await websocket.send_text(json.dumps({
                "type": "session_started",
                "session_id": session_id,
                "message": "Voice accessibility session started. You can now speak commands."
            }))
            
            return session_id
        except Exception as e:
            print(f"Error in register_client: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    async def unregister_client(self, websocket, session_id: str = None):
        """Unregister a WebSocket client"""
        self.connected_clients.discard(websocket)
        if session_id:
            await self.voice_service.end_session(session_id)
    
    async def handle_message(self, websocket, message: str, session_id: str):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "voice_command":
                command_text = data.get("text", "")
                response = await self.voice_service.process_voice_command(session_id, command_text)
                
                await websocket.send_text(json.dumps({
                    "type": "command_response",
                    "response": response.dict()
                }))
            
            elif message_type == "get_status":
                status = await self.voice_service.get_session_status(session_id)
                await websocket.send_text(json.dumps({
                    "type": "status_response",
                    "status": status
                }))
            
            else:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }))
                
        except json.JSONDecodeError:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Invalid JSON message"
            }))
        except Exception as e:
            print(f"Error in handle_message: {str(e)}")
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Error processing message: {str(e)}"
            }))

# Global service instance
voice_service = VoiceAccessibilityService()
websocket_handler = WebSocketVoiceHandler(voice_service)