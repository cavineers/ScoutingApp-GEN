from datetime import datetime, timedelta, timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
import json
import os

ID:str = None
OAUTH:"dict[str]" = None
TOKEN_PATH:str = None
SCOPES:"list[str]" = []
SUBMISSIONS_FILE:str = None


class Column:
    "Defines how data should be processed from raw data, and what google sheets column it should end up in."

    default_get = lambda sheets, raw, data: data

    def __init__(self, raw_attr:str, column_name:str, process_data:"function"=default_get):
        self.raw_attr = raw_attr
        self.column_name = column_name
        self.process_data = process_data

    def get_var_name(self, t:type):
        "Get the name of the attribute that holds this column object."
        for attr, value in t.__dict__.items():
            if value is self:
                return attr
        raise AttributeError("Could not find attribute name for column.")

    def __get__(self, instance, owner:type):
        if instance is None:
            return self
        else:
            return instance.__dict__[self.get_var_name(type(instance))]
    
    def __set__(self, instance, value):
        if instance is not None:
            instance.__dict__[self.get_var_name(type(instance))] = value

class SheetsData:
    "Base class for object that stores collected and processed data to be sent to google sheets."

    @classmethod
    def get_column_pairs(cls):
        "Return each pair of attribute name and column object."
        for attr, var in cls.__dict__.items():
            if isinstance(var, Column):
                yield attr, var

    @classmethod
    def get_columns(cls):
        "Returns all column objects."
        for var in cls.__dict__.values():
            if isinstance(var, Column):
                yield var

    @classmethod
    def process_data(cls, raw_data:"dict[str]"):
        instance = cls.__new__(cls)
        for attr, column in cls.get_column_pairs():
            value = column.process_data(instance, raw_data, raw_data[column.raw_attr])
            setattr(instance, attr, value)
        return instance


class Event:
    "Object representing an event that happened during the match."

    def __init__(self, action:str, time:datetime, team_number:int, match_number:int, scouter_name:str, **other):
        self.action = action
        self.time = time if isinstance(time, datetime) else from_utc_timestamp(float(time))
        #reference fields: can be used in database subclass to access the related objects
        self.team_number = team_number
        self.match_number = match_number
        self.scouter_name = scouter_name
        self.other = other

    def __getitem__(self, key:str): return self.other[key]
    def __setitem__(self, key:str, value): self.other[key] = value

    def __repr__(self):
        return f"<Event '{self.action}' : {to_utc_timestamp(self.time) or '-'} at {hex(id(self))}>"

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
        
def _get_score_deltas(events:"list[Event]")->"list[timedelta]":
    pickup = None
    score_deltas = []
    for event in events:
        if event.action in (EventActions.PICK_UP, EventActions.PICK_UP_SHELF):
            pickup = event
        elif event.action == EventActions.SCORE and pickup is not None:
            score_deltas.append(event.time-pickup.time)
        elif event.action == EventActions.DROP:
            pickup = None
    return score_deltas

def construct_events(raw:"dict[str]"):
    team_number = raw.get(ContentKeys.TEAM_NUMBER)
    match_number = raw.get(ContentKeys.MATCH_NUMBER)
    scouter_name = raw.get(ContentKeys.SCOUTER_NAME)
    for index, history in raw.get(ContentKeys.SCORE,{}).items():
        for timestamp, game_piece in history.items():
            yield Event(
                EventActions.SCORE,
                timestamp,
                team_number,
                match_number,
                scouter_name,
                index=int(index),
                piece=game_piece
            )

    for timestamp in raw.get(ContentKeys.DROPS,()):
        yield Event(EventActions.DROP, timestamp, team_number, match_number, scouter_name)
    for timestamp in raw.get(ContentKeys.PICKUPS,()):
        yield Event(EventActions.PICK_UP, timestamp, team_number, match_number, scouter_name)
    for timestamp in raw.get(ContentKeys.SHELF_PICKUPS,()):
        yield Event(EventActions.PICK_UP_SHELF, timestamp, team_number, match_number, scouter_name)
    for timestamp in raw.get(ContentKeys.DEFENSES, ()):
        yield Event(EventActions.DEFENSE, timestamp, team_number, match_number, scouter_name)

