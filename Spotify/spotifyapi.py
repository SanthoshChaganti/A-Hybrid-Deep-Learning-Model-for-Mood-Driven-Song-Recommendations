from flask import Flask, redirect, request, session, url_for, render_template_string
import requests
import os
import random

app = Flask(__name__)

# Set a secret key for session management
app.secret_key = os.urandom(24)

# Spotify API credentials (replace with your actual credentials in environment variables)
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', '6adcfeab3be445ef8390b981326e485f')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', '008b719df4bb47d8b2f3d026ada40044')
REDIRECT_URI = 'http://localhost:5000/callback'
SCOPE = 'user-read-private user-read-email'

# HTML template with inline CSS for input form
input_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spotify Random Songs</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
        }
        .container {
            text-align: center;
            padding: 20px;
            border-radius: 8px;
            background-color: #ffffff;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            max-width: 400px;
            width: 100%;
        }
        h2 {
            color: #333;
        }
        form {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        label {
            font-weight: bold;
            color: #555;
            text-align: left;
            display: block;
            margin-bottom: 5px;
        }
        input {
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ccc;
            width: 100%;
            box-sizing: border-box;
        }
        button {
            padding: 10px;
            background-color: #1DB954;
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #1aa34a;
        }
    </style>
</head>
<body>

<div class="container">
    <h2>Change Your Mood</h2>
    <form action="/search" method="post">
        <label for="mood">Mood:</label>
        <input type="text" name="mood" id="mood" required>
        <label for="language">Language:</label>
        <input type="text" name="language" id="language" required>
        <label for="num_songs">Number of Songs:</label>
        <input type="number" name="num_songs" id="num_songs" min="1" max="20" required>
        <button type="submit">Search</button>
    </form>
</div>

</body>
</html>
'''

@app.route('/')
def home():
    return redirect(url_for('search_input'))

@app.route('/search_input')
def search_input():
    return render_template_string(input_template)

@app.route('/login')
def login():
    auth_url = f'https://accounts.spotify.com/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}'
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = 'https://accounts.spotify.com/api/token'
    
    response = requests.post(token_url, data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    })

    if response.status_code != 200:
        return f"Failed to get token: {response.json().get('error_description', 'Unknown error')}"

    data = response.json()
    session['access_token'] = data.get('access_token')
    
    return redirect(url_for('search_input'))

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
        song_list_html = ''.join(
            f'<li>{song["name"]} by {song["artists"][0]["name"]}<br>'
            f'<iframe src="https://open.spotify.com/embed/track/{song["id"]}" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe></li><br>'
            for song in random_songs
        )
        
        output = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{mood.capitalize()} Songs in {language.capitalize()}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f9;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    margin: 0;
                }}
                .container {{
                    text-align: center;
                    padding: 20px;
                    border-radius: 8px;
                    background-color: #ffffff;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                    max-width: 400px;
                    width: 100%;
                }}
                h2 {{
                    color: #333;
                }}
                ul {{
                    list-style-type: none;
                    padding: 0;
                    text-align: left;
                }}
                li {{
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>

        <div class="container">
            <h2>{mood.capitalize()} Songs</h2>
            <ul>{song_list_html}</ul>
            <a href="/search_input">Search Again</a>
        </div>

        </body>
        </html>
        '''
    else:
        output = '''
        <h2>No songs found.</h2>
        <a href="/search_input">Try a different search</a>
        '''
    
    return output

if __name__ == '__main__':
    app.run(debug=True)
