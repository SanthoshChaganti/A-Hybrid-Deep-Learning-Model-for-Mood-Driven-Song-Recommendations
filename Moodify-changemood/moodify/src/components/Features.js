import React, { useState, useRef } from 'react';
import axios from 'axios';

function Features() {
  const [cameraOn, setCameraOn] = useState(false);
  const [imageSrc, setImageSrc] = useState(null);
  const [showSubmitDialog, setShowSubmitDialog] = useState(false);
  const [emotion, setEmotion] = useState(null);
  const [songs, setSongs] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const audioRefs = useRef([]);
  const [playingIndex, setPlayingIndex] = useState(null);

  const startCamera = async () => {
    setCameraOn(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;
    } catch (error) {
      console.error('Error accessing the camera:', error);
      alert('Unable to access the camera. Please check your device settings.');
      setCameraOn(false);
    }
  };

  const captureImage = () => {
    const context = canvasRef.current.getContext('2d');
    context.drawImage(videoRef.current, 0, 0, canvasRef.current.width, canvasRef.current.height);
    setImageSrc(canvasRef.current.toDataURL('image/png'));
    videoRef.current.srcObject.getTracks().forEach((track) => track.stop());
    setCameraOn(false);
    setShowSubmitDialog(true);
  };

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (!file || !file.type.startsWith('image/')) {
      alert('Please upload a valid image file.');
      return;
    }

    const reader = new FileReader();
    reader.onloadend = () => {
      setImageSrc(reader.result);
      setShowSubmitDialog(true);  // Show the submit button after file is uploaded
    };
    reader.readAsDataURL(file);
  };

  const handleRetake = () => {
    setShowSubmitDialog(false);
    setImageSrc(null);
    startCamera();
  };

  const handleSubmit = async () => {
    if (!imageSrc) {
      alert('No image to submit.');
      return;
    }

    setShowSubmitDialog(false);
    setIsSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('image', imageSrc);

      const response = await axios.post('http://localhost:5000/upload_image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setEmotion(response.data.emotion);
      setSongs(response.data.songs);
      alert('Image submitted successfully! Predicted Emotion: ' + response.data.emotion);
    } catch (error) {
      console.error('Error submitting image:', error);
      alert('Failed to submit the image. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePlayPause = async (index) => {
    try {
      const song = songs[index];

      if (song.track_url && song.track_url.includes('spotify.com')) {
        const trackId = song.track_url.split('/').pop().split('?')[0];
        if (trackId) {
          window.open(`https://open.spotify.com/embed/track/${trackId}`, '_blank');
          return;
        }
      }

      const currentAudio = audioRefs.current[index];
      if (!currentAudio) {
        console.error('Audio element not found for index:', index);
        return;
      }

      if (playingIndex !== null && playingIndex !== index) {
        const playingAudio = audioRefs.current[playingIndex];
        if (playingAudio) {
          await playingAudio.pause();
          playingAudio.currentTime = 0;
        }
      }

      if (currentAudio.paused) {
        await currentAudio.play();
        setPlayingIndex(index);
      } else {
        await currentAudio.pause();
        setPlayingIndex(null);
      }
    } catch (error) {
      console.error('Audio playback error:', error);
      alert('Unable to play the audio. Please try again.');
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Capture or Upload an Image</h1>

      <div style={styles.optionContainer}>
        <div style={styles.cameraContainer}>
          <button onClick={startCamera} style={styles.button} disabled={cameraOn || isSubmitting}>
            Open Camera
          </button>
          {cameraOn && (
            <div style={styles.videoContainer}>
              <video ref={videoRef} autoPlay style={styles.video}></video>
              <button onClick={captureImage} style={styles.captureButton}>
                Capture
              </button>
            </div>
          )}
        </div>

        <div style={styles.uploadContainer}>
          <input type="file" accept="image/*" onChange={handleImageUpload} style={styles.uploadButton} disabled={isSubmitting} />
        </div>
      </div>

      <div style={styles.imageSongsContainer}>
        {imageSrc && (
          <div style={styles.imageContainer}>
            <h2 style={styles.imageTitle}>Captured/Uploaded Image</h2>
            <img src={imageSrc} alt="Captured" style={styles.capturedImage} />
            {emotion && <div style={styles.emotionText}>Predicted Emotion: {emotion}</div>}
          </div>
        )}

        {songs.length > 0 && (
          <div style={styles.songsContainer}>
            <h3 style={styles.songsTitle}>Recommended Songs:</h3>
            <ul>
              {songs.map((song, index) => (
                <li key={index} style={styles.songItem}>
                  <p style={styles.songInfo}>
                    {song.name} by {song.artists}
                  </p>
                  {song.track_url && song.track_url.includes('spotify.com') ? (
                    <iframe
                      title={`Spotify track: ${song.name} by ${song.artists}`} // Adding title for accessibility
                      src={`https://open.spotify.com/embed/track/${song.track_url.split('/').pop()}`}
                      width="300"
                      height="80"
                      frameBorder="0"
                      allow="encrypted-media"
                      style={styles.spotifyEmbed}
                    ></iframe>
                  ) : (
                    <>
                      <audio
                        ref={(el) => (audioRefs.current[index] = el)}
                        src={song.track_url}
                        preload="auto"
                        style={{ width: '100%' }}
                      />
                      <button
                        style={styles.playPauseButton}
                        onClick={() => handlePlayPause(index)}
                      >
                        {playingIndex === index ? 'Pause' : 'Play'}
                      </button>
                    </>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {showSubmitDialog && (
        <div style={styles.dialog}>
          <h3 style={styles.dialogTitle}>Do you want to submit this image?</h3>
          <div>
            <button onClick={handleRetake} style={styles.dialogButton} disabled={isSubmitting}>
              Retake
            </button>
            <button onClick={handleSubmit} style={styles.dialogButton} disabled={isSubmitting}>
              Submit
            </button>
          </div>
        </div>
      )}

      {isSubmitting && <div style={styles.loading}>Submitting...</div>}

      <canvas ref={canvasRef} style={{ display: 'none' }} width="500" height="375"></canvas>
    </div>
  );
}

const styles = {
  container: {
    textAlign: 'center',
    color: 'white',
    padding: '20px',
    backgroundColor: '#001f3d',
    borderRadius: '15px',
    margin: '20px auto',
    maxWidth: '900px',
    boxShadow: '0 0 15px rgba(0, 0, 0, 0.7)',
  },
  title: {
    fontSize: '30px',
    fontWeight: 'bold',
    color: '#4a90e2',
    marginBottom: '30px',
  },
  optionContainer: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '20px',
    gap: '20px',
  },
  cameraContainer: {
    flex: 1,
    padding: '15px',
    backgroundColor: '#2e3b4e',
    borderRadius: '10px',
  },
  uploadContainer: {
    flex: 1,
    padding: '15px',
    backgroundColor: '#2e3b4e',
    borderRadius: '10px',
  },
  button: {
    padding: '12px 25px',
    backgroundColor: '#4a90e2',
    border: 'none',
    borderRadius: '5px',
    color: 'white',
    fontSize: '16px',
    cursor: 'pointer',
  },
  uploadButton: {
    padding: '12px 20px',
    width: '100%',
    backgroundColor: '#4a90e2',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontSize: '16px',
    color: 'white',
  },
  videoContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    marginTop: '15px',
  },
  video: {
    width: '320px', // Smaller width for the video window
    height: '240px', // Smaller height for the video window
    borderRadius: '10px',
    backgroundColor: '#000',
  },
  captureButton: {
    padding: '10px 20px',
    backgroundColor: '#4a90e2',
    border: 'none',
    borderRadius: '5px',
    color: 'white',
    marginTop: '10px',
    cursor: 'pointer',
    fontSize: '16px',
  },
  imageSongsContainer: {
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: '30px',
    gap: '20px',
  },
  imageContainer: {
    flex: 1,
    textAlign: 'center',
    padding: '20px',
    backgroundColor: '#3a4f6d',
    borderRadius: '10px',
  },
  imageTitle: {
    fontSize: '22px',
    fontWeight: 'bold',
    color: '#4a90e2',
    marginBottom: '15px',
  },
  capturedImage: {
    width: '100%',
    maxWidth: '500px',
    borderRadius: '10px',
    boxShadow: '0 0 10px rgba(0, 0, 0, 0.6)',
  },
  emotionText: {
    fontSize: '18px',
    fontWeight: 'bold',
    marginTop: '15px',
    color: '#76a9d1',
  },
  songsContainer: {
    flex: 1,
    textAlign: 'left',
    padding: '20px',
    backgroundColor: '#3a4f6d',
    borderRadius: '10px',
  },
  songsTitle: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#4a90e2',
    marginBottom: '15px',
  },
  songItem: {
    marginBottom: '20px',
    color: '#ddd',
  },
  songInfo: {
    fontSize: '16px',
    color: '#fff',
  },
  playPauseButton: {
    padding: '10px 20px',
    backgroundColor: '#4a90e2',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    marginTop: '10px',
  },
  spotifyEmbed: {
    marginTop: '15px',
    width: '100%',
    borderRadius: '10px',
  },
  dialog: {
    marginTop: '20px',
    padding: '20px',
    backgroundColor: '#2e3b4e',
    borderRadius: '10px',
    boxShadow: '0 0 10px rgba(0, 0, 0, 0.7)',
  },
  dialogTitle: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#4a90e2',
  },
  dialogButton: {
    padding: '10px 20px',
    backgroundColor: '#4a90e2',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    margin: '0 10px',
    fontSize: '16px',
  },
  loading: {
    marginTop: '20px',
    fontSize: '18px',
    color: '#76a9d1',
  },
};

export default Features;