def _get_unique_scores(score_range:"list[Event]", piece:str):
    s = set()
    for event in score_range:
        if event.other["piece"] == piece:
            s.add(event.other["index"])
        elif event.other["piece"] is None:
            s.discard(event.other["index"])
    return s

def process_events(events:"list[Event]")->"dict[str]":
    #cones&cubes bottom,middle,top; min,max,avg score delta
    deltas = _get_score_deltas(events)
    rows:"list[list[Event]]" = [] #top, middle, bottom
    for row_range in SCORE_GRID_ROW_INDEX:
        rows.append([event for event in events if event.action==EventActions.SCORE and event.other["index"] in row_range]) #get scores in top, middle, bottom respectively

    return {
        "cones_bottom":len(_get_unique_scores(rows[2], GamePiece.CONE)),
        "cones_middle":len(_get_unique_scores(rows[1], GamePiece.CONE)),
        "cones_top":len(_get_unique_scores(rows[0], GamePiece.CONE)),
        "cubes_bottom":len(_get_unique_scores(rows[2], GamePiece.CUBE)),
        "cubes_middle":len(_get_unique_scores(rows[1], GamePiece.CUBE)),
        "cubes_top":len(_get_unique_scores(rows[0], GamePiece.CUBE)),
        "min_score_delta":round(min(deltas).total_seconds(), 3) if deltas else 0,
        "max_score_delta":round(max(deltas).total_seconds(), 3) if deltas else 0,
        "avg_score_delta":round((sum(delta.total_seconds() for delta in deltas)/len(deltas)) if deltas else 0, 3)
    }

def from_utc_timestamp(value:int)->datetime: #assuming that value is a javascript timestamp in ms since python takes timestamp in seconds
    return datetime.fromtimestamp(value/1000, tz=timezone.utc).astimezone(LOCAL_TIMEZONE)

def to_utc_timestamp(dt:datetime)->int:
    return int(dt.astimezone(timezone.utc).timestamp()*1000) #from f"{seconds}.{microseconds}" -> milliseconds

def get_sheets_api_creds():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(OAUTH, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return creds

def get_sheet_columns()->list:
    "Get columns for the google sheets."

    creds = get_sheets_api_creds()

    try:
        service:Resource = build("sheets", "v4", credentials=creds)
        sheets:Resource = service.spreadsheets()
        data = sheets.values().get(spreadsheetId=ID, range="'Backup Data'!A1:1").execute()
        return data["values"][0] if "values" in data else []
    except HttpError as e:
        print(e)
    finally:
        if "service" in locals():
            service.close()

sheet_columns = [] #get_sheet_columns() TODO load after configs

def save_to_sheets(*datas:SheetsData):
    "Save processed data to the google sheets."

    creds = get_sheets_api_creds()

    try:
        insert_range = "A2:A" #range to insert into
        service:Resource = build("sheets", "v4", credentials=creds)
        sheets:Resource = service.spreadsheets()
        
        rows = []
        for data in datas:
            column_map = {column.column_name:attr for attr, column in data.get_column_pairs()}
            rows.append([getattr(data, column_map[column_name]) for column_name in sheet_columns])

        #insert data at the end of the Data sheet
        print(sheets.values().append(
            spreadsheetId=ID,
            range=f"Data!{insert_range}",
            valueInputOption="RAW", insertDataOption="INSERT_ROWS", body={"values":rows}
        ).execute())
        #insert data at the end of the Backup Data sheet
        print(sheets.values().append(
            spreadsheetId=ID,
            range=f"'Backup Data'!{insert_range}",
            valueInputOption="RAW", insertDataOption="INSERT_ROWS", body={"values":rows}
        ).execute())
    except HttpError as e:
        print(e)
    finally:
        if "service" in locals():
            service.close()

def save_local(raw:"dict[str]|str"):
    "Save (append) the raw data to a local file."
    if not isinstance(raw, str):
        raw = json.dumps(raw)
    with open(SUBMISSIONS_FILE, "a" if os.path.isfile(SUBMISSIONS_FILE) else "w") as f:
        f.write(raw+"\n")

def setup():
    global sheet_columns
    sheet_columns = get_sheet_columns()