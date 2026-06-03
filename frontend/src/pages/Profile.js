import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { auth, signOutUser } from '../firebase';
import axios from 'axios';
import './Profile.css';

function Profile({ user, firebaseUser, onLogout }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [backendUser, setBackendUser] = useState(null);
  const [error, setError] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    phone_number: '',
    country: '',
    preferred_market: ''
  });

  useEffect(() => {
    fetchBackendProfile();
  }, [user]);

  const fetchBackendProfile = async () => {
    if (!user?.token) {
      setLoading(false);
      return;
    }

    try {
      const response = await axios.get('http://localhost:8000/api/auth/me', {
        headers: {
          Authorization: `Bearer ${user.token}`
        }
      });
      setBackendUser(response.data);
      setEditForm({
        phone_number: response.data.phone_number || '',
        country: response.data.country || '',
        preferred_market: response.data.preferred_market || 'US'
      });
    } catch (err) {
      console.error('Error fetching backend profile:', err);
      setError('Could not load backend profile data');
    } finally {
      setLoading(false);
    }
  };

  const handleEditChange = (e) => {
    setEditForm({
      ...editForm,
      [e.target.name]: e.target.value
    });
  };

  const handleSaveProfile = async () => {
    if (!user?.token) {
      setError('Please login to backend to edit profile');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Send profile update
      await axios.put(
        'http://localhost:8000/api/auth/profile',
        {
          phone_number: editForm.phone_number || '',
          country: editForm.country || '',
          preferred_market: editForm.preferred_market || 'US'
        },
        {
          headers: {
            'Authorization': `Bearer ${user.token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      // Refetch profile to get updated data
      await fetchBackendProfile();
      setIsEditing(false);
    } catch (err) {
      console.error('Error updating profile:', err);
      setError('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = async () => {
    try {
      await signOutUser();
      onLogout();
      navigate('/');
    } catch (error) {
      console.error('Error signing out:', error);
      setError('Failed to sign out');
    }
  };

  const getProviderName = () => {
    if (!firebaseUser) return 'Unknown';
    const providers = firebaseUser.providerData.map(p => p.providerId);
    if (providers.includes('google.com') && providers.includes('password')) {
      return 'Google + Email/Password';
    } else if (providers.includes('google.com')) {
      return 'Google';
    } else if (providers.includes('password')) {
      return 'Email/Password';
    }
    return 'Unknown';
  };

  const displayName = backendUser?.username || firebaseUser?.displayName || 'User'; // Always use backend username first
  const email = firebaseUser?.email || backendUser?.email || 'Not available';

  return (
    <motion.div
      className="profile-page"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="profile-container">
        <motion.div
          className="profile-card"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          <div className="profile-header">
            <div className="profile-avatar-large">
              {firebaseUser?.photoURL ? (
                <img src={firebaseUser.photoURL} alt="Profile" />
              ) : (
                <div className="avatar-placeholder-large">
                  {displayName.charAt(0).toUpperCase()}
                </div>
              )}
            </div>
            <h1 className="profile-name">{displayName}</h1>
            <p className="profile-email">{email}</p>
            <div className="profile-provider">
              <span className="provider-badge">{getProviderName()}</span>
            </div>
          </div>

          {error && (
            <div className="profile-error">
              {error}
            </div>
          )}

          <div className="profile-content">
            <div className="profile-section">
              <h2 className="section-title">
                <span className="section-icon">👤</span>
                Account Information
              </h2>
              <div className="info-grid">
                <div className="info-item">
                  <span className="info-label">Username</span>
                  <span className="info-value">{displayName}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Email</span>
                  <span className="info-value">{email}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Account Provider</span>
                  <span className="info-value">{getProviderName()}</span>
                </div>
                {backendUser && (
                  <div className="info-item">
                    <span className="info-label">Member Since</span>
                    <span className="info-value">
                      {new Date(backendUser.created_at).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {user?.token && (
              <div className="profile-section">
                <div className="section-header">
                  <h2 className="section-title">
                    <span className="section-icon">📱</span>
                    Contact & Preferences
                  </h2>
                  {!isEditing && (
                    <button
                      className="edit-button"
                      onClick={() => setIsEditing(true)}
                    >
                      ✏️ Edit
                    </button>
                  )}
                </div>

                {loading && !backendUser ? (
                  <div className="loading-spinner">
                    <div className="spinner"></div>
                  </div>
                ) : isEditing ? (
                  <div className="edit-form">
                    <div className="form-group">
                      <label>Mobile Number</label>
                      <input
                        type="tel"
                        name="phone_number"
                        value={editForm.phone_number}
                        onChange={handleEditChange}
                        className="input"
                        placeholder="Enter your mobile number"
                      />
                    </div>
                    <div className="form-group">
                      <label>Country</label>
                      <input
                        type="text"
                        name="country"
                        value={editForm.country}
                        onChange={handleEditChange}
                        className="input"
                        placeholder="Enter your country"
                      />
                    </div>
                    <div className="form-group">
                      <label>Preferred Music Language</label>
                      <select
                        name="preferred_market"
                        value={editForm.preferred_market}
                        onChange={handleEditChange}
                        className="input"
                      >
                        <option value="US">English (US)</option>
                        <option value="GB">English (UK)</option>
                        <option value="IN">Hindi/Indian</option>
                        <option value="ES">Spanish</option>
                        <option value="FR">French</option>
                        <option value="DE">German</option>
                        <option value="JP">Japanese</option>
                        <option value="KR">Korean</option>
                        <option value="BR">Portuguese (Brazil)</option>
                      </select>
                    </div>
                    <div className="edit-actions">
                      <button
                        className="save-button"
                        onClick={handleSaveProfile}
                        disabled={loading}
                      >
                        {loading ? 'Saving...' : 'Save Changes'}
                      </button>
                      <button
                        className="cancel-button"
                        onClick={() => {
                          setIsEditing(false);
                          setEditForm({
                            phone_number: backendUser?.phone_number || '',
                            country: backendUser?.country || '',
                            preferred_market: backendUser?.preferred_market || 'US'
                          });
                        }}
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="info-grid">
                    <div className="info-item">
                      <span className="info-label">Mobile Number</span>
                      <span className="info-value">
                        {backendUser?.phone_number && backendUser.phone_number.trim() ? backendUser.phone_number : 'Not set'}
                      </span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Country</span>
                      <span className="info-value">
                        {backendUser?.country && backendUser.country.trim() ? backendUser.country : 'Not set'}
                      </span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Preferred Music Language</span>
                      <span className="info-value">
                        {backendUser?.preferred_market || 'US'}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            )}

            {!user?.token && (
              <div className="profile-section">
                <div className="backend-login-prompt">
                  <p className="prompt-text">
                    <span className="prompt-icon">ℹ️</span>
                    Login to backend to view and edit additional profile information
                  </p>
                </div>
              </div>
            )}
          </div>

          <div className="profile-actions">
            <button className="logout-button" onClick={handleSignOut}>
              <span className="button-icon">🚪</span>
              Sign Out
            </button>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}

export default Profile;
