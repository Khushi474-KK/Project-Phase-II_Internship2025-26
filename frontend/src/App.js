import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { auth, needsProfileCompletion } from './firebase';
import { onAuthStateChanged } from 'firebase/auth';
import axios from 'axios';
import CompleteProfile from './components/CompleteProfile';
import Navbar from './components/Navbar';
import AuthModal from './components/AuthModal';
import Home from './pages/Home';
import Camera from './pages/Camera';
import Gallery from './pages/Gallery';
import Analytics from './pages/Analytics';
import About from './pages/About';
import Profile from './pages/Profile';
import './App.css';

function AppContent() {
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const [user, setUser] = useState(null);
  const [firebaseUser, setFirebaseUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [showProfileCompletion, setShowProfileCompletion] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  // Authenticate with backend using Firebase user
  const authenticateWithBackend = async (firebaseUser) => {
    try {
      console.log('Getting Firebase ID token for user:', firebaseUser.uid);
      
      // Get Firebase ID token
      const idToken = await firebaseUser.getIdToken();
      
      // Store token for API calls
      localStorage.setItem('firebaseToken', idToken);
      localStorage.setItem('userEmail', firebaseUser.email);
      
      // Call login endpoint to create a new session
      const response = await axios.post('http://localhost:8000/api/auth/login', {}, {
        headers: {
          Authorization: `Bearer ${idToken}`
        }
      });

      const backendUser = response.data;
      
      setUser({
        email: firebaseUser.email,
        username: backendUser.username, // Always use backend username (preserved during account linking)
        token: idToken,
        backendUser: backendUser
      });
      
      console.log('Backend authentication successful - Session:', backendUser.login_session_id);
    } catch (error) {
      console.error('Backend authentication failed:', error);
      // Continue anyway - user can still use Firebase features
      // Store token even if backend call fails
      const idToken = await firebaseUser.getIdToken();
      localStorage.setItem('firebaseToken', idToken);
      localStorage.setItem('userEmail', firebaseUser.email);
      
      setUser({
        email: firebaseUser.email,
        username: firebaseUser.displayName || firebaseUser.email.split('@')[0],
        token: idToken
      });
    }
  };

  // Firebase auth state listener
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (currentUser) => {
      console.log('Firebase auth state changed:', currentUser);
      setFirebaseUser(currentUser);
      
      if (currentUser) {
        // Check if user needs profile completion
        if (needsProfileCompletion(currentUser)) {
          console.log('User needs profile completion');
          setShowProfileCompletion(true);
        } else {
          setShowProfileCompletion(false);
          // Authenticate with backend
          await authenticateWithBackend(currentUser);
        }
      } else {
        // User signed out
        setUser(null);
        localStorage.removeItem('token');
        localStorage.removeItem('username');
      }
      
      setAuthLoading(false);
    });

    return () => unsubscribe();
  }, []);

  // Check for existing backend session on mount
  useEffect(() => {
    const token = localStorage.getItem('firebaseToken');
    const email = localStorage.getItem('userEmail');
    if (token && email && !user) {
      setUser({ 
        email, 
        username: email.split('@')[0],
        token 
      });
    }
  }, []);

  const handleGoogleSignInSuccess = async (googleUser) => {
    console.log('Google user signed in:', googleUser);
    // Check if profile completion is needed
    if (needsProfileCompletion(googleUser)) {
      setShowProfileCompletion(true);
    } else {
      // Authenticate with backend
      await authenticateWithBackend(googleUser);
    }
    // Close auth modal
    closeAuthModal();
  };

  const handleProfileComplete = async (updatedUser) => {
    console.log('Profile completed:', updatedUser);
    setShowProfileCompletion(false);
    // Authenticate with backend after profile completion
    await authenticateWithBackend(updatedUser);
  };

  const openAuthModal = (mode) => {
    setAuthMode(mode);
    setIsAuthModalOpen(true);
  };

  const closeAuthModal = () => {
    setIsAuthModalOpen(false);
  };

  const handleAuthSuccess = async (firebaseUser) => {
    // Firebase user is already authenticated
    // Just get the token and set user state
    await authenticateWithBackend(firebaseUser);
    closeAuthModal();
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('firebaseToken');
    localStorage.removeItem('userEmail');
  };

  // Check if route requires authentication
  const requiresAuth = (path) => {
    return ['/camera', '/gallery', '/analytics', '/profile'].includes(path);
  };

  // Redirect to home and open login modal if trying to access protected route
  useEffect(() => {
    if (!user && requiresAuth(location.pathname)) {
      navigate('/');
      openAuthModal('login');
    }
  }, [location.pathname, user]);

  // Show loading while checking auth
  if (authLoading) {
    return (
      <div className="app-loading">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  // Show profile completion if needed
  if (showProfileCompletion && firebaseUser) {
    return <CompleteProfile user={firebaseUser} onProfileComplete={handleProfileComplete} />;
  }

  // Show main app (Home page accessible without login)
  return (
    <div className="app">
      <Navbar 
        user={user} 
        onOpenAuth={openAuthModal} 
        onLogout={handleLogout}
        firebaseUser={firebaseUser}
      />
      
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<Home user={user} onOpenAuth={openAuthModal} />} />
          <Route path="/camera" element={<Camera user={user} />} />
          <Route path="/gallery" element={<Gallery user={user} />} />
          <Route path="/analytics" element={<Analytics user={user} />} />
          <Route path="/about" element={<About />} />
          <Route path="/profile" element={<Profile user={user} firebaseUser={firebaseUser} onLogout={handleLogout} />} />
        </Routes>
      </AnimatePresence>

      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={closeAuthModal}
        mode={authMode}
        onAuthSuccess={handleAuthSuccess}
        onOpenAuth={openAuthModal}
        onGoogleSignInSuccess={handleGoogleSignInSuccess}
      />
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
