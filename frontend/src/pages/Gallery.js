import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Gallery.css';

function Gallery({ user }) {
  const navigate = useNavigate();
  const [photos, setPhotos] = useState([]);
  const [filter, setFilter] = useState('all');
  const [selectedPhoto, setSelectedPhoto] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showFilterPanel, setShowFilterPanel] = useState(false);
  const [ageFilter, setAgeFilter] = useState('');
  const [genderFilter, setGenderFilter] = useState('any');
  const [deletingPhotoId, setDeletingPhotoId] = useState(null);

  // Collage state
  const [collageMode, setCollageMode] = useState(false);
  const [selectedForCollage, setSelectedForCollage] = useState([]);
  const [collageStep, setCollageStep] = useState(null); // null | 'select' | 'template' | 'generating'
  const [collageTemplate, setCollageTemplate] = useState(null);

  useEffect(() => {
    if (!user) {
      navigate('/');
    } else {
      fetchPhotos();
    }
  }, [user, navigate]);
  
  useEffect(() => {
    console.log('Selected photo changed:', selectedPhoto);
  }, [selectedPhoto]);

  const fetchPhotos = async () => {
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
      
      // Deduplicate by id — guard against backend returning same photo twice
      const seen = new Set();
      const unique = response.data.filter(photo => {
        if (seen.has(photo.id)) return false;
        seen.add(photo.id);
        return true;
      });
      
      setPhotos(unique);
      setError('');
    } catch (err) {
      console.error('Error fetching photos:', err);
      setError('Failed to load photos');
      setPhotos([]);
    } finally {
      setLoading(false);
    }
  };

  // Filter photos by category and custom filters
  const getFilteredPhotos = () => {
    let filtered = [...photos];
    
    if (filter === 'high-quality') {
      filtered = filtered.filter(photo => photo.is_best_in_session === true);
    } else if (filter === 'uploaded') {
      filtered = filtered.filter(photo => photo.source === 'upload');
    } else if (filter === 'captured') {
      filtered = filtered.filter(photo => photo.source === 'camera' || !photo.source);
    }
    
    if (ageFilter) {
      const age = parseInt(ageFilter);
      filtered = filtered.filter(photo => {
        if (!photo.age_category) return false;
        if (age <= 12) return photo.age_category === 'child';
        if (age <= 25) return photo.age_category === 'young_adult';
        return photo.age_category === 'adult';
      });
    }
    
    if (genderFilter && genderFilter !== 'any') {
      filtered = filtered.filter(photo => 
        photo.gender && photo.gender.toLowerCase() === genderFilter.toLowerCase()
      );
    }
    
    return filtered;
  };

  const applyCustomFilter = () => {
    setShowFilterPanel(false);
    // Filtering happens automatically through getFilteredPhotos
  };

  const clearCustomFilters = () => {
    setAgeFilter('');
    setGenderFilter('any');
    setShowFilterPanel(false);
  };

  const handleDeletePhoto = async (photoId, event) => {
    if (event) {
      event.stopPropagation(); // Prevent opening modal
    }
    
    if (!window.confirm('Are you sure you want to delete this image?')) {
      return;
    }
    
    setDeletingPhotoId(photoId);
    
    try {
      const token = localStorage.getItem('firebaseToken');
      await axios.delete(`http://localhost:8000/api/photos/${photoId}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      // Remove photo from state
      setPhotos(photos.filter(p => p.id !== photoId));
      
      // Close modal if this photo was selected
      if (selectedPhoto && selectedPhoto.id === photoId) {
        setSelectedPhoto(null);
      }
      
      console.log('Photo deleted successfully');
    } catch (err) {
      console.error('Error deleting photo:', err);
      alert('Failed to delete photo. Please try again.');
    } finally {
      setDeletingPhotoId(null);
    }
  };

  // Group photos by session
  const groupPhotosBySession = (photoList) => {
    const sessions = {};
    
    photoList.forEach(photo => {
      const sessionId = photo.session_id;
      if (!sessions[sessionId]) {
        sessions[sessionId] = {
          id: sessionId,
          photos: [],
          timestamp: photo.created_at
        };
      }
      sessions[sessionId].photos.push(photo);
    });
    
    // Convert to array and sort by timestamp (newest first)
    return Object.values(sessions).sort((a, b) => 
      new Date(b.timestamp) - new Date(a.timestamp)
    );
  };

  const filteredPhotos = getFilteredPhotos();
  const sessionGroups = groupPhotosBySession(filteredPhotos);

  const formatSessionTitle = (sessionId, photos) => {
    // If all photos in this session are uploads, label it accordingly
    if (photos && photos.every(p => p.source === 'upload')) {
      return 'Uploaded Photos';
    }
    const match = sessionId.match(/session_(\d+)\s+(.+)/);
    if (match) {
      return `Session ${match[1]} – ${match[2]}`;
    }
    return 'Photos';
  };

  const enterCollageMode = () => {
    setCollageMode(true);
    setCollageStep('select');
    setSelectedForCollage([]);
    setCollageTemplate(null);
  };

  const exitCollageMode = () => {
    setCollageMode(false);
    setCollageStep(null);
    setSelectedForCollage([]);
    setCollageTemplate(null);
  };

  const toggleCollageSelect = (photoId) => {
    setSelectedForCollage(prev => {
      if (prev.includes(photoId)) return prev.filter(id => id !== photoId);
      if (prev.length >= 5) return prev; // max 5
      return [...prev, photoId];
    });
  };

  const getTemplatesForCount = (n) => {
    if (n === 2) return [
      { id: 'side-by-side', label: 'Side by Side', icon: '⬜⬜' },
      { id: 'top-bottom', label: 'Top / Bottom', icon: '🔲' },
    ];
    if (n === 3) return [
      { id: '1-large-2-small', label: '1 Large + 2 Small', icon: '🖼️' },
      { id: 'grid', label: 'Grid (1 top + 2 bottom)', icon: '⊞' },
    ];
    if (n === 4) return [
      { id: '2x2', label: '2×2 Grid', icon: '⊞' },
      { id: 'large-3', label: '1 Large + 3 Bottom', icon: '🖼️' },
    ];
    if (n === 5) return [
      { id: '5-grid', label: '5-Photo Grid', icon: '⊞' },
    ];
    return [];
  };

  const handleCreateCollage = async () => {
    if (!collageTemplate) return;
    setCollageStep('generating');
    try {
      const token = localStorage.getItem('firebaseToken');
      await axios.post(
        'http://localhost:8000/api/collage/create',
        { photo_ids: selectedForCollage, template: collageTemplate },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      await fetchPhotos();
      exitCollageMode();
    } catch (err) {
      console.error('Collage error:', err);
      alert('Failed to create collage. Please try again.');
      setCollageStep('template');
    }
  };

  if (!user) {
    return null;
  }

  return (
    <>
    <motion.div
      className="page gallery-page"
      initial={{ y: '-100%' }}
      animate={{ y: 0 }}
      exit={{ y: '-100%' }}
      transition={{ type: 'spring', stiffness: 100, damping: 20 }}
    >
      <div className="gallery-container">
        <motion.div
          className="gallery-header"
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <h1 className="gallery-title">Photo Gallery</h1>
          <p className="gallery-subtitle">Browse your captured moments</p>
        </motion.div>

        <motion.div
          className="gallery-filters"
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <button
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All Photos
          </button>
          <button
            className={`filter-btn ${filter === 'high-quality' ? 'active' : ''}`}
            onClick={() => setFilter('high-quality')}
          >
            High Quality
          </button>
          <button
            className={`filter-btn ${filter === 'captured' ? 'active' : ''}`}
            onClick={() => setFilter('captured')}
          >
            Captured
          </button>
          <button
            className={`filter-btn ${filter === 'uploaded' ? 'active' : ''}`}
            onClick={() => setFilter('uploaded')}
          >
            Uploaded
          </button>
          <button
            className={`filter-btn ${showFilterPanel ? 'active' : ''}`}
            onClick={() => setShowFilterPanel(!showFilterPanel)}
          >
            Filter {(ageFilter || genderFilter !== 'any') ? '✓' : ''}
          </button>
          <button
            className={`filter-btn collage-btn ${collageMode ? 'active' : ''}`}
            onClick={collageMode ? exitCollageMode : enterCollageMode}
          >
            ⊞ Collage
          </button>
        </motion.div>

        {/* Custom Filter Panel */}
        {showFilterPanel && (
          <motion.div
            className="filter-panel"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <div className="filter-panel-content">
              <div className="filter-group">
                <label>Age:</label>
                <input
                  type="number"
                  placeholder="Enter age"
                  value={ageFilter}
                  onChange={(e) => setAgeFilter(e.target.value)}
                  className="filter-input"
                />
              </div>
              <div className="filter-group">
                <label>Gender:</label>
                <select
                  value={genderFilter}
                  onChange={(e) => setGenderFilter(e.target.value)}
                  className="filter-select"
                >
                  <option value="any">Any</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                </select>
              </div>
              <div className="filter-actions">
                <button className="btn btn-ghost" onClick={clearCustomFilters}>
                  Clear
                </button>
                <button className="btn btn-primary" onClick={applyCustomFilter}>
                  Apply Filter
                </button>
              </div>
            </div>
          </motion.div>
        )}

        {/* Collage selection bar */}
        {collageMode && collageStep === 'select' && (
          <motion.div
            className="collage-bar"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <span className="collage-bar-info">
              Select 2–5 photos &nbsp;·&nbsp; {selectedForCollage.length} selected
            </span>
            <div className="collage-bar-actions">
              <button className="btn btn-ghost" onClick={exitCollageMode}>Cancel</button>
              <button
                className="btn btn-primary"
                disabled={selectedForCollage.length < 2}
                onClick={() => setCollageStep('template')}
              >
                Next →
              </button>
            </div>
          </motion.div>
        )}

        {/* Template picker */}
        {collageMode && collageStep === 'template' && (
          <motion.div
            className="collage-template-panel"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h3 className="collage-template-title">Choose a Layout</h3>
            <div className="collage-template-grid">
              {getTemplatesForCount(selectedForCollage.length).map(t => (
                <button
                  key={t.id}
                  className={`collage-template-btn ${collageTemplate === t.id ? 'active' : ''}`}
                  onClick={() => setCollageTemplate(t.id)}
                >
                  <span className="template-icon">{t.icon}</span>
                  <span className="template-label">{t.label}</span>
                </button>
              ))}
            </div>
            <div className="collage-bar-actions">
              <button className="btn btn-ghost" onClick={() => setCollageStep('select')}>← Back</button>
              <button
                className="btn btn-primary"
                disabled={!collageTemplate}
                onClick={handleCreateCollage}
              >
                Create Collage
              </button>
            </div>
          </motion.div>
        )}

        {/* Generating overlay */}
        {collageMode && collageStep === 'generating' && (
          <div className="collage-generating">
            <div className="spinner"></div>
            <p>Generating collage...</p>
          </div>
        )}

        {loading ? (
          <div className="gallery-loading">
            <div className="spinner"></div>
            <p>Loading photos...</p>
          </div>
        ) : error ? (
          <div className="gallery-error">
            <p>{error}</p>
            <button className="btn btn-primary" onClick={fetchPhotos}>
              Retry
            </button>
          </div>
        ) : sessionGroups.length === 0 ? (
          <div className="empty-gallery">
            <div className="empty-icon">📷</div>
            <p>No photos yet. Start capturing!</p>
            <button
              className="btn btn-primary"
              onClick={() => navigate('/camera')}
            >
              Take a Photo
            </button>
          </div>
        ) : (
          <motion.div
            className="sessions-container"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            {sessionGroups.map((session, sessionIndex) => (
              <div key={session.id} className="session-group">
                <div className="session-header">
                  <h3 className="session-title">
                    {formatSessionTitle(session.id, session.photos)}
                  </h3>
                  <span className="session-count">
                    {session.photos.length} {session.photos.length === 1 ? 'photo' : 'photos'}
                  </span>
                </div>
                
                <div className="gallery-grid">
                  {session.photos.map((photo, photoIndex) => (
                    <motion.div
                      key={photo.id}
                      className={`photo-card ${collageMode ? 'collage-selectable' : ''} ${selectedForCollage.includes(photo.id) ? 'collage-selected' : ''}`}
                      initial={{ scale: 0.8, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ delay: 0.05 * photoIndex }}
                      onClick={() => {
                        if (collageMode) {
                          toggleCollageSelect(photo.id);
                        } else {
                          console.log('Photo clicked:', photo);
                          setSelectedPhoto(photo);
                        }
                      }}
                    >
                      <img 
                        src={`http://localhost:8000${photo.file_path}`} 
                        alt={`Photo ${photo.id}`} 
                        className="photo-thumbnail" 
                      />
                      {collageMode && (
                        <div className={`collage-checkbox ${selectedForCollage.includes(photo.id) ? 'checked' : ''}`}>
                          {selectedForCollage.includes(photo.id) ? '✓' : ''}
                        </div>
                      )}
                      {photo.is_best_in_session && !collageMode && (
                        <div className="best-badge">⭐ Best</div>
                      )}
                      <div className="photo-overlay">
                        <div className="photo-stats">
                          {photo.smile_score && (
                            <div className="stat">
                              <span className="stat-icon">😊</span>
                              <span className="stat-value">{photo.smile_score.toFixed(0)}%</span>
                            </div>
                          )}
                          {photo.final_score && (
                            <div className="stat">
                              <span className="stat-icon">⭐</span>
                              <span className="stat-value">{photo.final_score.toFixed(0)}%</span>
                            </div>
                          )}
                        </div>
                        <div className="photo-actions">
                          <button
                            className="delete-btn"
                            onClick={(e) => handleDeletePhoto(photo.id, e)}
                            disabled={deletingPhotoId === photo.id}
                            title="Delete photo"
                          >
                            {deletingPhotoId === photo.id ? '⏳' : '🗑'}
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            ))}
          </motion.div>
        )}

      </div>
    </motion.div>

    {/* Modal rendered via portal directly into document.body — bypasses any transform/stacking context */}
    {createPortal(
      <AnimatePresence mode="wait">
        {selectedPhoto && (
          <motion.div
            className="photo-modal"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedPhoto(null)}
          >
            <motion.div
              className="photo-modal-content"
              initial={{ scale: 0.85, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.85, opacity: 0 }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              onClick={(e) => e.stopPropagation()}
            >
              <button className="modal-close" onClick={() => setSelectedPhoto(null)}>✕</button>
              <button
                className="modal-delete"
                onClick={() => handleDeletePhoto(selectedPhoto.id)}
                disabled={deletingPhotoId === selectedPhoto.id}
                title="Delete photo"
              >
                {deletingPhotoId === selectedPhoto.id ? '⏳' : '🗑'}
              </button>

              <img
                src={`http://localhost:8000${selectedPhoto.file_path}`}
                alt="Selected"
                className="modal-photo"
                onError={(e) => {
                  e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23334155" width="400" height="300"/%3E%3Ctext fill="%2394A3B8" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3EImage not found%3C/text%3E%3C/svg%3E';
                }}
              />

              <div className="modal-details">
                <h3>Photo Details</h3>
                {selectedPhoto.is_best_in_session && (
                  <div className="detail-row">
                    <span>Status:</span>
                    <span className="detail-value">⭐ Best in Session</span>
                  </div>
                )}
                {selectedPhoto.smile_score != null && (
                  <div className="detail-row">
                    <span>Smile Score:</span>
                    <span className="detail-value">{selectedPhoto.smile_score.toFixed(1)}%</span>
                  </div>
                )}
                {selectedPhoto.lighting_score != null && (
                  <div className="detail-row">
                    <span>Lighting:</span>
                    <span className="detail-value">{selectedPhoto.lighting_score.toFixed(1)}%</span>
                  </div>
                )}
                {selectedPhoto.sharpness_score != null && (
                  <div className="detail-row">
                    <span>Sharpness:</span>
                    <span className="detail-value">{selectedPhoto.sharpness_score.toFixed(1)}%</span>
                  </div>
                )}
                {selectedPhoto.alignment_score != null && (
                  <div className="detail-row">
                    <span>Alignment:</span>
                    <span className="detail-value">{selectedPhoto.alignment_score.toFixed(1)}%</span>
                  </div>
                )}
                {selectedPhoto.final_score != null && (
                  <div className="detail-row">
                    <span>Final Score:</span>
                    <span className="detail-value">{selectedPhoto.final_score.toFixed(1)}%</span>
                  </div>
                )}
                {selectedPhoto.age_category && (
                  <div className="detail-row">
                    <span>Age Category:</span>
                    <span className="detail-value" style={{ textTransform: 'capitalize' }}>
                      {selectedPhoto.age_category.replace('_', ' ')}
                    </span>
                  </div>
                )}
                {selectedPhoto.gender && (
                  <div className="detail-row">
                    <span>Gender:</span>
                    <span className="detail-value">{selectedPhoto.gender}</span>
                  </div>
                )}
                {selectedPhoto.created_at && (
                  <div className="detail-row">
                    <span>Captured:</span>
                    <span className="detail-value">
                      {new Date(selectedPhoto.created_at).toLocaleString()}
                    </span>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>,
      document.body
    )}
    </>
  );
}

export default Gallery;
