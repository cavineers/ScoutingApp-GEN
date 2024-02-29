from datetime import datetime, tzinfo, timedelta, timezone
import json
import os
import scoutingutil
from scoutingutil import Column, configs, Table, SheetsService

# constants used for key names
START = "start"
END = "end"
END_AUTO = "endAuto"
MATCH_INPUT_NAMES = ("score", "move", "pickup", "dropped", "defend")
LOCAL_TIMEZONE:tzinfo = datetime.now().astimezone().tzinfo

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

def from_utc_timestamp(value:int)->datetime: #assuming that value is a javascript timestamp in ms since python takes timestamp in seconds
    return datetime.fromtimestamp(value/1000, tz=timezone.utc).astimezone(LOCAL_TIMEZONE)

def to_utc_timestamp(dt:datetime)->int:
    return int(dt.astimezone(timezone.utc).timestamp()*1000) #from f"{seconds}.{microseconds}" -> milliseconds

# function to handle data uploaded to the server
def handle_upload(raw:"dict[str]"):
    "Handle data sent to the upload route"
    upload_datetime_str = datetime.now().isoformat()  # Get current date and time as ISO 8601 string
    raw['upload_date'] = upload_datetime_str

    # Parse ISO 8601 formatted string into datetime object
    upload_datetime = datetime.fromisoformat(upload_datetime_str)

    # Format datetime into a more human-readable format
    formatted_upload_date = upload_datetime.strftime('%m/%d/%Y')

    # Add formatted upload date to the data
    raw['formatted_upload_date'] = formatted_upload_date

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
    robotState = Column("ROBOT", "robotState")
    team = Column("TEAM", "preliminaryData", process_data=lambda ctx: ctx.data["team"])
    match = Column("MATCH", "preliminaryData", process_data=lambda ctx: ctx.data["match"], strict=True)
    scouter = Column("SCOUTER", "preliminaryData", process_data=lambda ctx: ctx.data["scouter"])
    upload_date = Column("DATE", "formatted_upload_date")
    
    #prematch page
    starting_piece = Column("STARTING PIECE", "startObject")
    starting_position = Column("STARTING POSITION", "roboPos")

    #auto page
    auto_action1 = Column("AUTO:ACTION 1", "autoAction1", process_data=count_column_auto)
    auto_action2 = Column("AUTO:ACTION 2", "autoAction2", process_data=count_column_auto)
    auto_action3 = Column("AUTO:ACTION 3", "autoAction3", process_data=count_column_auto)
    auto_action4 = Column("AUTO:ACTION 4", "autoAction4", process_data=count_column_auto)
    stateOff_auto = Column("AUTO STATE", "autoState") 
    state1_auto = Column("AUTO STATE", "autoState")
    state2_auto = Column("AUTO STATE", "autoState") 
    
    #teleop page
    action1 = Column("ACTION 1", "teleAction1", process_data=count_column_teleop)
    action2 = Column("ACTION 2", "teleAction2", process_data=count_column_teleop)
    action3 = Column("ACTION 3", "teleAction3", process_data=count_column_teleop)
    action4 = Column("ACTION 4", "teleAction4", process_data=count_column_teleop)
    offState = Column("TELE STATE", "teleState") 
    state1 = Column("TELE STATE", "teleState")
    state2 = Column("TELE STATE", "teleState") 
    
    #result page
    comments = Column("COMMENTS", "comments", lambda ctx: ctx.data[0])
    
    #done