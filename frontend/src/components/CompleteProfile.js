import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { completeProfile } from '../firebase';
import './CompleteProfile.css';

function CompleteProfile({ user, onProfileComplete }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    username: user?.displayName || '',
    password: '',
    confirmPassword: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validation
    if (!formData.username) {
      setError('Username is required');
      setLoading(false);
      return;
    }

    if (!formData.password) {
      setError('Password is required');
      setLoading(false);
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      setLoading(false);
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    try {
      const updatedUser = await completeProfile(formData.username, formData.password);
      console.log('Profile completed successfully:', updatedUser);
      onProfileComplete(updatedUser);
    } catch (err) {
      console.error('Error completing profile:', err);
      setError(err.message || 'Failed to complete profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="complete-profile-container">
      <motion.div
        className="complete-profile-card"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <div className="profile-header">
          <div className="user-avatar">
            {user?.photoURL ? (
              <img src={user.photoURL} alt="Profile" />
            ) : (
              <div className="avatar-placeholder">
                {user?.email?.charAt(0).toUpperCase() || '?'}
              </div>
            )}
          </div>
          <h2 className="profile-title">Complete Your Profile</h2>
          <p className="profile-subtitle">
            Set up your username and password to secure your account
          </p>
          <p className="profile-email">{user?.email}</p>
        </div>

        <div className="profile-content">
          {error && <div className="profile-error">{error}</div>}

          <form onSubmit={handleSubmit} className="profile-form">
            <div className="form-group">
              <label>Username (Display Name)</label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className="input"
                placeholder="Enter your username"
              />
              <span className="input-hint">This will be your display name</span>
            </div>

            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="input"
                placeholder="Create a password (min 6 characters)"
              />
              <span className="input-hint">You'll use this to sign in with email</span>
            </div>

            <div className="form-group">
              <label>Confirm Password</label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                className="input"
                placeholder="Confirm your password"
              />
            </div>

            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? <span className="profile-spinner"></span> : 'Complete Profile'}
            </button>
          </form>

          <div className="profile-info">
            <p>
              <strong>Why do I need this?</strong>
            </p>
            <p>
              Setting a password allows you to sign in with your email address in addition to Google.
              Your username will be displayed throughout the app.
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

export default CompleteProfile;
