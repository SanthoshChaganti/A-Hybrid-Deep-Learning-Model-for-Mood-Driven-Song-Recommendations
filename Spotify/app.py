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
import os
import random

app = Flask(__name__, static_folder='../Moodify-changemood/build', static_url_path='')
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

# Image preprocessing
def preprocess_image(image_base64):
    img_data = base64.b64decode(image_base64.split(',')[1])
    img = Image.open(BytesIO(img_data)).convert('L').resize((48, 48))
    img_array = np.array(img).astype('float32') / 255.0
    img_array = np.expand_dims(img_array, axis=(0, -1))
    return img_array

# Emotion-based song recommendation
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
    tracks = [{
        "name": track['name'],
        "artists": ", ".join(artist['name'] for artist in track['artists']),
        "embed_url": f"https://open.spotify.com/embed/track/{track['id']}",
        "track_url": f"https://open.spotify.com/track/{track['id']}"
    } for track in results['tracks']['items']]
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

# ✅ Serve React Frontend
@app.route('/')
def serve_react():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_react_static(path):
    file_path = os.path.join(app.static_folder, path)
    if os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Run locally
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
