from datetime import datetime, timedelta
import json
import os
import scoutingutil
from scoutingutil import Column, Table

# constants used for key names
START = "start"
END = "end"
END_AUTO = "end-auto"
MATCH_INPUT_NAMES = ("score", "move", "pickup", "dropped", "defend")

# directory and file paths
DIR = os.path.dirname(__file__)
SUBMISSIONS_FILE = os.path.join(DIR, "submissions.txt")

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
def prep_data(data:dict[str]):
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
    #TODO use scoutingutil stuff
    save_local(raw) #remove this comment if you want to physically see the submission.txt file

# function to save (append) raw data to a local file
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
    match = Column("MATCH", "match", process_data=lambda ctx: int(ctx.data), strict=True)
    scouter = Column("SCOUTER", "scouter")
    
    #prematch page
    starting_piece = Column("STARTING  PIECE", "startingpiece")
    starting_position = Column("STARTING POSITION", "startingpos")
    
    #auto page
    picked_up_note_auto = Column("AUTO:ACTION 1", "pickup", process_data=count_column_auto)
    missed_shot_auto = Column("AUTO:ACTION 2", "missed", process_data=count_column_auto)
    dropped_note_auto = Column("AUTO:ACTION 3", "dropped", process_data=count_column_auto)
    dropped_note_auto = Column("AUTO:ACTION 3", "dropped", process_data=count_column_auto)
    
    #teleop page
    picked_up_note = Column("ACTION 1", "pickup", process_data=count_column_teleop)
    missed_shot = Column("ACTION 2", "missed", process_data=count_column_teleop)
    dropped_note = Column("ACTION 3", "dropped", process_data=count_column_teleop)
    defense = Column("ACTION 4", "defense", process_data=count_column_teleop)

    #result page
    comments = Column("COMMENTS", "comments")
    
    #done