import json
import os

CONFIG_PATH = "config.json"

SHEETS_ID = "SheetsId"
SHEETS_OAUTH = "SheetsOAuth"
SHEETS_TOKEN_PATH = "SheetsTokenPath"
SHEETS_SCOPES = "SheetsScopes"
COMPETITIONS = "Competitions"
SUBMISSIONS_FILE = "SubmissionsFile"
TIMEZONE = "Timezone"

def read_configs()->"dict[str]":
    "Read values from the designated config file."
    if not os.path.isfile(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH) as f:
        return json.load(f)
    
def write_config(__d:"dict[str]", **config):
    "Write values to the designated config file."
    new = dict(__d, **config)
    to_write = read_configs()
    to_write.update(new)
    with open(CONFIG_PATH, "w") as f:
        json.dump(to_write, f)