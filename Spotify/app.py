import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array
import base64
from io import BytesIO
from PIL import Image
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random

app = Flask(__name__, static_folder='build', static_url_path='')

CORS(app)

# Spotify API credentials
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', '6adcfeab3be445ef8390b981326e485f')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', '008b719df4bb47d8b2f3d026ada40044')

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

# Load the trained model
model = tf.keras.models.load_model('emotion_detection_hybrid.h5')

# Emotion map
emotion_map = {
    1: 'Anger',
    2: 'Disgust',
    3: 'Fear',
    4: 'Happy',
    5: 'Sad',
    6: 'Surprise',
    7: 'Neutral'
}

# Image preprocessing function
def preprocess_image(image_base64):
    img_data = base64.b64decode(image_base64.split(',')[1])
    img = Image.open(BytesIO(img_data))
    img = img.convert('L')  # Convert to grayscale
    img = img.resize((48, 48))  # Resize to match the model input size
    img_array = np.array(img).astype('float32') / 255.0  # Normalize
    img_array = np.expand_dims(img_array, axis=(0, -1))  # Expand dimensions for batch and channel
    return img_array


@app.route('/search', methods=['POST'])
def search():
    mood = request.form.get('mood')
    language = request.form.get('language')
    num_songs = int(request.form.get('num_songs'))
    access_token = session.get('access_token')

    if not access_token:
        return redirect(url_for('login'))
    
    search_url = 'https://api.spotify.com/v1/search'
    headers = {'Authorization': f'Bearer {access_token}'}
    query = f'{mood} {language}'
    params = {
        'q': query,
        'type': 'track',
        'limit': 50
    }
    
    response = requests.get(search_url, headers=headers, params=params)

    if response.status_code != 200:
        return f"Failed to retrieve songs: {response.json().get('error', {}).get('message', 'Unknown error')}"
    
    songs = response.json().get('tracks', {}).get('items', [])
    
    if songs:
        random_songs = random.sample(songs, min(num_songs, len(songs)))
        song_data = [
            {
                'name': song["name"],
                'artist': song["artists"][0]["name"],
                'track_id': song["id"]
            }
            for song in random_songs
        ]
        return {'songs': song_data}
    else:
        return {'songs': []}

# Function to fetch Spotify tracks based on emotion
def fetch_spotify_tracks(emotion):
    playlists = {
    'Happy': 'celebratory and joyful Telugu tracks',
    'Sad': 'healing and comforting Telugu melodies',
    'Anger': 'energetic and cathartic Telugu beats',
    'Surprise': 'vibrant and adventurous Telugu tracks',
    'Neutral': 'easy-going and balanced Telugu hits',
    'Disgust': 'refreshing and tranquil Telugu melodies',
    'Fear': 'motivational and uplifting Telugu songs',
}

    query = playlists.get(emotion, 'mood telugu music')
    results = sp.search(q=query, type='track', limit=50) 

    tracks = [
        {
            "name": track['name'],
            "artists": ", ".join(artist['name'] for artist in track['artists']),
            "embed_url": f"https://open.spotify.com/embed/track/{track['id']}",
            "track_url": f"https://open.spotify.com/track/{track['id']}"
        } for track in results['tracks']['items']
    ]
    
    random.shuffle(tracks)
    
    return tracks[:5]


@app.route('/upload_image', methods=['POST'])
def upload_image():
    try:
        image_data = request.form.get('image')
        
        img_array = preprocess_image(image_data)
        
        prediction = model.predict(img_array)
        emotion_index = np.argmax(prediction[0])
        detected_emotion = emotion_map[emotion_index + 1]
        
        songs = fetch_spotify_tracks(detected_emotion)
        
        return jsonify({"emotion": detected_emotion, "songs": songs})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to process the request"}), 400


# Serve React files in production
@app.route('/')
def serve_react_app():
    return send_from_directory(os.path.join(app.root_path, 'build'), 'index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
