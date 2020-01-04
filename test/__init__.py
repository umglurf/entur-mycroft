from datetime import datetime, timezone
from os.path import basename
from unittest.mock import MagicMock, patch
from test.integrationtests.skills.skill_tester import SkillTest
import types
import sys

def test_runner(skill, example, emitter, loader):
    # Get the skill object from the skill path
    s = [s for s in loader.skills if s and s.root_dir == skill]

    if basename(example) == '001.no.config.intent.json':
        return SkillTest(skill, example, emitter).run(loader)
    elif basename(example) == '002.invalid.stop.intent.json':
        with patch('requests.Session') as MockSession:
            MockSession.post.return_value = {"data": {"stopPlace": None}}
            return SkillTest(skill, example, emitter).run(loader)
    elif basename(example) == '003.no.departures.intent.json':
        with patch('requests.Session') as MockSession:
            instance = MockSession.return_value
            instance.post.return_value.json.return_value = {"data": {
                "stopPlace": {"id": "NSR:StopPlace:58366"},
                "stopPlaces": []
                }
            }
            return SkillTest(skill, example, emitter).run(loader)
    else:
        with patch(s[0].__module__ + '.realtime.RealTime') as MockRealTime:

            data = [
                    {
                        'stop': "Test place",
                        'destination': "Foobar",
                        'departureTime': datetime.now(timezone.utc),
                        'line': '1',
                        'transportType': 'metro'
                    }
            ]
            instance = MockRealTime.return_value
            instance.get_departures.return_value = data
            return SkillTest(skill, example, emitter).run(loader)

