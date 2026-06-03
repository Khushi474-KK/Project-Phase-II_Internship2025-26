import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { signOutUser } from '../firebase';
import './Navbar.css';

function Navbar({ user, onOpenAuth, onLogout, firebaseUser }) {
  const location = useLocation();
  const [showDropdown, setShowDropdown] = useState(false);

  const navItems = [
    { path: '/', label: 'Home' },
    { path: '/camera', label: 'Take a Pic' },
    { path: '/gallery', label: 'Gallery' },
    { path: '/analytics', label: 'Analytics' },
    { path: '/about', label: 'About' }
  ];

  const getActiveIndex = () => {
    const idx = navItems.findIndex(item => item.path === location.pathname);
    // /profile is not in navItems — return null to hide indicator
    return idx;
  };

  const indicatorVisible = getActiveIndex() >= 0;

  const handleSignOut = async () => {
    try {
      await signOutUser();
      onLogout();
      setShowDropdown(false);
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  // Display name priority: backend user > firebase display name > firebase email
  const displayName = user?.username || firebaseUser?.displayName || firebaseUser?.email?.split('@')[0] || 'User';

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <span className="logo-smart">Smart</span>
          <span className="logo-camera">Camera</span>
        </Link>

        <div className="navbar-menu">
          <div className="navbar-links">
            {navItems.map((item, index) => (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
              >
                {item.label}
              </Link>
            ))}
            <motion.div
              className="nav-indicator"
              initial={false}
              animate={{
                left: `${getActiveIndex() * 20}%`,
                width: '20%',
                opacity: indicatorVisible ? 1 : 0
              }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            />
          </div>

          <div className="navbar-auth">
            {user || firebaseUser ? (
              <div className="user-dropdown">
                <button
                  className="user-button"
                  onClick={() => setShowDropdown(!showDropdown)}
                >
                  {firebaseUser?.photoURL ? (
                    <img 
                      src={firebaseUser.photoURL} 
                      alt="Profile" 
                      className="user-avatar"
                    />
                  ) : (
                    <span className="user-icon">👤</span>
                  )}
                  {displayName}
                  <span className="dropdown-arrow">▼</span>
                </button>
                {showDropdown && (
                  <motion.div
                    className="dropdown-menu"
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                  >
                    {!user && (
                      <>
                        <button onClick={() => { onOpenAuth('login'); setShowDropdown(false); }} className="dropdown-item">
                          Backend Login
                        </button>
                        <button onClick={() => { onOpenAuth('register'); setShowDropdown(false); }} className="dropdown-item">
                          Backend Register
                        </button>
                        <div className="dropdown-divider"></div>
                      </>
                    )}
                    <Link to="/profile" className="dropdown-item" onClick={() => setShowDropdown(false)}>
                      Profile
                    </Link>
                    <button onClick={handleSignOut} className="dropdown-item">
                      Sign Out
                    </button>
                  </motion.div>
                )}
              </div>
            ) : (
              <button
                className="login-btn"
                onClick={() => onOpenAuth('login')}
              >
                Login
              </button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
