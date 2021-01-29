import yaml
import spotipy
import random
from spotipy.oauth2 import SpotifyOAuth
from mycroft import MycroftSkill, intent_file_handler


class PlaySpotify(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        stream = open(
            '/opt/mycroft/skills/play-spotify-skill/spotipy.yaml', 'r')
        spotipyConfig = yaml.safe_load(stream)
        self.code = spotipyConfig.get('Code')

        scope = "user-read-playback-state user-modify-playback-state playlist-read-private playlist-read-collaborative"
        self.auth_manager = SpotifyOAuth(scope=scope, client_id=spotipyConfig.get(
            'ClientID'), client_secret=spotipyConfig.get('ClientSecret'), redirect_uri='http://127.0.0.1/', open_browser=False, username='javi_t')
        self.token_info = self.auth_manager.get_access_token(
            code=spotipyConfig.get('Code'), as_dict=True)
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)

    @intent_file_handler('play.artist.song.intent')
    def handle_play_artist_song(self, message):
        self.speak_dialog('play.artist.song.intent', {
                          'artist': message.data.get('artist'), 'song': message.data.get('song')})

    @intent_file_handler('play.playlist.intent')
    def handle_play_playlist(self, message):
        self.log.info(("The playlist is {}").format(
            message.data.get('playlist')))

        self.refreshToken()

        deviceId = self.getDevice()
        if deviceId == None:
            self.speak_dialog('play.device.notfound')
            return

        playlists = self.sp.current_user_playlists()
        while playlists:
            for _, playlist in enumerate(playlists['items']):
                name = playlist['name'].lower()
                if name == message.data.get('playlist'):
                    self.playPlaylist(deviceId, playlist['uri'], playlist['tracks']['total'])
                    self.speak_dialog('play.playlist', {
                        'playlist': message.data.get('playlist')})
                    return
            if playlists['next']:
                playlists = self.sp.next(playlists)
            else:
                playlists = None
        self.speak_dialog('play.playlist.notfound')

    @intent_file_handler('play.some.intent')
    def handle_play_some(self, message):
        self.log.info(("The genre is {}").format(
            message.data.get('type')))

        self.refreshToken()

        deviceId = self.getDevice()
        if deviceId == None:
            self.speak_dialog('play.device.notfound')
            return

        genres = self.sp.recommendation_genre_seeds()
        for _, genre in enumerate(genres['genres']):
            if genre == message.data.get('type'):
                query = ('name:{}').format(genre)
                recomendations = self.sp.search(query, limit=50, type='playlist', market='ES')
                playlistList = recomendations['playlists']
                self.log
                offset = random.randint(1, len(playlistList))
                for i, playlist in enumerate(playlistList):
                    if i==offset:
                        self.playPlaylist(deviceId, playlist['uri'], playlist['tracks']['total'])
                        self.speak_dialog('play.some', {'type': message.data.get('type')})
                        return

        self.speak_dialog('play.genre.notfound', {
                          'type': message.data.get('type')})

    @intent_file_handler('play.stop.intent')
    def handle_play_stop(self, message):
        self.log.info("Stopping...")
        self.refreshToken()

        deviceId = self.getDevice()
        if deviceId == None:
            self.speak_dialog('play.device.notfound')
            return

        self.sp.pause_playback(deviceId)
        self.speak_dialog('play.stop')

    @intent_file_handler('play.artist.intent')
    def handle_play_artist(self, message):
        self.speak_dialog(
            'play.artist', {'artist': message.data.get('artist')})

    def getDevice(self):
        devices = self.sp.devices()
        for _, device in enumerate(devices['devices']):
            if device['name'] == 'Mycroft':
                return device['id']
        return None

    def refreshToken(self):
        if self.auth_manager.is_token_expired(self.token_info):
            self.token_info = self.auth_manager.get_access_token(
                code=self.code, as_dict=True)

    def playPlaylist(self, deviceId, playlistUri, total):
        offset = random.randint(1, total)
        self.sp.start_playback(device_id=deviceId, context_uri=playlistUri, offset={'position': offset})
        self.sp.shuffle(True, device_id=deviceId)
        self.sp.repeat(True, device_id=deviceId)


def create_skill():
    return PlaySpotify()
