import React, { useState } from 'react';
import { PredictionResult, apiClient } from '../../api';

interface PredictionFormProps {
  profileId: number;
  platform: 'linkedin' | 'twitter';
}

const PredictionForm: React.FC<PredictionFormProps> = ({ profileId, platform }) => {
  const [content, setContent] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const maxLength = platform === 'twitter' ? 280 : 3000;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await apiClient.predictPostPerformance(
        profileId,
        content,
        imageUrl || undefined
      );
      setPrediction(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate prediction');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setContent('');
    setImageUrl('');
    setPrediction(null);
    setError('');
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          Predict Post Performance
        </h2>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {/* Content Input */}
          <div>
            <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-2">
              Post Content
            </label>
            <textarea
              id="content"
              required
              rows={6}
              maxLength={maxLength}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder={`Write your ${platform} post here...`}
            />
            <div className="mt-2 text-sm text-gray-500">
              {content.length}/{maxLength} characters
            </div>
          </div>

          {/* Image URL (Optional) */}
          <div>
            <label htmlFor="imageUrl" className="block text-sm font-medium text-gray-700 mb-2">
              Image URL (Optional)
            </label>
            <input
              type="url"
              id="imageUrl"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              value={imageUrl}
              onChange={(e) => setImageUrl(e.target.value)}
              placeholder="https://example.com/image.jpg"
            />
          </div>

          <div className="flex space-x-4">
            <button
              type="submit"
              disabled={loading || !content.trim()}
              className="flex-1 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? 'Analyzing...' : 'Predict Performance'}
            </button>
            <button
              type="button"
              onClick={handleReset}
              className="py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Reset
            </button>
          </div>
        </form>
      </div>

      {/* Prediction Results */}
      {prediction && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Prediction Results</h3>
          
          {/* Performance Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-blue-600">
                {prediction.predicted_impressions.toLocaleString()}
              </div>
              <div className="text-sm text-gray-600">Impressions</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-green-600">
                {prediction.predicted_reactions.likes.toLocaleString()}
              </div>
              <div className="text-sm text-gray-600">Likes</div>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-yellow-600">
                {prediction.predicted_reactions.comments.toLocaleString()}
              </div>
              <div className="text-sm text-gray-600">Comments</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-purple-600">
                {prediction.predicted_reactions.shares.toLocaleString()}
              </div>
              <div className="text-sm text-gray-600">
                {platform === 'twitter' ? 'Retweets' : 'Shares'}
              </div>
            </div>
          </div>

          {/* Confidence Score */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Confidence Score</span>
              <span className="text-sm font-medium text-gray-900">
                {Math.round(prediction.confidence_score * 100)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-indigo-600 h-2 rounded-full" 
                style={{ width: `${prediction.confidence_score * 100}%` }}
              />
            </div>
          </div>

          {/* Factors */}
          <div className="space-y-4">
            {/* Positive Factors */}
            {prediction.factors.positive.length > 0 && (
              <div>
                <h4 className="font-medium text-green-800 mb-2">✅ What's Working</h4>
                <ul className="list-disc list-inside space-y-1">
                  {prediction.factors.positive.map((factor, index) => (
                    <li key={index} className="text-green-700 text-sm">{factor}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Negative Factors */}
            {prediction.factors.negative.length > 0 && (
              <div>
                <h4 className="font-medium text-red-800 mb-2">⚠️ Areas of Concern</h4>
                <ul className="list-disc list-inside space-y-1">
                  {prediction.factors.negative.map((factor, index) => (
                    <li key={index} className="text-red-700 text-sm">{factor}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Suggestions */}
            {prediction.factors.suggestions.length > 0 && (
              <div>
                <h4 className="font-medium text-indigo-800 mb-2">💡 Suggestions for Improvement</h4>
                <ul className="list-disc list-inside space-y-1">
                  {prediction.factors.suggestions.map((suggestion, index) => (
                    <li key={index} className="text-indigo-700 text-sm">{suggestion}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default PredictionForm;