import React from 'react';
import { motion } from 'framer-motion';
import './About.css';

function About() {
  const features = [
    {
      icon: '😊',
      title: 'Real-time Smile Detection',
      description: 'Advanced AI detects smiles in real-time and automatically captures photos when smiles are detected.'
    },
    {
      icon: '👤',
      title: 'Age and Gender Prediction',
      description: 'Deep learning models predict age ranges and gender with high accuracy using facial analysis.'
    },
    {
      icon: '📊',
      title: 'Portrait Quality Analysis',
      description: 'Comprehensive evaluation of lighting, sharpness, alignment, and overall photo quality.'
    },
    {
      icon: '🏆',
      title: 'Session-based Photo Ranking',
      description: 'Intelligent ranking system identifies the best photos from each capture session.'
    },
    {
      icon: '🎵',
      title: 'Emotion-based YouTube Music Recommendation',
      description: 'Personalized YouTube music suggestions based on detected emotional states and moods.'
    }
  ];

  const technologies = [
    {
      category: 'Computer Vision',
      items: ['OpenCV', 'Face Detection', 'Smile Detection', 'Quality Analysis']
    },
    {
      category: 'Deep Learning',
      items: ['Age Prediction Models', 'Gender Detection', 'Emotion Analysis', 'Caffe Models']
    },
    {
      category: 'Backend',
      items: ['Python', 'FastAPI', 'SQLAlchemy', 'JWT Authentication']
    },
    {
      category: 'Frontend',
      items: ['Modern Web Technologies', 'React', 'Responsive Design', 'Animations']
    }
  ];

  return (
    <motion.div
      className="page about-page"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="about-container">
        <motion.div
          className="about-hero"
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <h1 className="about-title">About Smart Camera</h1>
          <p className="about-description">
            Smart Camera is an AI-powered image analysis system designed to detect 
            smiles, estimate age and gender, and analyze portrait quality in real time. 
            The system captures photos through a live camera feed and evaluates facial 
            expressions, emotional states, and image quality. It automatically ranks 
            captured images to identify the best portrait and provides mood-based 
            YouTube music suggestions for an enhanced experience.
          </p>
        </motion.div>

        <motion.div
          className="about-section"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <h2 className="section-title">Key Features</h2>
          <div className="features-grid">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                className="feature-item"
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.4 + index * 0.1 }}
              >
                <div className="feature-icon-large">{feature.icon}</div>
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-description">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        <motion.div
          className="about-section"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <h2 className="section-title">Technologies Used</h2>
          <div className="tech-grid">
            {technologies.map((tech, index) => (
              <motion.div
                key={index}
                className="tech-card"
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.9 + index * 0.1 }}
              >
                <h3 className="tech-category">{tech.category}</h3>
                <ul className="tech-list">
                  {tech.items.map((item, idx) => (
                    <li key={idx} className="tech-item">
                      <span className="tech-bullet">▸</span>
                      {item}
                    </li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </div>
        </motion.div>

        <motion.div
          className="about-section"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 1.2 }}
        >
          <h2 className="section-title">How It Works</h2>
          <div className="workflow-steps">
            <div className="workflow-step">
              <div className="step-number">1</div>
              <div className="step-content">
                <h3>Capture</h3>
                <p>Position yourself in front of the camera and smile. Our AI detects faces and emotions in real-time.</p>
              </div>
            </div>
            <div className="workflow-step">
              <div className="step-number">2</div>
              <div className="step-content">
                <h3>Analyze</h3>
                <p>Advanced algorithms analyze age, gender, smile strength, and portrait quality metrics.</p>
              </div>
            </div>
            <div className="workflow-step">
              <div className="step-number">3</div>
              <div className="step-content">
                <h3>Recommend</h3>
                <p>Based on your emotional state, receive personalized music suggestions from YouTube.</p>
              </div>
            </div>
            <div className="workflow-step">
              <div className="step-number">4</div>
              <div className="step-content">
                <h3>Store</h3>
                <p>Photos are securely stored with session management and intelligent ranking.</p>
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          className="about-footer"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 1.4 }}
        >
          <p className="footer-text">
            Built with ❤️ using cutting-edge AI and modern web technologies
          </p>
        </motion.div>
      </div>
    </motion.div>
  );
}

export default About;
