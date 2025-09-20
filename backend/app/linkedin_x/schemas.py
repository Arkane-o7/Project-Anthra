from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# Profile Schemas
class LinkedInXProfileBase(BaseModel):
    platform: str  # "linkedin" or "twitter"
    follower_count: int
    connection_count: Optional[int] = None  # LinkedIn specific
    industry: str
    job_title: str
    location: str

class LinkedInXProfileCreate(LinkedInXProfileBase):
    pass

class LinkedInXProfile(LinkedInXProfileBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Social Post Schemas
class SocialPostBase(BaseModel):
    content: str
    image_url: Optional[str] = None
    impressions: int
    likes: int
    comments: int
    shares: int
    hashtags: List[str] = []
    mentions: List[str] = []
    posted_at: datetime

class SocialPostCreate(SocialPostBase):
    pass

class SocialPost(SocialPostBase):
    id: int
    profile_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Prediction Schemas
class PredictionRequestData(BaseModel):
    content: str
    image_url: Optional[str] = None

class PredictionFactors(BaseModel):
    positive: List[str]
    negative: List[str]
    suggestions: List[str]

class PredictionResult(BaseModel):
    predicted_impressions: int
    predicted_reactions: Dict[str, int]  # likes, comments, shares
    confidence_score: float
    factors: PredictionFactors

class PredictionRequestCreate(BaseModel):
    profile_id: int
    content: str
    image_url: Optional[str] = None

class PredictionRequest(BaseModel):
    id: int
    profile_id: int
    content: str
    image_url: Optional[str] = None
    predicted_impressions: int
    predicted_likes: int
    predicted_comments: int
    predicted_shares: int
    confidence_score: float
    prediction_factors: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

# Audience Analysis Schemas
class AudienceSegment(BaseModel):
    name: str
    demographics: Dict[str, Any]
    interests: List[str]
    size_estimate: int

class AudienceAnalysis(BaseModel):
    current_audience: List[AudienceSegment]
    suggested_audiences: List[AudienceSegment]
    engagement_patterns: Dict[str, Any]