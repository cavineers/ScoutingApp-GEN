from . import from_timestamp, to_timestamp
from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime, timedelta

ACTIONS:"set[EventAction]" = set()

@dataclass(slots=True)
class Event:
    "Baseclass for objects representing an event caused by one team that happened during a match."

    action:"EventAction"
    time:datetime
    team_number:int
    match_number:int
    scouter_name:int

    def __repr__(self):
        return f"<{type(self).__name__} '{self.action}' : {to_timestamp(self.time) or '-'} at {hex(id(self))}>"

    def __gt__(self, value):
        if isinstance(value, Event):
            return self.time > value.time
        else:
            return super().__gt__(value)

    def __lt__(self, value):
        if isinstance(value, Event):
            return self.time < value.time
        else:
            return super().__lt__(value)

    def __eq__(self, value):
        if isinstance(value, Event):
            return self.time == value.time and self.action == value.action
        else:
            return super().__eq__(value)

_BasicEventInfo = namedtuple("_BasicEventInfo", ("team", "match", "scouter"))

class EventAction:
    "Action for an Event."

    @staticmethod
    def default_get_from_timestamp(action:"EventAction", basic:_BasicEventInfo, raw:"dict[str]", data:"int|list[int]"):
        return (Event(action, from_timestamp(data), basic.team, basic.match, basic.scouter) if action.single else
                [Event(action, from_timestamp(d), basic.team, basic.match, basic.scouter) for d in data])

    def __init__(self, name:str, raw_attr:str, get:"function"=default_get_from_timestamp, single:bool=True):
        self.name = name
        self.raw_attr = raw_attr
        self._get = get
        self.single = single

    def get(self, basic_info:_BasicEventInfo, raw:"dict[str]"):
        return self._get(self, basic_info, raw, raw[self.raw_attr])
        
def get_event_deltas(events:"list[Event]", start_set:"set[EventAction]", stop_set:"set[EventAction]", drop_set:"set[EventAction]", match_drops_marker:"bool"=True)->"list[timedelta]":
    "Difference in time between events of one set and events of another set. Event list should be in chronological order for most realistic results."
    marker = None
    deltas = []
    for event in events:
        if event.action in stop_set and marker is not None:
            deltas.append(event.time-marker.time)
            if match_drops_marker: marker = None
        elif event.action in start_set:
            marker = event
        elif event.action in drop_set:
            marker = None
    return deltas

def construct_events(raw:"dict[str]", team_key:str, match_key:str, scouter_key:str):
    "Construct events"
    team_number = raw[team_key]
    match_number = raw[match_key]
    scouter_name = raw[scouter_key]

    events = []

    for action in ACTIONS:
        event = action.get(_BasicEventInfo(team_number, match_number, scouter_name), raw)
        if action.single:
            events.append(event)
        else:
            events.extend(event)
    return events

def get_events_once(events:"list[Event]", target:tuple, untarget:tuple, by:"function|None"=None, key:"function|None"=None):
    "Get a set of unique Event objects. Specify the contents of the set by assigning a callback to key to return the value stored."
    once = set()
    for event in events:
        e = event if by is None else by(event)
        if e in target:
            once.add(event if key is None else key(event))
        elif e in untarget:
            once.discard(event if key is None else key(event))
    return once

def add_actions(*actions:EventAction):
    "Add EventActions to the list of actions."
    ACTIONS.update(*actions)