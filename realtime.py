import dateutil.parser
import json
import re
import requests

API_URL = 'https://api.entur.io/journey-planner/v2/graphql'
REAL_TIME_QUERY = '''
query RealTime($stops: [String]) {
  stopPlaces(
    ids: $stops
  )

#### Requested fields
  {
    name
    id
    estimatedCalls {
      actualArrivalTime
      expectedDepartureTime
      forBoarding
      destinationDisplay {
        frontText
      }
      serviceJourney {
        line {
          publicCode
          transportMode
        }
      }
    }
  }
}
'''
STOP_QUERY = '''
query Stop($stop: String!) {
  stopPlace(id: $stop) {
    id
  }
}
'''

class RealTime:
    def __init__(self, stops, filters):
        self.stops = stops
        self.session = requests.Session()
        self.session.headers.update({
            'ET-Client-Name': 'mycroft-entur',
            'Content-Type': 'application/json'
            })
        self._validate_stops()
        if len(filters) > 0:
            self.filter = re.compile("|".join([re.escape(f) for f in filters]), re.IGNORECASE)
        else:
            self.filter = None

    def _validate_stops(self):
        for stop in self.stops:
            data = {'query': STOP_QUERY, 'variables': {'stop': stop} }
            response = self.session.post(API_URL, data=json.dumps(data))
            response.raise_for_status()
            stop_place = response.json()['data']['stopPlace']
            if (stop_place is not None and stop_place['id'] == stop):
                pass
            else:
                raise Exception("Invalid stop {}".format(stop))

    def get_departures(self, line = None, transport_type = None):
        data={'query': REAL_TIME_QUERY, 'variables': {'stops': self.stops}}
        response = self.session.post(API_URL, data=json.dumps(data))
        response.raise_for_status()
        departures = []
        for stop_place in response.json()['data']['stopPlaces']:
            for call in stop_place['estimatedCalls']:
                if not call['forBoarding']:
                    continue
                if self.filter is not None and self.filter.search(call['destinationDisplay']['frontText']):
                    continue
                if line is not None:
                    if not call['serviceJourney']['line']['publicCode'] == line:
                        continue
                if transport_type is not None:
                    if not call['serviceJourney']['line']['transportMode'] == transport_type:
                        continue
                if call['expectedDepartureTime'] is not None:
                    departure_time = dateutil.parser.parse(call['expectedDepartureTime'])
                elif call['actualArrivalTime'] is not None:
                    departure_time = dateutil.parser.parse(call['actualArrivalTime'])
                else:
                    continue
                departure = {
                        'stop': stop_place['name'],
                        'destination': call['destinationDisplay']['frontText'],
                        'departureTime': departure_time,
                        'line': call['serviceJourney']['line']['publicCode'],
                        'transportType': call['serviceJourney']['line']['transportMode']
                }
                departures.append(departure)

        return sorted(departures, key=lambda d: d['departureTime'])
