from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..database.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    campaigns = relationship("Campaign", back_populates="owner")

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    headline = Column(String)
    body_text = Column(Text)
    image_url = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="campaigns")

class PersonaProfile(Base):
    __tablename__ = "persona_profiles"
    id = Column(Integer, primary_key=True, index=True)
    demographics = Column(JSON)
    psychographics = Column(JSON)
    embedding_vector = Column(String) # This will store the ID from the vector DB

class SimulationRun(Base):
    __tablename__ = "simulation_runs"
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="queued")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class SimulationResult(Base):
    __tablename__ = "simulation_results"
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulation_runs.id"))
    persona_id = Column(Integer, ForeignKey("persona_profiles.id"))
    initial_reaction = Column(Text)
    key_takeaway = Column(Text)
    likelihood_to_engage = Column(String) # Storing as string to avoid float precision issues
    critique = Column(Text)
    sentiment_score = Column(String) # Storing as string
    reasoning = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
