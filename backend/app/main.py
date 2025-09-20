from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .auth import routes as auth_routes
from .linkedin_x import routes as linkedin_x_routes

app = FastAPI(title="ANTHRA MVP", description="Predictive Marketing Intelligence Platform")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(linkedin_x_routes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to ANTHRA MVP - Predictive Marketing Intelligence Platform"}
