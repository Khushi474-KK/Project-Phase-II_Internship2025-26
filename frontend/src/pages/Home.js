import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import './Home.css';

function Home({ user, onOpenAuth }) {
  const navigate = useNavigate();

  const handleStartCamera = () => {
    if (user) {
      navigate('/camera');
    } else {
      onOpenAuth('login');
    }
  };

  return (
    <motion.div
      className="page home-page"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="home-container">
        <motion.div
          className="home-content"
          initial={{ x: -50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.6 }}
        >
          <h1 className="home-title">
            Smart Camera
          </h1>
          <h2 className="home-subtitle">
            AI-Based Smile, Age and Portrait Intelligence System
          </h2>
          <p className="home-description">
            Smart Camera is an AI-powered image analysis system designed to detect 
            smiles, estimate age and gender, and analyze portrait quality in real time. 
            The system captures photos through a live camera feed and evaluates facial 
            expressions, emotional states, and image quality. It automatically ranks 
            captured images to identify the best portrait and provides mood-based 
            YouTube music suggestions for an enhanced experience.
          </p>
          <div className="home-buttons">
            <button
              className="btn btn-primary"
              onClick={handleStartCamera}
            >
              Start Camera
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => navigate('/about')}
            >
              Learn More
            </button>
          </div>
        </motion.div>

        <motion.div
          className="home-visual"
          initial={{ x: 50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.6 }}
        >
          <div className="visual-card">
            <div className="camera-icon">📸</div>
            <div className="visual-features">
              <div className="feature-badge">😊 Smile Detection</div>
              <div className="feature-badge">👤 Age Prediction</div>
              <div className="feature-badge">⚡ Real-time Analysis</div>
              <div className="feature-badge">🎵 Music Suggestions</div>
            </div>
          </div>
        </motion.div>
      </div>

      <motion.div
        className="home-features"
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.6, duration: 0.6 }}
      >
        <div className="feature-card">
          <div className="feature-icon">🎯</div>
          <h3>Smart Detection</h3>
          <p>Advanced AI detects faces, smiles, and emotions in real-time</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">📊</div>
          <h3>Portrait Analytics</h3>
          <p>Comprehensive analysis of lighting, sharpness, and alignment</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">🎵</div>
          <h3>Music Recommendations</h3>
          <p>Mood-based YouTube suggestions tailored to your emotions</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">🏆</div>
          <h3>Session Ranking</h3>
          <p>Automatically identifies your best photos in each session</p>
        </div>
      </motion.div>
    </motion.div>
  );
}

export default Home;
