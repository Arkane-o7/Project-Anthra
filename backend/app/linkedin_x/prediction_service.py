import re
import math
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..database import models
from . import schemas

class PredictionService:
    """Rule-based prediction engine for LinkedIn and X content performance"""
    
    def __init__(self):
        # Platform-specific engagement rates (baseline averages)
        self.platform_rates = {
            "linkedin": {
                "impression_rate": 0.02,  # 2% of followers see the post
                "like_rate": 0.03,        # 3% of impressions get likes
                "comment_rate": 0.005,    # 0.5% of impressions get comments
                "share_rate": 0.002       # 0.2% of impressions get shares
            },
            "twitter": {
                "impression_rate": 0.05,  # 5% of followers see the post
                "like_rate": 0.02,        # 2% of impressions get likes
                "comment_rate": 0.003,    # 0.3% of impressions get comments
                "share_rate": 0.008       # 0.8% of impressions get shares (retweets)
            }
        }
    
    def predict_performance(
        self, 
        profile: models.LinkedInXProfile, 
        content: str, 
        image_url: str = None,
        db: Session = None
    ) -> schemas.PredictionResult:
        """Main prediction method"""
        
        # Get historical performance if available
        historical_posts = []
        if db:
            historical_posts = db.query(models.SocialPost).filter(
                models.SocialPost.profile_id == profile.id
            ).order_by(models.SocialPost.posted_at.desc()).limit(5).all()
        
        # Calculate base metrics
        base_impressions = self._calculate_base_impressions(profile, historical_posts)
        
        # Apply content analysis multipliers
        content_multiplier = self._analyze_content(content, profile.platform)
        
        # Apply image multiplier
        image_multiplier = self._analyze_image(image_url, profile.platform)
        
        # Apply timing and audience factors
        timing_multiplier = self._analyze_timing()
        audience_multiplier = self._analyze_audience(profile)
        
        # Calculate final predictions
        final_multiplier = content_multiplier * image_multiplier * timing_multiplier * audience_multiplier
        
        predicted_impressions = int(base_impressions * final_multiplier)
        
        platform_rates = self.platform_rates[profile.platform]
        predicted_likes = int(predicted_impressions * platform_rates["like_rate"])
        predicted_comments = int(predicted_impressions * platform_rates["comment_rate"])
        predicted_shares = int(predicted_impressions * platform_rates["share_rate"])
        
        # Calculate confidence score
        confidence = self._calculate_confidence(profile, historical_posts, content)
        
        # Generate explanatory factors
        factors = self._generate_factors(
            content, image_url, profile, content_multiplier, 
            image_multiplier, timing_multiplier, audience_multiplier
        )
        
        return schemas.PredictionResult(
            predicted_impressions=predicted_impressions,
            predicted_reactions={
                "likes": predicted_likes,
                "comments": predicted_comments,
                "shares": predicted_shares
            },
            confidence_score=confidence,
            factors=factors
        )
    
    def _calculate_base_impressions(self, profile: models.LinkedInXProfile, historical_posts: List) -> float:
        """Calculate base impression estimate"""
        if historical_posts:
            # Use average of historical performance
            avg_impressions = sum(post.impressions for post in historical_posts) / len(historical_posts)
            return avg_impressions
        else:
            # Use follower count with platform-specific rate
            platform_rate = self.platform_rates[profile.platform]["impression_rate"]
            return profile.follower_count * platform_rate
    
    def _analyze_content(self, content: str, platform: str) -> float:
        """Analyze content and return multiplier (0.5 - 2.0)"""
        multiplier = 1.0
        
        # Content length analysis
        content_length = len(content)
        if platform == "linkedin":
            # LinkedIn optimal length: 100-300 characters
            if 100 <= content_length <= 300:
                multiplier *= 1.2
            elif content_length > 500:
                multiplier *= 0.8
        else:  # Twitter
            # Twitter optimal length: 71-100 characters
            if 71 <= content_length <= 100:
                multiplier *= 1.3
            elif content_length > 200:
                multiplier *= 0.7
        
        # Hashtag analysis
        hashtags = re.findall(r'#\w+', content)
        hashtag_count = len(hashtags)
        if platform == "linkedin":
            if 1 <= hashtag_count <= 3:
                multiplier *= 1.1
            elif hashtag_count > 5:
                multiplier *= 0.9
        else:  # Twitter
            if 1 <= hashtag_count <= 2:
                multiplier *= 1.2
            elif hashtag_count > 3:
                multiplier *= 0.8
        
        # Mention analysis
        mentions = re.findall(r'@\w+', content)
        if mentions:
            multiplier *= 1.1
        
        # Question analysis (drives engagement)
        if '?' in content:
            multiplier *= 1.15
        
        # Call-to-action analysis
        cta_words = ['comment', 'share', 'thoughts', 'opinion', 'agree', 'disagree', 'what do you think']
        if any(word in content.lower() for word in cta_words):
            multiplier *= 1.1
        
        # Emotional trigger words
        emotional_words = ['excited', 'thrilled', 'amazing', 'incredible', 'shocked', 'surprised']
        if any(word in content.lower() for word in emotional_words):
            multiplier *= 1.05
        
        return max(0.5, min(2.0, multiplier))
    
    def _analyze_image(self, image_url: str, platform: str) -> float:
        """Analyze image presence and return multiplier"""
        if image_url:
            # Posts with images generally perform better
            if platform == "linkedin":
                return 1.3  # LinkedIn images boost engagement significantly
            else:  # Twitter
                return 1.2  # Twitter images also help
        return 1.0
    
    def _analyze_timing(self) -> float:
        """Analyze posting timing (simplified for MVP)"""
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()
        
        # Business hours tend to be better for LinkedIn
        # Evening hours better for Twitter
        # This is a simplified heuristic
        if 9 <= hour <= 17 and weekday < 5:  # Business hours, weekday
            return 1.1
        elif 18 <= hour <= 21:  # Evening hours
            return 1.05
        else:
            return 0.95
    
    def _analyze_audience(self, profile: models.LinkedInXProfile) -> float:
        """Analyze audience size and engagement potential"""
        multiplier = 1.0
        
        # Follower count analysis
        if profile.follower_count < 500:
            multiplier *= 0.8  # Smaller audience
        elif 500 <= profile.follower_count <= 5000:
            multiplier *= 1.0  # Sweet spot for engagement
        elif 5000 <= profile.follower_count <= 50000:
            multiplier *= 1.1  # Good reach
        else:
            multiplier *= 0.9  # Larger audiences often have lower engagement rates
        
        return multiplier
    
    def _calculate_confidence(self, profile: models.LinkedInXProfile, historical_posts: List, content: str) -> float:
        """Calculate confidence score for prediction"""
        confidence = 0.5  # Base confidence
        
        # More historical data = higher confidence
        if len(historical_posts) >= 5:
            confidence += 0.3
        elif len(historical_posts) >= 3:
            confidence += 0.2
        elif len(historical_posts) >= 1:
            confidence += 0.1
        
        # Established profile = higher confidence
        if profile.follower_count > 1000:
            confidence += 0.1
        
        # Content analysis confidence
        if len(content) > 50:  # Sufficient content to analyze
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _generate_factors(
        self, 
        content: str, 
        image_url: str, 
        profile: models.LinkedInXProfile,
        content_mult: float,
        image_mult: float, 
        timing_mult: float,
        audience_mult: float
    ) -> schemas.PredictionFactors:
        """Generate explanatory factors for the prediction"""
        
        positive = []
        negative = []
        suggestions = []
        
        # Content factors
        if content_mult > 1.1:
            positive.append("Well-optimized content length for platform")
        elif content_mult < 0.9:
            negative.append("Content length not optimal for platform")
            if profile.platform == "linkedin":
                suggestions.append("Try keeping posts between 100-300 characters for LinkedIn")
            else:
                suggestions.append("Try keeping posts between 71-100 characters for Twitter")
        
        # Hashtag analysis
        hashtags = re.findall(r'#\w+', content)
        if hashtags:
            if len(hashtags) <= 3:
                positive.append(f"Good use of {len(hashtags)} hashtag(s)")
            else:
                negative.append("Too many hashtags may reduce reach")
                suggestions.append("Limit hashtags to 2-3 for better performance")
        else:
            suggestions.append("Consider adding 1-2 relevant hashtags")
        
        # Image factors
        if image_mult > 1.0:
            positive.append("Visual content boosts engagement")
        else:
            suggestions.append("Consider adding an image to increase engagement")
        
        # Engagement triggers
        if '?' in content:
            positive.append("Question encourages audience interaction")
        else:
            suggestions.append("Ask a question to encourage comments")
        
        # Call-to-action
        cta_words = ['comment', 'share', 'thoughts', 'opinion']
        if any(word in content.lower() for word in cta_words):
            positive.append("Clear call-to-action present")
        else:
            suggestions.append("Add a call-to-action to increase engagement")
        
        # Timing factors
        if timing_mult > 1.0:
            positive.append("Good timing for your audience")
        else:
            suggestions.append("Consider posting during peak hours (9-17 weekdays or 18-21 evenings)")
        
        # Audience factors
        if audience_mult > 1.0:
            positive.append("Audience size is in the engagement sweet spot")
        elif profile.follower_count < 500:
            suggestions.append("Focus on growing your follower base for better reach")
        
        return schemas.PredictionFactors(
            positive=positive,
            negative=negative,
            suggestions=suggestions
        )