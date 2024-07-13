from flask import Flask, render_template, jsonify, request
import vlc
import pyradios

app = Flask(__name__)

SERVERS = [
    "de1.api.radio-browser.info",
    "de2.api.radio-browser.info",
    "nl1.api.radio-browser.info",
    "at1.api.radio-browser.info",
    "fr1.api.radio-browser.info",
]

COMMON_GENRES = [
    "pop", "rock", "jazz", "classical", "electronic", "hiphop", "country", "reggae", "blues", "metal",
    "disco", "folk", "funk", "gospel", "latin", "soul", "techno", "trance", "world"
]

player = None

@app.route('/')
def index():
    return render_template('index.html', genres=COMMON_GENRES)

@app.route('/stations')
def get_stations():
    country = request.args.get('country')
    genre = request.args.get('genre')
    stations = fetch_radio_stations(country, genre)
    return jsonify(stations)

def fetch_radio_stations(country, genre):
    for server in SERVERS:
        try:
            rb = pyradios.RadioBrowser(base_url=f"https://{server}")
            stations = rb.search(country=country, tag=genre, limit=10)
            if stations:
                return stations
        except Exception as e:
            print(f"Error fetching stations from {server}: {e}")
    return []

@app.route('/play', methods=['POST'])
def play_station():
    global player
    url = request.json['url']
    if player and player.is_playing():
        player.stop()
    instance = vlc.Instance('--quiet', '--no-xlib')
    player = instance.media_player_new()
    media = instance.media_new(url)
    player.set_media(media)
    player.audio_set_volume(50)
    player.play()
    return jsonify({'status': 'playing'})

@app.route('/stop', methods=['POST'])
def stop_station():
    global player
    if player and player.is_playing():
        player.stop()
    return jsonify({'status': 'stopped'})

if __name__ == '__main__':
    app.run(debug=True)
