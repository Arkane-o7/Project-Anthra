from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import models
from ..database.database import get_db
from ..auth.security import get_current_user
from . import schemas
from .prediction_service import PredictionService

router = APIRouter(
    prefix="/linkedin-x",
    tags=["linkedin-x"],
)

prediction_service = PredictionService()

@router.post("/profiles", response_model=schemas.LinkedInXProfile)
def create_profile(
    profile: schemas.LinkedInXProfileCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new LinkedIn/X profile for the user"""
    # Check if user already has a profile for this platform
    existing_profile = db.query(models.LinkedInXProfile).filter(
        models.LinkedInXProfile.user_id == current_user.id,
        models.LinkedInXProfile.platform == profile.platform
    ).first()
    
    if existing_profile:
        raise HTTPException(
            status_code=400, 
            detail=f"Profile for {profile.platform} already exists"
        )
    
    db_profile = models.LinkedInXProfile(
        user_id=current_user.id,
        **profile.dict()
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

@router.get("/profiles", response_model=List[schemas.LinkedInXProfile])
def get_profiles(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all LinkedIn/X profiles for the current user"""
    profiles = db.query(models.LinkedInXProfile).filter(
        models.LinkedInXProfile.user_id == current_user.id
    ).all()
    return profiles

@router.get("/profiles/{profile_id}", response_model=schemas.LinkedInXProfile)
def get_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get a specific LinkedIn/X profile"""
    profile = db.query(models.LinkedInXProfile).filter(
        models.LinkedInXProfile.id == profile_id,
        models.LinkedInXProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile

@router.post("/profiles/{profile_id}/posts", response_model=schemas.SocialPost)
def add_historical_post(
    profile_id: int,
    post: schemas.SocialPostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Add a historical post for performance tracking"""
    # Verify profile ownership
    profile = db.query(models.LinkedInXProfile).filter(
        models.LinkedInXProfile.id == profile_id,
        models.LinkedInXProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    db_post = models.SocialPost(
        profile_id=profile_id,
        **post.dict()
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@router.get("/profiles/{profile_id}/posts", response_model=List[schemas.SocialPost])
def get_historical_posts(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get historical posts for a profile"""
    # Verify profile ownership
    profile = db.query(models.LinkedInXProfile).filter(
        models.LinkedInXProfile.id == profile_id,
        models.LinkedInXProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    posts = db.query(models.SocialPost).filter(
        models.SocialPost.profile_id == profile_id
    ).order_by(models.SocialPost.posted_at.desc()).all()
    
    return posts

@router.post("/profiles/{profile_id}/predict", response_model=schemas.PredictionResult)
def predict_post_performance(
    profile_id: int,
    prediction_data: schemas.PredictionRequestData,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Predict performance for a new post"""
    # Verify profile ownership
    profile = db.query(models.LinkedInXProfile).filter(
        models.LinkedInXProfile.id == profile_id,
        models.LinkedInXProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Generate prediction
    prediction_result = prediction_service.predict_performance(
        profile=profile,
        content=prediction_data.content,
        image_url=prediction_data.image_url,
        db=db
    )
    
    # Save prediction request for tracking
    db_prediction = models.PredictionRequest(
        profile_id=profile_id,
        content=prediction_data.content,
        image_url=prediction_data.image_url,
        predicted_impressions=prediction_result.predicted_impressions,
        predicted_likes=prediction_result.predicted_reactions["likes"],
        predicted_comments=prediction_result.predicted_reactions["comments"],
        predicted_shares=prediction_result.predicted_reactions["shares"],
        confidence_score=str(prediction_result.confidence_score),
        prediction_factors=prediction_result.factors.dict()
    )
    db.add(db_prediction)
    db.commit()
    
    return prediction_result

@router.get("/profiles/{profile_id}/predictions", response_model=List[schemas.PredictionRequest])
def get_prediction_history(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get prediction history for a profile"""
    # Verify profile ownership
    profile = db.query(models.LinkedInXProfile).filter(
        models.LinkedInXProfile.id == profile_id,
        models.LinkedInXProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    predictions = db.query(models.PredictionRequest).filter(
        models.PredictionRequest.profile_id == profile_id
    ).order_by(models.PredictionRequest.created_at.desc()).all()
    
    return predictions

@router.get("/profiles/{profile_id}/analytics")
def get_profile_analytics(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get analytics and insights for a profile"""
    # Verify profile ownership
    profile = db.query(models.LinkedInXProfile).filter(
        models.LinkedInXProfile.id == profile_id,
        models.LinkedInXProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Get historical posts for analytics
    posts = db.query(models.SocialPost).filter(
        models.SocialPost.profile_id == profile_id
    ).all()
    
    if not posts:
        return {
            "total_posts": 0,
            "average_performance": {},
            "engagement_trends": [],
            "best_performing_content": [],
            "recommendations": [
                "Add some historical posts to get personalized analytics",
                "Try posting consistently to build engagement patterns"
            ]
        }
    
    # Calculate analytics
    total_impressions = sum(post.impressions for post in posts)
    total_likes = sum(post.likes for post in posts)
    total_comments = sum(post.comments for post in posts)
    total_shares = sum(post.shares for post in posts)
    
    avg_impressions = total_impressions / len(posts)
    avg_likes = total_likes / len(posts)
    avg_comments = total_comments / len(posts)
    avg_shares = total_shares / len(posts)
    
    # Find best performing post
    best_post = max(posts, key=lambda p: p.impressions + p.likes * 10 + p.comments * 20 + p.shares * 30)
    
    return {
        "total_posts": len(posts),
        "average_performance": {
            "impressions": round(avg_impressions),
            "likes": round(avg_likes),
            "comments": round(avg_comments),
            "shares": round(avg_shares),
            "engagement_rate": round((total_likes + total_comments + total_shares) / total_impressions * 100, 2) if total_impressions > 0 else 0
        },
        "best_performing_content": {
            "content": best_post.content[:100] + "..." if len(best_post.content) > 100 else best_post.content,
            "impressions": best_post.impressions,
            "likes": best_post.likes,
            "comments": best_post.comments,
            "shares": best_post.shares
        },
        "recommendations": [
            "Post consistently to maintain engagement",
            "Use 1-2 relevant hashtags for better reach",
            "Ask questions to encourage comments",
            "Share visual content when possible"
        ]
    }