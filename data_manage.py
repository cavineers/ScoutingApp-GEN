import json
import os

DIR = os.path.dirname(__file__)
SUBMISSIONS_FILE = os.path.join(DIR, "submissions.txt")

def handle_upload(raw:"dict[str]"):
    "Handle data sent to the upload route"
    #TODO use scoutingutil stuff

def save_local(raw:"dict[str]|str"):
    "Save (append) the raw data to a local file."
    if not isinstance(raw, str):
        raw = json.dumps(raw)
    with open(SUBMISSIONS_FILE, "a" if os.path.isfile(SUBMISSIONS_FILE) else "w") as f:
        f.write(raw+"\n")