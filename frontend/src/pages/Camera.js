import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Camera.css';

function Camera({ user }) {
  const navigate = useNavigate();
  const [capturedPhoto, setCapturedPhoto] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [musicRecommendation, setMusicRecommendation] = useState(null);
  const [caption, setCaption] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [imageLoading, setImageLoading] = useState(false);
  const [likedSongs, setLikedSongs] = useState(new Set());
  const [dislikedSongs, setDislikedSongs] = useState(new Set());
  const [currentlyPlaying, setCurrentlyPlaying] = useState(null);
  const [selectedTrackForEmbed, setSelectedTrackForEmbed] = useState(null);
  const [faces, setFaces] = useState([]);
  
  // New state for webcam streaming
  const [streaming, setStreaming] = useState(false);
  const [smileCounter, setSmileCounter] = useState(0);
  const [detectionResults, setDetectionResults] = useState(null);
  const [lastUpdateTime, setLastUpdateTime] = useState(Date.now());
  const [mode, setMode] = useState(null); // null, 'capture', 'upload'
  const videoRef = React.useRef(null);
  const canvasRef = React.useRef(null);
  const wsRef = React.useRef(null);
  const streamIntervalRef = React.useRef(null);
  const mediaStreamRef = React.useRef(null);
  const captureLockRef = React.useRef(false); // Prevents multiple captures per detection event
  
  const SMILE_THRESHOLD = 7;

  useEffect(() => {
    if (!user) {
      navigate('/');
    }
  }, [user, navigate]);
  
  // Start webcam only when capture mode is selected
  useEffect(() => {
    if (user && mode === 'capture' && !capturedPhoto) {
      startWebcam();
    }
    
    return () => {
      if (mode === 'capture') {
        stopWebcam();
      }
    };
  }, [user, mode, capturedPhoto]);
  
  const startWebcam = async () => {
    try {
      // Get webcam stream
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 }
      });
      
      mediaStreamRef.current = stream;
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        
        // Wait for video to be ready before playing
        videoRef.current.onloadedmetadata = () => {
          videoRef.current.play().catch(err => {
            console.log('Video play error:', err);
          });
        };
      }
      
      // Connect WebSocket
      const ws = new WebSocket('ws://localhost:8000/api/camera/ws/analyze');
      wsRef.current = ws;
      
      ws.onopen = () => {
        console.log('✓ WebSocket connected');
        setStreaming(true);
        startFrameStreaming();
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        console.log('Received detection data:', data);
        
        if (data.error) {
          console.error('Detection error:', data.error);
          return;
        }
        
        setDetectionResults(data);
        setLastUpdateTime(Date.now());  // Track last update
        
        // Update smile counter based on all_smiling flag
        if (data.all_smiling && data.face_count > 0) {
          setSmileCounter(prev => {
            const newCount = prev + 1;
            console.log(`Smile detected! Counter: ${newCount}/${SMILE_THRESHOLD}`);
            
            // Trigger capture when threshold reached — lock prevents multiple triggers
            if (newCount >= SMILE_THRESHOLD && !captureLockRef.current) {
              captureLockRef.current = true;
              console.log('Smile threshold reached! Capturing...');
              handleAutoCapture();
              return 0;
            }
            
            return newCount;
          });
        } else {
          // Reset counter if not all faces are smiling
          setSmileCounter(prev => {
            if (prev > 0) {
              console.log('Smile lost, resetting counter');
            }
            return 0;
          });
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('Connection error. Please refresh the page.');
      };
      
      ws.onclose = () => {
        console.log('✓ WebSocket disconnected');
        setStreaming(false);
      };
      
    } catch (err) {
      console.error('Webcam error:', err);
      setError('Failed to access webcam. Please grant camera permissions.');
    }
  };
  
  const stopWebcam = () => {
    // Stop frame streaming
    if (streamIntervalRef.current) {
      clearInterval(streamIntervalRef.current);
      streamIntervalRef.current = null;
    }
    
    // Close WebSocket
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    // Stop media stream
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
      mediaStreamRef.current = null;
    }
    
    setStreaming(false);
    setSmileCounter(0);
    setDetectionResults(null);
  };
  
  const startFrameStreaming = () => {
    // Send frames every 200ms (reduced from 120ms for better performance)
    streamIntervalRef.current = setInterval(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN && videoRef.current && canvasRef.current) {
        const video = videoRef.current;
        const canvas = canvasRef.current;
        
        // Check if video is ready
        if (video.readyState !== video.HAVE_ENOUGH_DATA) {
          return;
        }
        
        const ctx = canvas.getContext('2d');
        
        // Set canvas size to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Draw current frame to canvas
        ctx.drawImage(video, 0, 0);
        
        // Convert to base64 with lower quality for faster transmission
        const frameData = canvas.toDataURL('image/jpeg', 0.6);
        
        // Send to backend
        try {
          wsRef.current.send(JSON.stringify({ frame: frameData }));
        } catch (err) {
          console.error('Error sending frame:', err);
        }
      }
    }, 200);  // Increased from 120ms to 200ms
  };
  
  const handleAutoCapture = async () => {
    if (!videoRef.current || !canvasRef.current) return;
    
    console.log('Auto-capture triggered!');
    
    // Stop streaming first
    if (streamIntervalRef.current) {
      clearInterval(streamIntervalRef.current);
      streamIntervalRef.current = null;
    }
    
    // Close WebSocket
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setLoading(true);
    setError('');    
    try {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      
      // Wait a moment for the video to stabilize
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Ensure video is playing and has data
      if (video.readyState < video.HAVE_CURRENT_DATA) {
        throw new Error('Video not ready for capture');
      }
      
      // Capture high resolution frame from video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      // Clear canvas first
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw the current video frame
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // Convert to high quality JPEG
      const frameData = canvas.toDataURL('image/jpeg', 0.95);
      
      console.log('Frame captured, size:', frameData.length, 'bytes');
      
      // Verify frame data is valid
      if (!frameData || frameData.length < 1000) {
        throw new Error('Captured frame is too small or invalid');
      }
      
      const token = localStorage.getItem('firebaseToken');
      const clientTimestamp = new Date().toISOString();
      const clientTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
      
      console.log('Sending capture request to backend...');
      
      const response = await axios.post(
        '/api/camera/capture',
        {
          client_timestamp: clientTimestamp,
          client_timezone: clientTimezone,
          frame: frameData
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      console.log('Capture response received:', response.data);
      
      // Stop media stream after successful capture
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach(track => track.stop());
        mediaStreamRef.current = null;
      }
      
      const data = response.data;
      
      let imagePath = data.image_path;
      if (imagePath) {
        if (!imagePath.startsWith('/')) {
          imagePath = '/' + imagePath;
        }
        const imageUrl = `http://localhost:8000${imagePath}`;
        console.log('Setting captured image URL:', imageUrl);
        setImageLoading(true);
        setCapturedPhoto(imageUrl);
      } else {
        setError('No image path received from server');
      }
      
      setCaption(data.caption || 'Photo captured successfully!');
      setAnalytics(data.analytics);
      setFaces(data.faces || []);
      setMusicRecommendation(data.music_recommendation);
      
    } catch (err) {
      console.error('Capture error:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to capture photo. Please try again.');
      captureLockRef.current = false; // Release lock so user can retry
      // Restart webcam on error
      setTimeout(() => {
        startWebcam();
      }, 1000);
    } finally {
      setLoading(false);
      setStreaming(false);
    }
  };

  // Auto-load first song when music recommendations appear
  useEffect(() => {
    if (musicRecommendation?.tracks?.length > 0) {
      const firstTrack = musicRecommendation.tracks[0];
      if (firstTrack.embed_url) setSelectedTrackForEmbed(firstTrack.embed_url);
    }
  }, [musicRecommendation]);

  // Extract unique track key — use video_id for YouTube
  const getTrackId = (track) => track.video_id || track.track_id || null;

  const autoPlayFirstSong = (tracks) => {
    const player = document.getElementById('songPlayer');
    if (!player) return;

    const firstPlayableSong = tracks.find(track => track.preview_url !== null && track.preview_url !== undefined);
    
    if (firstPlayableSong) {
      player.src = firstPlayableSong.preview_url;
      setCurrentlyPlaying(firstPlayableSong.preview_url);
      player.play().catch(err => {
        console.log('Autoplay prevented by browser:', err);
      });
    }
  };

  const playSong = (previewUrl) => {
    const player = document.getElementById('songPlayer');
    if (!player || !previewUrl) return;

    player.src = previewUrl;
    setCurrentlyPlaying(previewUrl);
    player.play().catch(err => {
      console.error('Error playing song:', err);
    });
  };

  const handleCapture = async () => {
    // Manual capture - same as auto capture
    handleAutoCapture();
  };

  const handleRetake = () => {
    const player = document.getElementById('songPlayer');
    if (player) {
      player.pause();
      player.src = '';
    }
    
    captureLockRef.current = false; // Reset lock for next session
    setCapturedPhoto(null);
    setAnalytics(null);
    setFaces([]);
    setMusicRecommendation(null);
    setCaption('');
    setError('');
    setImageLoading(false);
    setLoading(false);
    setLikedSongs(new Set());
    setCurrentlyPlaying(null);
    setSelectedTrackForEmbed(null);
    setMode(null); // Go back to mode selection
  };
  
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Please upload an image file');
      return;
    }
    
    setLoading(true);
    setError('');
    setMode('upload'); // Set mode to upload
    
    try {
      // Read file as base64
      const reader = new FileReader();
      reader.onload = async (e) => {
        const frameData = e.target.result;
        
        const token = localStorage.getItem('firebaseToken');
        const clientTimestamp = new Date().toISOString();
        const clientTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone; // Fixed: removed ()
        
        const response = await axios.post(
          '/api/camera/capture',
          {
            client_timestamp: clientTimestamp,
            client_timezone: clientTimezone,
            frame: frameData,
            source: 'upload'
          },
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        );
        
        const data = response.data;
        
        let imagePath = data.image_path;
        if (imagePath) {
          if (!imagePath.startsWith('/')) {
            imagePath = '/' + imagePath;
          }
          const imageUrl = `http://localhost:8000${imagePath}`;
          setImageLoading(true);
          setCapturedPhoto(imageUrl);
        } else {
          setError('No image path received from server');
        }
        
        setCaption(data.caption || 'Photo uploaded successfully!');
        setAnalytics(data.analytics);
        setFaces(data.faces || []);
        setMusicRecommendation(data.music_recommendation);
        setLoading(false);
      };
      
      reader.onerror = () => {
        setError('Failed to read file');
        setLoading(false);
      };
      
      reader.readAsDataURL(file);
      
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.response?.data?.detail || 'Failed to upload photo. Please try again.');
      setLoading(false);
    }
  };

  const handleLikeSong = async (track, mood) => {
    try {
      const token = localStorage.getItem('firebaseToken');
      const songId = track.video_id || track.track_id || '';
      if (!songId) return;

      const isLiked = likedSongs.has(songId);
      if (isLiked) {
        const newLiked = new Set(likedSongs);
        newLiked.delete(songId);
        setLikedSongs(newLiked);
      } else {
        const newLiked = new Set(likedSongs);
        newLiked.add(songId);
        setLikedSongs(newLiked);
        await axios.post('/api/music/like',
          { song_id: songId, artist: track.artist, track_name: track.title, mood: mood || 'neutral' },
          { headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } }
        );
      }
    } catch (err) {
      console.error('Error liking song:', err);
      const songId = track.video_id || track.track_id || '';
      const newLiked = new Set(likedSongs);
      newLiked.delete(songId);
      setLikedSongs(newLiked);
    }
  };

  const handleDislikeSong = async (track, mood) => {
    try {
      const token = localStorage.getItem('firebaseToken');
      const songId = track.video_id || track.track_id || '';
      if (!songId) return;

      const isDisliked = dislikedSongs.has(songId);
      if (isDisliked) {
        const newDisliked = new Set(dislikedSongs);
        newDisliked.delete(songId);
        setDislikedSongs(newDisliked);
      } else {
        const newDisliked = new Set(dislikedSongs);
        newDisliked.add(songId);
        setDislikedSongs(newDisliked);
        await axios.post('/api/music/dislike',
          { song_id: songId, artist: track.artist, track_name: track.title, mood: mood || 'neutral' },
          { headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } }
        );
      }
    } catch (err) {
      console.error('Error disliking song:', err);
      const songId = track.video_id || track.track_id || '';
      const newDisliked = new Set(dislikedSongs);
      newDisliked.delete(songId);
      setDislikedSongs(newDisliked);
    }
  };

  const handleSave = () => {
    if (capturedPhoto) {
      const link = document.createElement('a');
      link.href = capturedPhoto;
      link.download = `smart-camera-${Date.now()}.jpg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  if (!user) {
    return null;
  }

  return (
    <motion.div
      className="page camera-page"
      initial={{ x: '100%' }}
      animate={{ x: 0 }}
      exit={{ x: '-100%' }}
      transition={{ type: 'spring', stiffness: 100, damping: 20 }}
    >
      {/* Hidden audio player for song previews */}
      <audio id="songPlayer" style={{ display: 'none' }} />
      
      <div className="camera-container">
        {!capturedPhoto && !mode ? (
          // Mode selection screen
          <motion.div
            className="mode-selection"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <h2 className="mode-title">Choose an Option</h2>
            <div className="mode-buttons">
              <motion.button
                className="mode-btn"
                onClick={() => setMode('capture')}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <div className="mode-icon">📷</div>
                <div className="mode-label">Capture Photo</div>
                <div className="mode-description">Auto-capture with smile detection</div>
              </motion.button>
              
              <motion.button
                className="mode-btn"
                onClick={() => document.getElementById('file-upload').click()}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <div className="mode-icon">📁</div>
                <div className="mode-label">Upload Photo</div>
                <div className="mode-description">Analyze an existing photo</div>
              </motion.button>
              
              <input
                id="file-upload"
                type="file"
                accept="image/*"
                style={{ display: 'none' }}
                onChange={handleFileUpload}
              />
            </div>
          </motion.div>
        ) : !capturedPhoto && mode === 'upload' && loading ? (
          // Upload loading screen
          <motion.div
            className="upload-loading"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
          >
            <div className="spinner-large"></div>
            <h3>Analyzing your photo...</h3>
            <p>Running smile detection, emotion analysis, and generating music recommendations</p>
          </motion.div>
        ) : !capturedPhoto && mode === 'capture' ? (
          <motion.div
            className="camera-section"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <div className="camera-preview">
              {/* Guidance message at top */}
              {streaming && detectionResults && detectionResults.guidance && (
                <div className="guidance-message-top">
                  {detectionResults.guidance}
                </div>
              )}
              
              <video
                ref={videoRef}
                playsInline
                muted
                style={{
                  width: '100%',
                  maxWidth: '640px',
                  borderRadius: '12px',
                  transform: 'scaleX(-1)' // Mirror effect
                }}
              />
              <canvas ref={canvasRef} style={{ display: 'none' }} />
              
              {/* Detection overlay */}
              {streaming && detectionResults && (
                <div className="detection-overlay">
                  <div className="detection-info">
                    <p>
                      <span className="live-indicator">●</span> Faces: {detectionResults.face_count}
                    </p>
                    {detectionResults.face_count > 0 && (
                      <>
                        <p className="smile-counter-display">
                          Smile: {smileCounter} / {SMILE_THRESHOLD}
                        </p>
                        {detectionResults.faces.map((face, idx) => (
                          <div key={idx} className="face-info">
                            <span>{face.age_range} </span>
                            <span>{face.gender} </span>
                            <span>{face.smile_detected ? '😊' : '😐'}</span>
                          </div>
                        ))}
                      </>
                    )}
                    {detectionResults.processing_time_ms && (
                      <p className="processing-time">
                        {detectionResults.processing_time_ms}ms
                      </p>
                    )}
                  </div>
                </div>
              )}
              
              {!streaming && !loading && !captureLockRef.current && (
                <div className="camera-loading">
                  <div className="spinner"></div>
                  <p>Starting camera...</p>
                </div>
              )}
              
              {error && <p className="error-text">{error}</p>}
              
              {loading && (
                <div className="capturing-overlay">
                  <div className="spinner"></div>
                  <p>Capturing...</p>
                </div>
              )}
            </div>
          </motion.div>
        ) : (
          <div className="capture-result">
            {/* Left Column */}
            <div className="left-column">
              <motion.div
                className="photo-section"
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.5 }}
              >
                <motion.img
                  src={capturedPhoto}
                  alt="Captured"
                  className="captured-photo"
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ duration: 0.5 }}
                  onLoad={() => {
                    console.log('Image loaded successfully:', capturedPhoto);
                    setImageLoading(false);
                  }}
                  onError={(e) => {
                    console.error('Image failed to load:', capturedPhoto);
                    console.error('Image error event:', e);
                    setImageLoading(false);
                    setError('Failed to load captured image. Please try again.');
                  }}
                />
                
                {imageLoading && (
                  <div className="image-loading">
                    <div className="spinner"></div>
                    <p>Loading image...</p>
                  </div>
                )}
                
                {caption && (
                  <motion.p
                    className="photo-caption"
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ delay: 0.3 }}
                  >
                    {caption}
                  </motion.p>
                )}

                {/* Action Buttons - Inside photo section, below caption */}
                <motion.div
                  className="photo-actions"
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.4 }}
                >
                  <button className="btn btn-ghost" onClick={handleRetake}>
                    Retake
                  </button>
                  <button className="btn btn-primary" onClick={handleSave}>
                    Save to Device
                  </button>
                </motion.div>
              </motion.div>

              {/* Music Panel */}
              <AnimatePresence>
                {musicRecommendation && musicRecommendation.tracks && (
                  <motion.div
                    className="music-panel"
                    initial={{ y: 30, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    exit={{ y: 30, opacity: 0 }}
                    transition={{ type: 'spring', stiffness: 100, delay: 0.6 }}
                  >
                    <h3 className="panel-title">🎵 Music Suggestions</h3>
                    <p className="music-message">{musicRecommendation.message}</p>
                    
                    <div className="music-tracks">
                      {musicRecommendation.tracks.slice(0, 5).map((track, idx) => {
                        const trackId = track.video_id || track.track_id || null;
                        const isLiked = likedSongs.has(trackId);
                        const isDisliked = dislikedSongs.has(trackId);
                        const isSelectedForEmbed = selectedTrackForEmbed === track.embed_url;
                        
                        return (
                          <div 
                            key={trackId || idx} 
                            className={`track-card ${isSelectedForEmbed ? 'selected-embed' : ''} clickable`}
                            onClick={(e) => {
                              if (e.target.closest('.track-actions')) return;
                              if (track.embed_url) setSelectedTrackForEmbed(track.embed_url);
                            }}
                            style={{ cursor: 'pointer' }}
                          >
                            <div className="track-info">
                              <div className="track-title">
                                {isSelectedForEmbed && '🎵 '}
                                {track.title}
                              </div>
                              <div className="track-artist">{track.artist}</div>
                            </div>
                            <div className="track-actions">
                              <button
                                className={`like-btn ${isLiked ? 'liked' : ''}`}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleLikeSong(track, musicRecommendation.state);
                                }}
                                title={isLiked ? 'Unlike' : 'Like'}
                              >
                                {isLiked ? '❤️' : '♡'}
                              </button>
                              <button
                                className={`dislike-btn ${isDisliked ? 'disliked' : ''}`}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDislikeSong(track, musicRecommendation.state);
                                }}
                                title={isDisliked ? 'Un-dislike' : 'Dislike'}
                              >
                                {isDisliked ? '👎' : '👎'}
                              </button>
                              <a
                                href={track.watch_url || `https://www.youtube.com/results?search_query=${encodeURIComponent(track.title + ' ' + track.artist)}`}
                                target="_blank"
                                rel="noopener noreferrer"
                              className="track-youtube-btn"
                                onClick={(e) => e.stopPropagation()}
                                title="Open on YouTube"
                              >
                                {/* YouTube icon */}
                                <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                                  <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                                </svg>
                              </a>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* YouTube Embed Player */}
              <AnimatePresence>
                {selectedTrackForEmbed && (
                  <motion.div
                    className="youtube-embed-panel"
                    initial={{ y: 30, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    exit={{ y: 30, opacity: 0 }}
                    transition={{ type: 'spring', stiffness: 100, delay: 0.2 }}
                  >
                    <iframe
                      key={selectedTrackForEmbed}
                      id="youtube-player"
                      src={`${selectedTrackForEmbed}?autoplay=1&controls=1`}
                      width="100%"
                      height="80"
                      frameBorder="0"
                      allow="autoplay; encrypted-media"
                      allowFullScreen={false}
                      title="YouTube Player"
                      style={{ borderRadius: '8px' }}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Right Column - Analytics Panel */}
            <AnimatePresence>
              {analytics && (
                <motion.div
                  className="right-column"
                  initial={{ x: 50, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  exit={{ x: 50, opacity: 0 }}
                  transition={{ type: 'spring', stiffness: 100, delay: 0.5 }}
                >
                  <div className="analytics-panel">
                    <h3 className="panel-title">Portrait Analytics</h3>
                    
                    <div className="analytics-metrics">
                      <div className="metric-card">
                        <div className="metric-label">Smile Score</div>
                        <div className="metric-value">{analytics.smile_score?.toFixed(1)}%</div>
                        <div className="metric-bar">
                          <div 
                            className="metric-fill"
                            style={{ width: `${analytics.smile_score}%` }}
                          />
                        </div>
                      </div>

                      <div className="metric-card">
                        <div className="metric-label">Face Lighting</div>
                        <div className="metric-value">{analytics.lighting?.toFixed(1)}%</div>
                        <div className="metric-bar">
                          <div 
                            className="metric-fill"
                            style={{ width: `${analytics.lighting}%` }}
                          />
                        </div>
                        <div className="metric-hint">Face illumination quality</div>
                      </div>

                      <div className="metric-card">
                        <div className="metric-label">Sharpness</div>
                        <div className="metric-value">{analytics.sharpness?.toFixed(1)}%</div>
                        <div className="metric-bar">
                          <div 
                            className="metric-fill"
                            style={{ width: `${analytics.sharpness}%` }}
                          />
                        </div>
                      </div>

                      <div className="metric-card">
                        <div className="metric-label">Alignment</div>
                        <div className="metric-value">{analytics.alignment?.toFixed(1)}%</div>
                        <div className="metric-bar">
                          <div 
                            className="metric-fill"
                            style={{ width: `${analytics.alignment}%` }}
                          />
                        </div>
                      </div>

                      <div className="metric-card final-score">
                        <div className="metric-label">Final Score</div>
                        <div className="metric-value large">{analytics.final_score?.toFixed(1)}%</div>
                      </div>

                      {faces.length > 0 && (
                        <>
                          <div className="metric-card">
                            <div className="metric-label">Estimated Age</div>
                            <div className="metric-value">{faces[0].age_range}</div>
                          </div>
                          <div className="metric-card">
                            <div className="metric-label">Gender</div>
                            <div className="metric-value">{faces[0].gender}</div>
                          </div>
                        </>
                      )}
                    </div>

                    {analytics.explanations && analytics.explanations.length > 0 && (
                      <div className="explanations">
                        {analytics.explanations.map((exp, idx) => (
                          <div key={idx} className="explanation-item">
                            {exp}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
      </div>
    </motion.div>
  );
}

export default Camera;
