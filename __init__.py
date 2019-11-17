from mycroft import MycroftSkill, intent_file_handler


class Entur(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('entur.intent')
    def handle_entur(self, message):
        self.speak_dialog('entur')


def create_skill():
    return Entur()

