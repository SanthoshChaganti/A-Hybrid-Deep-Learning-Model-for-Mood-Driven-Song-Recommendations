import React, { useState } from 'react';

function SongsDisplay() {
  const [songs, setSongs] = useState([]);
  const [mood, setMood] = useState('');
  const [language, setLanguage] = useState('');
  const [numSongs, setNumSongs] = useState(5);

  const fetchSongs = async () => {
    const response = await fetch('http://localhost:5000/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ mood, language, num_songs: numSongs })
    });
    const data = await response.json();
    if (data.songs) {
      setSongs(data.songs);
    } else {
      console.error('Error fetching songs:', data.message);
    }
  };

  return (
    <div>
      <h1>Music Recommendations</h1>
      <form onSubmit={(e) => { e.preventDefault(); fetchSongs(); }}>
        <label>
          Mood:
          <input type="text" value={mood} onChange={(e) => setMood(e.target.value)} required />
        </label>
        <br />
        <label>
          Language:
          <input type="text" value={language} onChange={(e) => setLanguage(e.target.value)} required />
        </label>
        <br />
        <label>
          Number of Songs:
          <input type="number" value={numSongs} onChange={(e) => setNumSongs(e.target.value)} min="1" max="20" required />
        </label>
        <br />
        <button type="submit">Get Songs</button>
      </form>

      <div>
        <h2>Recommended Songs</h2>
        {songs.length > 0 ? (
          <ul>
            {songs.map((song, index) => (
              <li key={index}>
                <strong>{song.name}</strong> by {song.artist}
                <br />
                <a href={song.spotify_url} target="_blank" rel="noopener noreferrer">Listen on Spotify</a>
              </li>
            ))}
          </ul>
        ) : (
          <p>No songs found.</p>
        )}
      </div>
    </div>
  );
}

export default SongsDisplay;
