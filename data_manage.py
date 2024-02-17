from datetime import datetime, timedelta
import json
import os
import scoutingutil
from scoutingutil import Column, configs, Table, SheetsService

# constants used for key names
START = "start"
END = "end"
END_AUTO = "endAuto"
MATCH_INPUT_NAMES = ("score", "move", "pickup", "dropped", "defend")

# directory and file paths
DIR = os.path.dirname(__file__)
SUBMISSIONS_FILE = os.path.join(DIR, "submissions.txt")

sheets_api = SheetsService()

def init_sheets_api():
    if not os.path.isfile(scoutingutil.configs.CONFIG_PATH):
        raise FileNotFoundError("Must create a config.json file to read from.")
    cnfg = scoutingutil.configs.load()
    try:
        sheets_api.config(cnfg)
    except Exception as e:
        token_path = os.path.abspath(cnfg.get(configs.SHEETS_TOKEN_PATH, "token.json"))
        if os.path.isfile(token_path):
            os.remove(token_path)
            sheets_api.config(cnfg)
        else:
            raise

# function to parse ISO date string to datetime object
def parse_isodate(dstr:str):
    return datetime.fromisoformat(dstr.replace("Z", "+00:00"))

# function to iterate through auto data
def iter_auto(data, raw:dict[str]):
    if data is None:
        return
    end_auto = raw[END_AUTO]
    for dt in data:
        if dt > end_auto:
            return
        yield dt

# function to iterate through teleop data
def iter_teleop(data, raw:dict[str]):
    if data is None:
        return
    end_auto = raw[END_AUTO]
    for dt in data:
        if dt > end_auto:
            yield dt

# function to prepare data by converting ISO date strings to datetime objects
# im going to kill this stupid start/end def
def prep_data(data:dict[str]):
    if "start" not in data or "end" not in data:
        return
    #set all iso datetime strings to datetime objects
    data[START] = parse_isodate(data[START])
    data[END] = parse_isodate(data[END])
    for name in MATCH_INPUT_NAMES:
        if isinstance(data[name], list):
            data[name] = [parse_isodate(dtstr) for dtstr in data[name] if isinstance(dtstr, str)]
    
    if data.get(END_AUTO) is None:
        new_end = data[START]+timedelta(seconds=45)
        #get which one happened earlier
        data[END_AUTO] = min(new_end, data[END])
    else:
        data[END_AUTO] = parse_isodate(data[END_AUTO])

# function to handle data uploaded to the server
def handle_upload(raw:"dict[str]"):
    "Handle data sent to the upload route"
    save_local(raw)
    
    # prep_data(raw)
    
    row = ScoutingData.process_data(raw)
    
    sheets_api.save_to_sheets(row)

def save_local(raw:"dict[str]|str"):
    "Save (append) the raw data to a local file."
    if not isinstance(raw, str):
        raw = json.dumps(raw)
    with open(SUBMISSIONS_FILE, "a" if os.path.isfile(SUBMISSIONS_FILE) else "w") as f:
        f.write(raw+"\n")

# function to count auto columns
def count_column_auto(ctx:scoutingutil.ProcessingContext):
    return sum(1 for _ in iter_auto(ctx.data, ctx.raw))

# function to count teleop columns
def count_column_teleop(ctx:scoutingutil.ProcessingContext):
    return sum(1 for _ in iter_teleop(ctx.data, ctx.raw))

# definition of the ScoutingData class, inheriting from Table
class ScoutingData(Table):
    "Data on robot/human player's performance"
    
    #home page
    date = Column("DATE", "date")
    robot = Column("ROBOT", "robot")
    team = Column("TEAM", "team")
    match = Column("MATCH", "preliminaryData", process_data=lambda ctx: ctx.data["match"], strict=True)
    scouter = Column("SCOUTER", "scouter")
    
    #prematch page
    starting_piece = Column("STARTING PIECE", "startingpiece")
    starting_position = Column("STARTING POSITION", "startingpos")
    
    #auto page
    picked_up_note_auto = Column("AUTO:PICKED UP NOTE", "pickup", process_data=count_column_auto)
    missed_shot_auto = Column("AUTO:MISSED SHOT", "missed", process_data=count_column_auto)
    dropped_note_auto = Column("AUTO:DROPPED NOTE", "dropped", process_data=count_column_auto)
    
    #teleop page
    picked_up_note = Column("PICKED UP NOTE", "pickup", process_data=count_column_teleop)
    missed_shot = Column("MISSED SHOT", "missed", process_data=count_column_teleop)
    dropped_note = Column("DROPPED NOTE", "dropped", process_data=count_column_teleop)
    defense = Column("DEFENSE", "defense", process_data=count_column_teleop)
    cooperation = Column("COOPERATION BONUS", "cooperation", process_data=count_column_teleop)
    amplified = Column("AMPLIFIED BONUS", "amplified", process_data=count_column_teleop)
    offState = Column("CHAIN STATE", "chainState") 
    state1 = Column("CHAIN POSITION", "chainPosition")
    state2 = Column("CHAIN STATE", "chainState") 
    
    #result page
    comments = Column("COMMENTS", "comments", lambda ctx: ctx.data[0])
    
    #done