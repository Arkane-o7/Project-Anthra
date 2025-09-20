// API configuration and utilities
const API_BASE_URL = 'http://localhost:8000';

export interface User {
  id: number;
  email: string;
  is_active: boolean;
}

export interface LinkedInXProfile {
  id: number;
  user_id: number;
  platform: 'linkedin' | 'twitter';
  follower_count: number;
  connection_count?: number;
  industry: string;
  job_title: string;
  location: string;
  created_at: string;
}

export interface SocialPost {
  id: number;
  profile_id: number;
  content: string;
  image_url?: string;
  impressions: number;
  likes: number;
  comments: number;
  shares: number;
  hashtags: string[];
  mentions: string[];
  posted_at: string;
  created_at: string;
}

export interface PredictionResult {
  predicted_impressions: number;
  predicted_reactions: {
    likes: number;
    comments: number;
    shares: number;
  };
  confidence_score: number;
  factors: {
    positive: string[];
    negative: string[];
    suggestions: string[];
  };
}

class APIClient {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('token', token);
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('token');
    }
    return this.token;
  }

  private async request(endpoint: string, options: RequestInit = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = this.getToken();
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Auth methods
  async register(email: string, password: string): Promise<User> {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async login(email: string, password: string): Promise<{ access_token: string; token_type: string }> {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/auth/token`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(error.detail || 'Login failed');
    }

    return response.json();
  }

  // LinkedIn/X Profile methods
  async createProfile(profile: Omit<LinkedInXProfile, 'id' | 'user_id' | 'created_at'>): Promise<LinkedInXProfile> {
    return this.request('/linkedin-x/profiles', {
      method: 'POST',
      body: JSON.stringify(profile),
    });
  }

  async getProfiles(): Promise<LinkedInXProfile[]> {
    return this.request('/linkedin-x/profiles');
  }

  async getProfile(profileId: number): Promise<LinkedInXProfile> {
    return this.request(`/linkedin-x/profiles/${profileId}`);
  }

  // Social Posts methods
  async addHistoricalPost(profileId: number, post: Omit<SocialPost, 'id' | 'profile_id' | 'created_at'>): Promise<SocialPost> {
    return this.request(`/linkedin-x/profiles/${profileId}/posts`, {
      method: 'POST',
      body: JSON.stringify(post),
    });
  }

  async getHistoricalPosts(profileId: number): Promise<SocialPost[]> {
    return this.request(`/linkedin-x/profiles/${profileId}/posts`);
  }

  // Prediction methods
  async predictPostPerformance(profileId: number, content: string, imageUrl?: string): Promise<PredictionResult> {
    return this.request(`/linkedin-x/profiles/${profileId}/predict`, {
      method: 'POST',
      body: JSON.stringify({ content, image_url: imageUrl }),
    });
  }

  async getProfileAnalytics(profileId: number): Promise<any> {
    return this.request(`/linkedin-x/profiles/${profileId}/analytics`);
  }
}

export const apiClient = new APIClient();