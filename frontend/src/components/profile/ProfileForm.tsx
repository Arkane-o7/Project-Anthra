import React, { useState } from 'react';
import { LinkedInXProfile, apiClient } from '../../api';

interface ProfileFormProps {
  onProfileCreated: (profile: LinkedInXProfile) => void;
}

const ProfileForm: React.FC<ProfileFormProps> = ({ onProfileCreated }) => {
  const [platform, setPlatform] = useState<'linkedin' | 'twitter'>('linkedin');
  const [followerCount, setFollowerCount] = useState('');
  const [connectionCount, setConnectionCount] = useState('');
  const [industry, setIndustry] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const profileData = {
        platform,
        follower_count: parseInt(followerCount),
        connection_count: platform === 'linkedin' && connectionCount ? parseInt(connectionCount) : undefined,
        industry,
        job_title: jobTitle,
        location,
      };

      const profile = await apiClient.createProfile(profileData);
      onProfileCreated(profile);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Create Your Social Media Profile</h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Platform Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Platform
          </label>
          <div className="flex space-x-4">
            <label className="flex items-center">
              <input
                type="radio"
                value="linkedin"
                checked={platform === 'linkedin'}
                onChange={(e) => setPlatform(e.target.value as 'linkedin')}
                className="mr-2"
              />
              LinkedIn
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="twitter"
                checked={platform === 'twitter'}
                onChange={(e) => setPlatform(e.target.value as 'twitter')}
                className="mr-2"
              />
              X (Twitter)
            </label>
          </div>
        </div>

        {/* Follower Count */}
        <div>
          <label htmlFor="followerCount" className="block text-sm font-medium text-gray-700">
            Follower Count
          </label>
          <input
            type="number"
            id="followerCount"
            required
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            value={followerCount}
            onChange={(e) => setFollowerCount(e.target.value)}
            placeholder="e.g., 1500"
          />
        </div>

        {/* Connection Count (LinkedIn only) */}
        {platform === 'linkedin' && (
          <div>
            <label htmlFor="connectionCount" className="block text-sm font-medium text-gray-700">
              Connection Count
            </label>
            <input
              type="number"
              id="connectionCount"
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              value={connectionCount}
              onChange={(e) => setConnectionCount(e.target.value)}
              placeholder="e.g., 500"
            />
          </div>
        )}

        {/* Industry */}
        <div>
          <label htmlFor="industry" className="block text-sm font-medium text-gray-700">
            Industry
          </label>
          <input
            type="text"
            id="industry"
            required
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            value={industry}
            onChange={(e) => setIndustry(e.target.value)}
            placeholder="e.g., Technology, Marketing, Finance"
          />
        </div>

        {/* Job Title */}
        <div>
          <label htmlFor="jobTitle" className="block text-sm font-medium text-gray-700">
            Job Title
          </label>
          <input
            type="text"
            id="jobTitle"
            required
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            value={jobTitle}
            onChange={(e) => setJobTitle(e.target.value)}
            placeholder="e.g., Marketing Manager, Software Developer"
          />
        </div>

        {/* Location */}
        <div>
          <label htmlFor="location" className="block text-sm font-medium text-gray-700">
            Location
          </label>
          <input
            type="text"
            id="location"
            required
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="e.g., San Francisco, CA"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          {loading ? 'Creating Profile...' : 'Create Profile'}
        </button>
      </form>
    </div>
  );
};

export default ProfileForm;