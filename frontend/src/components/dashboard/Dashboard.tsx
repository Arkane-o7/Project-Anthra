import React, { useState, useEffect } from 'react';
import { LinkedInXProfile, apiClient } from '../../api';
import ProfileForm from '../profile/ProfileForm';
import PredictionForm from '../prediction/PredictionForm';

const Dashboard: React.FC = () => {
  const [profiles, setProfiles] = useState<LinkedInXProfile[]>([]);
  const [selectedProfile, setSelectedProfile] = useState<LinkedInXProfile | null>(null);
  const [showProfileForm, setShowProfileForm] = useState(false);
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfiles();
  }, []);

  useEffect(() => {
    if (selectedProfile) {
      loadAnalytics(selectedProfile.id);
    }
  }, [selectedProfile]);

  const loadProfiles = async () => {
    try {
      const userProfiles = await apiClient.getProfiles();
      setProfiles(userProfiles);
      if (userProfiles.length > 0) {
        setSelectedProfile(userProfiles[0]);
      }
    } catch (error) {
      console.error('Failed to load profiles:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadAnalytics = async (profileId: number) => {
    try {
      const profileAnalytics = await apiClient.getProfileAnalytics(profileId);
      setAnalytics(profileAnalytics);
    } catch (error) {
      console.error('Failed to load analytics:', error);
      setAnalytics(null);
    }
  };

  const handleProfileCreated = (profile: LinkedInXProfile) => {
    setProfiles(prev => [...prev, profile]);
    setSelectedProfile(profile);
    setShowProfileForm(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (profiles.length === 0 && !showProfileForm) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl mx-auto text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Welcome to ANTHRA</h1>
          <p className="text-lg text-gray-600 mb-8">
            Let's start by setting up your social media profile to begin predicting content performance.
          </p>
          <button
            onClick={() => setShowProfileForm(true)}
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
          >
            Create Your First Profile
          </button>
        </div>
      </div>
    );
  }

  if (showProfileForm) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <ProfileForm onProfileCreated={handleProfileCreated} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <h1 className="text-3xl font-bold text-gray-900">ANTHRA Dashboard</h1>
            <div className="flex items-center space-x-4">
              {/* Profile Selector */}
              <select
                value={selectedProfile?.id || ''}
                onChange={(e) => {
                  const profile = profiles.find(p => p.id === parseInt(e.target.value));
                  setSelectedProfile(profile || null);
                }}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                {profiles.map(profile => (
                  <option key={profile.id} value={profile.id}>
                    {profile.platform.charAt(0).toUpperCase() + profile.platform.slice(1)} - {profile.job_title}
                  </option>
                ))}
              </select>
              <button
                onClick={() => setShowProfileForm(true)}
                className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
              >
                Add Profile
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {selectedProfile && (
          <div className="space-y-6">
            {/* Profile Overview */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Profile Overview
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Platform</dt>
                    <dd className="mt-1 text-sm text-gray-900 capitalize">{selectedProfile.platform}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Followers</dt>
                    <dd className="mt-1 text-sm text-gray-900">{selectedProfile.follower_count.toLocaleString()}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Industry</dt>
                    <dd className="mt-1 text-sm text-gray-900">{selectedProfile.industry}</dd>
                  </div>
                </div>
              </div>
            </div>

            {/* Analytics */}
            {analytics && (
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                    Performance Analytics
                  </h3>
                  {analytics.total_posts > 0 ? (
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="bg-blue-50 p-3 rounded-lg text-center">
                          <div className="text-xl font-bold text-blue-600">
                            {analytics.average_performance.impressions}
                          </div>
                          <div className="text-xs text-gray-600">Avg Impressions</div>
                        </div>
                        <div className="bg-green-50 p-3 rounded-lg text-center">
                          <div className="text-xl font-bold text-green-600">
                            {analytics.average_performance.likes}
                          </div>
                          <div className="text-xs text-gray-600">Avg Likes</div>
                        </div>
                        <div className="bg-yellow-50 p-3 rounded-lg text-center">
                          <div className="text-xl font-bold text-yellow-600">
                            {analytics.average_performance.comments}
                          </div>
                          <div className="text-xs text-gray-600">Avg Comments</div>
                        </div>
                        <div className="bg-purple-50 p-3 rounded-lg text-center">
                          <div className="text-xl font-bold text-purple-600">
                            {analytics.average_performance.engagement_rate}%
                          </div>
                          <div className="text-xs text-gray-600">Engagement Rate</div>
                        </div>
                      </div>
                      
                      {analytics.best_performing_content && (
                        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                          <h4 className="font-medium text-gray-900 mb-2">Best Performing Content</h4>
                          <p className="text-sm text-gray-700 mb-2">{analytics.best_performing_content.content}</p>
                          <div className="text-xs text-gray-500">
                            {analytics.best_performing_content.impressions} impressions • {analytics.best_performing_content.likes} likes
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-sm">
                      Add some historical posts to see analytics here.
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Prediction Form */}
            <PredictionForm 
              profileId={selectedProfile.id} 
              platform={selectedProfile.platform}
            />
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;