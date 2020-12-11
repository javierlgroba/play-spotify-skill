from mycroft import MycroftSkill, intent_file_handler


class PlaySpotify(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('spotify.play.intent')
    def handle_spotify_play(self, message):
        self.speak_dialog('spotify.play')


def create_skill():
    return PlaySpotify()

