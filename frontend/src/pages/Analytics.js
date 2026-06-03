import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import './Analytics.css';

function Analytics({ user }) {
  const navigate = useNavigate();
  const [photos, setPhotos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!user) {
      navigate('/');
    } else {
      fetchUserPhotos();
    }
  }, [user, navigate]);

  const fetchUserPhotos = async () => {
    if (!user?.token) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/photos/user', {
        headers: {
          Authorization: `Bearer ${user.token}`
        }
      });
      
      setPhotos(response.data);
      setError('');
    } catch (err) {
      console.error('Error fetching photos:', err);
      setError('Failed to load analytics data');
      setPhotos([]);
    } finally {
      setLoading(false);
    }
  };

  // Calculate analytics from user photos
  const calculateAnalytics = () => {
    if (photos.length === 0) {
      return {
        totalPhotos: 0,
        avgSmileScore: 0,
        avgQuality: 0,
        bestPhotos: 0,
        smileTrendData: [],
        emotionData: [],
        qualityData: [],
        ageDistribution: []
      };
    }

    // Group by session for trend data
    const sessionGroups = {};
    photos.forEach(photo => {
      if (!sessionGroups[photo.session_id]) {
        sessionGroups[photo.session_id] = [];
      }
      sessionGroups[photo.session_id].push(photo);
    });

    // Calculate smile trend by session
    const smileTrendData = Object.entries(sessionGroups)
      .map(([sessionId, sessionPhotos], index) => {
        const avgSmile = sessionPhotos.reduce((sum, p) => sum + (p.smile_score || 0), 0) / sessionPhotos.length;
        return {
          session: `Session ${index + 1}`,
          score: Math.round(avgSmile)
        };
      })
      .slice(-5); // Last 5 sessions

    // Calculate average scores
    const validSmileScores = photos.filter(p => p.smile_score).map(p => p.smile_score);
    const validFinalScores = photos.filter(p => p.final_score).map(p => p.final_score);
    
    const avgSmileScore = validSmileScores.length > 0
      ? Math.round(validSmileScores.reduce((a, b) => a + b, 0) / validSmileScores.length)
      : 0;
    
    const avgQuality = validFinalScores.length > 0
      ? Math.round(validFinalScores.reduce((a, b) => a + b, 0) / validFinalScores.length)
      : 0;

    // Count best photos
    const bestPhotos = photos.filter(p => p.is_best_in_session).length;

    // Quality metrics
    const qualityData = [
      {
        category: 'Lighting',
        score: Math.round(photos.reduce((sum, p) => sum + (p.lighting_score || 0), 0) / photos.length)
      },
      {
        category: 'Sharpness',
        score: Math.round(photos.reduce((sum, p) => sum + (p.sharpness_score || 0), 0) / photos.length)
      },
      {
        category: 'Alignment',
        score: Math.round(photos.reduce((sum, p) => sum + (p.alignment_score || 0), 0) / photos.length)
      },
      {
        category: 'Smile',
        score: avgSmileScore
      }
    ];

    // Age distribution
    const ageCategories = {};
    photos.forEach(photo => {
      if (photo.age_category) {
        ageCategories[photo.age_category] = (ageCategories[photo.age_category] || 0) + 1;
      }
    });

    const ageDistribution = Object.entries(ageCategories).map(([category, count]) => ({
      range: category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
      count
    }));

    // Emotion distribution based on smile scores
    // Map smile scores to our emotion categories: cheerful, positive, recovering, neutral, low_affect
    const emotionCounts = {
      cheerful: 0,      // smile_score >= 85
      positive: 0,      // smile_score 70-84
      recovering: 0,    // smile_score 55-69
      neutral: 0,       // smile_score 40-54
      low_affect: 0     // smile_score < 40
    };

    photos.forEach(photo => {
      if (photo.smile_score) {
        if (photo.smile_score >= 85) {
          emotionCounts.cheerful++;
        } else if (photo.smile_score >= 70) {
          emotionCounts.positive++;
        } else if (photo.smile_score >= 55) {
          emotionCounts.recovering++;
        } else if (photo.smile_score >= 40) {
          emotionCounts.neutral++;
        } else {
          emotionCounts.low_affect++;
        }
      }
    });

    const emotionData = [
      { name: 'Cheerful', value: emotionCounts.cheerful },
      { name: 'Positive', value: emotionCounts.positive },
      { name: 'Recovering', value: emotionCounts.recovering },
      { name: 'Neutral', value: emotionCounts.neutral },
      { name: 'Low Affect', value: emotionCounts.low_affect }
    ].filter(item => item.value > 0); // Only show categories with data

    return {
      totalPhotos: photos.length,
      avgSmileScore,
      avgQuality,
      bestPhotos,
      smileTrendData,
      emotionData,
      qualityData,
      ageDistribution
    };
  };

  const analytics = calculateAnalytics();
  const COLORS = ['#F97316', '#ea580c', '#fb923c', '#fdba74', '#fed7aa'];

  if (!user) {
    return null;
  }

  return (
    <motion.div
      className="page analytics-page"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="analytics-container">
        <motion.div
          className="analytics-header"
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <h1 className="analytics-title">Analytics Dashboard</h1>
          <p className="analytics-subtitle">Insights from your photo sessions</p>
        </motion.div>

        {loading ? (
          <div className="analytics-loading">
            <div className="spinner"></div>
            <p>Loading analytics...</p>
          </div>
        ) : error ? (
          <div className="analytics-error">
            <p>{error}</p>
            <button className="btn btn-primary" onClick={fetchUserPhotos}>
              Retry
            </button>
          </div>
        ) : photos.length === 0 ? (
          <div className="empty-analytics">
            <div className="empty-icon">📊</div>
            <p>No data yet. Start capturing photos to see analytics!</p>
            <button
              className="btn btn-primary"
              onClick={() => navigate('/camera')}
            >
              Take a Photo
            </button>
          </div>
        ) : (
          <>
            <motion.div
              className="stats-grid"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <div className="stat-card">
                <div className="stat-icon">📸</div>
                <div className="stat-content">
                  <div className="stat-value">{analytics.totalPhotos}</div>
                  <div className="stat-label">Total Photos</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">😊</div>
                <div className="stat-content">
                  <div className="stat-value">{analytics.avgSmileScore}%</div>
                  <div className="stat-label">Avg Smile Score</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">⭐</div>
                <div className="stat-content">
                  <div className="stat-value">{analytics.avgQuality}%</div>
                  <div className="stat-label">Avg Quality</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">🏆</div>
                <div className="stat-content">
                  <div className="stat-value">{analytics.bestPhotos}</div>
                  <div className="stat-label">Best Photos</div>
                </div>
              </div>
            </motion.div>

            <motion.div
              className="charts-grid"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.4 }}
            >
              {analytics.smileTrendData.length > 0 && (
                <div className="chart-card">
                  <h3 className="chart-title">Smile Strength Trend</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <LineChart data={analytics.smileTrendData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="session" stroke="#94A3B8" />
                      <YAxis stroke="#94A3B8" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#1E293B', 
                          border: '1px solid #334155',
                          borderRadius: '8px'
                        }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="score" 
                        stroke="#F97316" 
                        strokeWidth={3}
                        dot={{ fill: '#F97316', r: 6 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}

              <div className="chart-card">
                <h3 className="chart-title">Emotion Distribution</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={analytics.emotionData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {analytics.emotionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1E293B', 
                        border: '1px solid #334155',
                        borderRadius: '8px'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="chart-card">
                <h3 className="chart-title">Average Portrait Quality</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={analytics.qualityData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="category" stroke="#94A3B8" />
                    <YAxis stroke="#94A3B8" />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1E293B', 
                        border: '1px solid #334155',
                        borderRadius: '8px'
                      }}
                    />
                    <Bar dataKey="score" fill="#F97316" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {analytics.ageDistribution.length > 0 && (
                <div className="chart-card">
                  <h3 className="chart-title">Age Category Distribution</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={analytics.ageDistribution}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="range" stroke="#94A3B8" />
                      <YAxis stroke="#94A3B8" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#1E293B', 
                          border: '1px solid #334155',
                          borderRadius: '8px'
                        }}
                      />
                      <Bar dataKey="count" fill="#ea580c" radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </motion.div>
          </>
        )}
      </div>
    </motion.div>
  );
}

export default Analytics;
