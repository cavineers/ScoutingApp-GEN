from . import configs
import json
import os
import re

ID_PATTERN = "1[a-zA-Z0-9_-]{42}[AEIMQUYcgkosw048]"

def prompt_id()->str|None:
    id = input("Enter ID of google sheets file to interact with, or \"none\" to skip: ")
    while not re.fullmatch(ID_PATTERN, id):
        if id in ("none", "\"none\"", "skip", "null", "\"null\""):
            print("Skipping ID")
            return None
        id = input("Invalid ID. Enter a valid google sheets ID: ")
    return id

def prompt_oauth():
    oauth = input("Enter google API OAuth JSON (oneline), or \"none\" to skip: ")
    while True:
        if id in ("none", "\"none\"", "skip", "null", "\"null\""):
            print("Skipping ID")
            return None
        try:
            parsed = json.loads(oauth)
        except:
            oauth = input("Invalid JSON. Enter valid JSON: ")
        else:
            return parsed

def prompt_scopes()->list[str]:
    scopes = []
    print("Enter all of the scopes your project needs, or enter a blank input to stop adding scopes.")
    scope = input("Enter scope: ")
    while scope:
        scopes.append(scope.strip())
        scope = input("Enter scope: ")
    return scopes

def prompt_data_inserts()->list[str]:
    names = []
    print("Enter the name of all sheets in your google sheets file to add data to, or enter a blank input to stop adding sheets.")
    name = input("Enter sheet name: ")
    while name:
        names.append(name.strip())
        name = input("Enter sheet name: ")
    return names
        
def prompt_token_path()->str:
    path = input("Enter the path to keep your OAuth token at (\"token.json\" by default): ")
    if path:
        return path
    return "token.json"

def prompt_constants_sheet()->str:
    sheet = input("Enter the name of the sheet in your google sheets file to read constants from (\"Constants\" by default): ")
    if sheet:
        return sheet
    return "Constants"

def main():
    print("="*20,"Config Setup", "="*20)
    id = prompt_id()
    oauth = prompt_oauth()
    scopes = prompt_scopes()
    data_inserts = prompt_data_inserts()
    token_path = prompt_token_path()
    constants = prompt_constants_sheet()

    filename = input(f"Enter the path to keep your config file at (\"{configs.CONFIG_PATH}\" by default): ")

    if filename:
        if "." not in filename:
            filename += ".json"
    else:
        filename = configs.CONFIG_PATH
    
    with open(filename, "w") as f:
        json.dump({
            configs.SHEETS_ID: id,
            configs.SHEETS_OAUTH: oauth,
            configs.SHEETS_TOKEN_PATH: token_path,
            configs.SHEETS_SCOPES: scopes,
            configs.DATA_INSERTS: data_inserts,
            configs.CONSTANTS: constants
        }, f)

    print("Configs file generated at", os.path.abspath(filename))

    

if __name__ == "__main__":
    main()