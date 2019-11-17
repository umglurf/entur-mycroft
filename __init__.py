from datetime import datetime, timezone
from mycroft import MycroftSkill, intent_file_handler
from .realtime import RealTime

# NSR:StopPlace:6024 - sinsenterrassen
# NSR:StopPlace:6035 - sinsen t-bane


class Entur(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        self.settings_change_callback = self.handle_websettings_update
        self.handle_websettings_update()

    @intent_file_handler('realtime.departure.intent')
    def handle_realtime_departure(self, message):
        if not self.settings.get('stops', None):
            self.speak_dialog('no.stops')
            return
        departures = self.real_time.get_departures(line=message.data.get('line'), transport_type=message.data.get('transport'))
        if len(departures) == 0:
            self.speak_dialog("no.departures")
            return
        departure = departures.pop(0)
        self.speak_dialog("next.departure", data={
            'destination': departure['destination'],
            'line': departure['line'], 
            'time': self._format_time(departure['departureTime'])
        }, wait=True)
        yesno = self.ask_yesno("More departures?")
        if yesno == 'yes':
            for departure in departures[0:5]:
                self.speak_dialog("next.departure", data={
                    'destination': departure['destination'],
                    'line': departure['line'], 
                    'time': self._format_time(departure['departureTime'])
                }, wait=True)

    def handle_websettings_update(self):
        stops = self.settings.get('stops', "").split(",")
        filters = self.settings.get('filter', "").split(",")
        try:
            self.real_time = RealTime(stops, filters)
        except:
            self.speak_dialog('invalid.stop')

    def _format_time(self, departure_time):
        time_diff = departure_time - datetime.now(timezone.utc)
        if time_diff.days > 0:
            if time_diff.days == 1:
                return "tomorrow at {} {}".format(departure_time.hour, departure_time.minute)
            else:
                return "{} days at {} {}".format(time_diff.days, departure_time.hour, departure_time.minute)
        if time_diff.seconds < 60:
            return "{} seconds".format(time_diff.seconds)
        minutes = int(time_diff.seconds / 60)
        if minutes < 30:
            return "{} minutes".format(minutes)
        return "at {} {}".format(departure_time.hour, departure_time.minute)

def create_skill():
    return Entur()

