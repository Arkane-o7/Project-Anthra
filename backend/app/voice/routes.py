from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any
import json
import uuid
from .service import voice_service, websocket_handler
from .schemas import VoiceCommand, VoiceResponse

router = APIRouter(prefix="/voice", tags=["voice"])

# REST API endpoints
@router.post("/session", response_model=Dict[str, str])
async def create_voice_session():
    """Create a new voice accessibility session"""
    session_id = await voice_service.start_session()
    return {"session_id": session_id, "status": "created"}

@router.delete("/session/{session_id}")
async def end_voice_session(session_id: str):
    """End a voice accessibility session"""
    await voice_service.end_session(session_id)
    return {"status": "ended"}

@router.get("/session/{session_id}/status")
async def get_session_status(session_id: str):
    """Get the status of a voice accessibility session"""
    status = await voice_service.get_session_status(session_id)
    if status.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Session not found")
    return status

@router.post("/session/{session_id}/command", response_model=VoiceResponse)
async def process_voice_command(session_id: str, command: VoiceCommand):
    """Process a voice command in a session"""
    response = await voice_service.process_voice_command(session_id, command.text)
    return response

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "voice_accessibility"}

# WebSocket endpoint for real-time communication
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time voice communication"""
    await websocket.accept()
    session_id = None
    
    try:
        # Register the client and get session ID
        session_id = await websocket_handler.register_client(websocket)
        
        while True:
            # Wait for messages from client
            message = await websocket.receive_text()
            await websocket_handler.handle_message(websocket, message, session_id)
            
    except WebSocketDisconnect:
        print(f"WebSocket client disconnected: session {session_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Server error: {str(e)}"
        }))
    finally:
        # Clean up
        if session_id:
            await websocket_handler.unregister_client(websocket, session_id)