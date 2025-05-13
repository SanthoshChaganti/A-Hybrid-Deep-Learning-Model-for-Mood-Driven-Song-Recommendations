from flask import Flask, request, jsonify
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

# Image preprocessing function
def preprocess_image(image_base64):
    img_data = base64.b64decode(image_base64.split(',')[1])
    img = Image.open(BytesIO(img_data))
    img = img.convert('L')  # Convert to grayscale
    img = img.resize((48, 48))  # Resizea to match the model input size
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
# Function to fetch Spotify tracks based on emotion
# Function to fetch Spotify tracks based on emotion


# def fetch_spotify_tracks(emotion):
#     playlists = {
#         'Happy': 'happy music',
#         'Sad': 'sad music',
#         'Anger': 'anger management',
#         'Surprise': 'energetic',
#         'Fear': 'calm',
#         'Disgust': 'relaxing',
#         'Neutral': 'chill'
#     }

#     playlist_name = playlists.get(emotion, 'pop')
#     results = sp.search(q=playlist_name, type='track', limit=5)
#     return [
#         {
#             'name': track['name'],
#             'artists': ', '.join(artist['name'] for artist in track['artists']),
#             'track_url': track['external_urls']['spotify']
#         }
#         for track in results['tracks']['items']
#     ]

def fetch_spotify_tracks(emotion):
    # Updated playlists based on emotion and focusing strictly on Telugu songs
    playlists = {
    'Happy': 'celebratory and joyful Telugu tracks',  
    # Uplifting and energetic songs to amplify the happiness and keep the positive vibes flowing.

    'Sad': 'healing and comforting Telugu melodies',  
    # Soothing tunes that evoke hope and offer solace, transitioning towards a lighter mood.

    'Anger': 'energetic and cathartic Telugu beats',  
    # Intense songs with powerful rhythms to channel the energy constructively and gradually introduce calming tracks to reduce tension.

    'Surprise': 'vibrant and adventurous Telugu tracks',  
    # Dynamic and upbeat songs that match the unexpected energy, helping maintain excitement with an optimistic touch.

    'Neutral': 'easy-going and balanced Telugu hits',  
    # Relaxing, feel-good tracks with a moderate tempo to keep the mood steady and encourage lightheartedness.

    'Disgust': 'refreshing and tranquil Telugu melodies',  
    # Calming and inspiring songs that help counter negativity, promoting relaxation and shifting towards a serene state.

    'Fear': 'motivational and uplifting Telugu songs',  
    # Empowering tracks that instill confidence and courage, gradually replacing fear with determination and positivity.
}

    
    # Get search query for Spotify based on the detected emotion
    query = playlists.get(emotion, 'mood telugu music')  # Default to 'mood telugu music' if emotion not found
    
    # Search for tracks on Spotify based on the query
    results = sp.search(q=query, type='track', limit=50)  # Fetch up to 50 tracks
    
    # Extract track details, focusing on embedding and providing URL to Spotify app
    tracks = [
        {
            "name": track['name'],
            "artists": ", ".join(artist['name'] for artist in track['artists']),
            "embed_url": f"https://open.spotify.com/embed/track/{track['id']}",
            "track_url": f"https://open.spotify.com/track/{track['id']}"  # Direct URL for playing in Spotify app
        } for track in results['tracks']['items']
    ]
    
    # Shuffle the tracks to provide random songs
    random.shuffle(tracks)
    
    # Return a subset of tracks (e.g., 5 random tracks)
    return tracks[:5]


# Route to handle image upload and emotion-based song recommendation
@app.route('/upload_image', methods=['POST'])
def upload_image():
    try:
        # Get image data from the request
        image_data = request.form.get('image')
        
        # Preprocess the image
        img_array = preprocess_image(image_data)
        
        # Predict emotion from the image
        prediction = model.predict(img_array)
        emotion_index = np.argmax(prediction[0])  # Get the emotion index
        detected_emotion = emotion_map[emotion_index + 1]  # Map index to emotion name
        
        # Fetch Spotify tracks based on the detected emotion
        songs = fetch_spotify_tracks(detected_emotion)
        
        # Return the emotion and corresponding songs in JSON format
        return jsonify({"emotion": detected_emotion, "songs": songs})
    
    except Exception as e:
        # Handle errors and return a JSON response with an error message
        print(f"Error: {e}")
        return jsonify({"error": "Failed to process the request"}), 400

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
