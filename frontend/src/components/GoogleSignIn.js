import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { signInWithGoogle, registerWithEmail, loginWithEmail, linkGoogleAccount } from '../firebase';
import './GoogleSignIn.css';

function GoogleSignIn({ onSignInSuccess }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [mode, setMode] = useState('choice'); // 'choice', 'email-login', 'email-register', 'link-account'
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [linkingData, setLinkingData] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleGoogleSignIn = async () => {
    setLoading(true);
    setError('');
    
    try {
      const result = await signInWithGoogle();
      
      if (result.error === 'account-exists') {
        // Account exists with different credential
        setLinkingData(result);
        setFormData({ ...formData, email: result.email });
        setMode('link-account');
        setError(`An account already exists with ${result.email}. Please sign in with your password to link your Google account.`);
      } else {
        console.log('Google Sign-In successful:', result.user);
        // Pass user to parent - App.js will check if profile completion is needed
        onSignInSuccess(result.user);
      }
    } catch (err) {
      console.error('Google Sign-In error:', err);
      setError(err.message || 'Failed to sign in with Google. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleEmailRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validation
    if (!formData.username || !formData.email || !formData.password) {
      setError('Please fill in all required fields');
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
      const user = await registerWithEmail(formData.email, formData.password, formData.username);
      console.log('Email registration successful:', user);
      onSignInSuccess(user);
    } catch (err) {
      console.error('Email registration error:', err);
      setError(err.message || 'Failed to register. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleEmailLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!formData.email || !formData.password) {
      setError('Please fill in all fields');
      setLoading(false);
      return;
    }

    try {
      const user = await loginWithEmail(formData.email, formData.password);
      console.log('Email login successful:', user);
      
      // If we're in linking mode, link the Google account
      if (mode === 'link-account' && linkingData) {
        try {
          const linkedUser = await linkGoogleAccount();
          console.log('Google account linked successfully:', linkedUser);
          onSignInSuccess(linkedUser);
        } catch (linkErr) {
          console.error('Error linking Google account:', linkErr);
          // Still proceed with email login even if linking fails
          setError('Logged in successfully, but failed to link Google account: ' + linkErr.message);
          setTimeout(() => onSignInSuccess(user), 2000);
        }
      } else {
        onSignInSuccess(user);
      }
    } catch (err) {
      console.error('Email login error:', err);
      setError(err.message || 'Failed to sign in. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderChoiceScreen = () => (
    <>
      <div className="signin-header">
        <div className="camera-icon-large">📷</div>
        <h1 className="signin-title">
          <span className="title-smart">Smart</span>
          <span className="title-camera">Camera</span>
        </h1>
        <p className="signin-subtitle">
          AI-Based Smile, Age and Portrait Intelligence System
        </p>
      </div>

      <div className="signin-content">
        <p className="signin-description">
          Sign in to access the Smart Camera system
        </p>

        {error && <div className="signin-error">{error}</div>}

        <button
          className="google-signin-btn"
          onClick={handleGoogleSignIn}
          disabled={loading}
        >
          {loading ? (
            <span className="signin-spinner"></span>
          ) : (
            <>
              <svg className="google-icon" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Sign in with Google
            </>
          )}
        </button>

        <div className="divider">
          <span>OR</span>
        </div>

        <button
          className="email-signin-btn"
          onClick={() => setMode('email-login')}
        >
          Sign in with Email
        </button>

        <button
          className="email-register-btn"
          onClick={() => setMode('email-register')}
        >
          Create Account with Email
        </button>
      </div>
    </>
  );

  const renderEmailLoginForm = () => (
    <>
      <div className="signin-header-small">
        <h2 className="signin-title-small">Sign In</h2>
        <p className="signin-subtitle-small">
          {mode === 'link-account' ? 'Sign in to link your Google account' : 'Sign in with your email and password'}
        </p>
      </div>

      <div className="signin-content">
        {error && <div className="signin-error">{error}</div>}

        <form onSubmit={handleEmailLogin} className="auth-form">
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="input"
              placeholder="Enter your email"
              disabled={mode === 'link-account'}
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="input"
              placeholder="Enter your password"
            />
          </div>

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? <span className="signin-spinner"></span> : 'Sign In'}
          </button>
        </form>

        {mode !== 'link-account' && (
          <button className="back-btn" onClick={() => setMode('choice')}>
            Back to options
          </button>
        )}
      </div>
    </>
  );

  const renderEmailRegisterForm = () => (
    <>
      <div className="signin-header-small">
        <h2 className="signin-title-small">Create Account</h2>
        <p className="signin-subtitle-small">Register with your email</p>
      </div>

      <div className="signin-content">
        {error && <div className="signin-error">{error}</div>}

        <form onSubmit={handleEmailRegister} className="auth-form">
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
          </div>

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="input"
              placeholder="Enter your email"
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="input"
              placeholder="Enter your password (min 6 characters)"
            />
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
            {loading ? <span className="signin-spinner"></span> : 'Create Account'}
          </button>
        </form>

        <button className="back-btn" onClick={() => setMode('choice')}>
          Back to options
        </button>
      </div>
    </>
  );

  return (
    <div className="google-signin-container">
      <motion.div
        className="google-signin-card"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <AnimatePresence mode="wait">
          {mode === 'choice' && (
            <motion.div
              key="choice"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              {renderChoiceScreen()}
            </motion.div>
          )}
          {(mode === 'email-login' || mode === 'link-account') && (
            <motion.div
              key="login"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              {renderEmailLoginForm()}
            </motion.div>
          )}
          {mode === 'email-register' && (
            <motion.div
              key="register"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              {renderEmailRegisterForm()}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}

export default GoogleSignIn;
