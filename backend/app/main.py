from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .auth import routes as auth_routes
from .voice import routes as voice_routes

app = FastAPI(
    title="ANTHRA Voice Accessibility API",
    description="Voice-controlled web accessibility tool for visually impaired users",
    version="1.0.0"
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(voice_routes.router)

@app.get("/")
def read_root():
    return {
        "message": "ANTHRA Voice Accessibility API",
        "version": "1.0.0",
        "endpoints": {
            "voice": "/voice",
            "auth": "/auth",
            "docs": "/docs",
            "websocket": "/voice/ws"
        }
    }
