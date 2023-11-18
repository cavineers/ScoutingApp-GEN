from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
import os

DIR = os.path.dirname(__file__)
SUBMISSIONS_FILE = os.path.join(DIR, "submissions.txt")

#NOTE: the notes below are about scoring, points, etc
#cite: see manual 6.4:44-45 for time period between action taking place and when it counts for points
#cite: see manual 6.4.1:45 for scoring criteria
#cite: see manual 6.4.3:46-47 for point values

#cite: https://stackoverflow.com/a/43587551


    # @classmethod
    # def generate(cls, data:dict):
    #     "Create a MatchData object from raw data."
    #     preliminary_data = data.get(ContentKeys.PRELIMINARY_DATA,{})
    #     nav_stamps = data.get(ContentKeys.NAV_STAMPS,{})
    #     return cls(
    #         version=data.get(ContentKeys.VERSION),
    #         team_number=preliminary_data.get(ContentKeys.TEAM_NUMBER),
    #         match_number=preliminary_data.get(ContentKeys.MATCH_NUMBER),
    #         scouter_name=preliminary_data.get(ContentKeys.SCOUTER_NAME),
    #         score=data.get(ContentKeys.SCORE),
    #         pickups=data.get(ContentKeys.PICKUPS),
    #         drops=data.get(ContentKeys.DROPS),
    #         defenses=data.get(ContentKeys.DEFENSES),
    #         charge_state=data.get(ContentKeys.CHARGE_STATE),
    #         comments=data.get(ContentKeys.COMMENTS),
    #         end_auto=data.get(ContentKeys.END_AUTO),
    #         navigation_start=nav_stamps.get("home.html"),
    #         navigation_prematch=nav_stamps.get("prematch.html"),
    #         navigation_match=nav_stamps.get("scout.html"),
    #         navigation_result=nav_stamps.get("result.html"),
    #         navigation_finish=nav_stamps.get("qrscanner.html")

    # def contruct_defense_events(self)->"list[Event]":
    #     if self.defenses is None:
    #         raise KeyError(ContentKeys.DEFENSES)
    #     return [Event(EventActions.DEFENSE, timestamp, self.team_number, self.match_number, self.scouter_name) for timestamp in self.defenses]



def handle_upload(raw:"dict[str]"):
    "Handle data sent to the upload route"
    #TODO use scoutingutil stuff



def save_local(raw:"dict[str]|str"):
    "Save (append) the raw data to a local file."
    if not isinstance(raw, str):
        raw = json.dumps(raw)
    with open(SUBMISSIONS_FILE, "a" if os.path.isfile(SUBMISSIONS_FILE) else "w") as f:
        f.write(raw+"\n")


# def _debug(path:str): #debug used in scouting app presentation on 2/4/2023
#     from pprint import pprint
#     print("="*10+"RAW DATA"+"="*10)
#     pprint(parse_qr_code(path))
#     data:MatchData = load_qr_code(path)
#     print("\n"+"="*10+"EXTRACTED DATA"+"="*10)
#     for attr, value in data.items():
#         print(attr+":",value)
#     for attr, value in MatchData.__dict__.items():
#         if isinstance(value, property):
#             print(attr+":", getattr(data, attr))