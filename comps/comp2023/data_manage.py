

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




# class TeamMatchReport:
#     "An object representing what a team did in a match based on Events and other match data. Should not be used to mutate or modify database contents, just for analytics."

#     def __init__(self, team_number:int, match_number:int):
#         self._init = False
#         self.team_number = team_number
#         self.match_number = match_number
#         #match_data = MatchData.get(MatchData._construct_id(team_number, match_number))
#         #all events
#         self.events:"list[Event]" = list(Event.search(team_number=team_number, match_number=match_number))
#         self.events.sort()
#         #event categories
#         self.event_categories:"dict[str, list[Event]]" = {
#             EventActions.PICK_UP:[],
#             EventActions.DROP:[],
#             EventActions.SCORE:[],
#             EventActions.DEFENSE:[]
#         }
#         self.started:Event = None
#         self.ended:Event = None
#         self.end_auto:Event = None #event that marks the end of auto
#         self.score_groups:"list[ScoreGroup]" = []
#         self.links:"list[tuple[ScoreGroup, ScoreGroup, ScoreGroup]]" = []
#         self.events_auto = []
#         self.events_teleop = []
#         self.score_deltas = []
#         #as seen on manual 6.4.3 (pg 46) {Award Name: value}
#         # cooperation bonus requires both alliances to do 3, so thats a MatchReport thing (boolean)
#         self.points_auto:"dict[str, int]" = {
#             ScoreAwardName.MOBILITY:0,
#             ScoreAwardName.GAME_PIECES:0,
#             # have docked and engaged points calculated in AllianceMatchReport (depends on stats of multiple team reports)
#         }
#         self.points_teleop:"dict[str, int]" = {
#             ScoreAwardName.GAME_PIECES:0,
#             ScoreAwardName.LINK:0,
#             ScoreAwardName.PARK:0
#         }
#         self.points_ranking:"dict[str, int]" = {
#             ScoreAwardName.SUSTAINABILITY:0,
#             ScoreAwardName.ACTIVATION:0 # figure out how this is earned, because one team can not earn 26 charging station points alone
#             # Tie and Win go in the AllianceMatchReport
#         }

#     def before_teleop(self, event:Event)->bool:
#         return event.time < self.end_auto.time

#     def initialize_report(self):
#         if self._init: return
#         self._init = True
#         self._categorize_events()
#         self._get_score_groups()
#         self._get_score_links()
#         self._get_score_deltas()
#         self._get_points()

#     def _categorize_events(self):
#         "Categorize events by action, timestamp, and other things."
#         #sort based on action name
#         for event in self.events:
#             if event.action in self.event_categories:
#                 self.event_categories[event.action].append(event)
#             elif not self.started and event.action == EventActions.START:
#                 self.started = event
#             elif not self.ended and event.action == EventActions.END:
#                 self.ended = event
#         #find the auto_end/teleop_start event and split events into auto and teleop lists
#         for i, event in enumerate(self.events):
#             if event.action == EventActions.END_AUTO:
#                 self.end_auto = event
#                 self.events_auto = self.events[:i]
#                 self.events_teleop = self.events[i+1:]
#                 break
#         else: # autogenerate self.end_auto event at 15 seconds from scout.html start timestamp if its missing in self.events, else set
#             self.end_auto = Event(EventActions.END_AUTO, self.started.time+timedelta(seconds=15), self.started.team_number, self.started.match_number, self.started.scouter_name)
#             for i, event in enumerate(self.events):
#                 if event.time < self.end_auto.time:
#                     self.events_auto.append(event)
#                 elif event.time >= self.end_auto.time:
#                     self.events_teleop = self.events[i:]
#                     break

#     def _get_score_links(self):
#         for irow in range(len(SCORE_GRID_ROW_INDEX)): #0, 1, 2
#             current_link:"list[ScoreGroup]" = []
#             for sg in self.score_groups:
#                 if not (sg.score and sg.row == irow):
#                     continue
#                 elif not current_link or sg.index == current_link[-1].index+1: #sg is first in link or sg is right after last
#                     current_link.append(sg)
#                 else:
#                     current_link = [sg] #the current link starts with this sg

#                 if len(current_link)==3:
#                     self.links.append(tuple(current_link))
#                     current_link.clear()

#     def _get_points(self):
#         for sg in self.score_groups:
#             if not sg.score:
#                 continue
#             if self.before_teleop(sg.second):
#                 self.points_auto[ScoreAwardName.GAME_PIECES] += sg.score+1
#             else:
#                 self.points_teleop[ScoreAwardName.GAME_PIECES] += sg.score

#functions


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
