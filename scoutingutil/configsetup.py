from . import configs # import the 'configs' module from the current package (relative import)
import json
import os
import re

ID_PATTERN = "1[a-zA-Z0-9_-]{42}[AEIMQUYcgkosw048]" # regular expression pattern for a Google Sheets ID

# function to prompt the user to enter a Google Sheets ID
def prompt_id()->str|None:
    id = input("Enter ID of google sheets file to interact with, or \"none\" to skip: ")
    while not re.fullmatch(ID_PATTERN, id):
        if id in ("none", "\"none\"", "skip", "null", "\"null\""):
            print("Skipping ID")
            return None
        id = input("Invalid ID. Enter a valid google sheets ID: ")
    return id

# function to prompt the user to enter Google API OAuth JSON
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

# function to prompt the user to enter Google Sheets API scopes
def prompt_scopes()->list[str]:
    scopes = []
    print("Enter all of the scopes your project needs, or enter a blank input to stop adding scopes.")
    scope = input("Enter scope: ")
    while scope:
        scopes.append(scope.strip())
        scope = input("Enter scope: ")
    return scopes

# function to prompt the user to enter sheet names to add data to in the Google Sheets file
def prompt_data_inserts()->list[str]:
    names = []
    print("Enter the name of all sheets in your google sheets file to add data to, or enter a blank input to stop adding sheets.")
    name = input("Enter sheet name: ")
    while name:
        names.append(name.strip())
        name = input("Enter sheet name: ")
    return names
        
# function to prompt the user to enter the path for the OAuth token file
def prompt_token_path()->str:
    path = input("Enter the path to keep your OAuth token at (\"token.json\" by default): ")
    if path:
        return path
    return "token.json"

# function to prompt the user to enter the name of the sheet containing constants in the Google Sheets file
def prompt_constants_sheet()->str:
    sheet = input("Enter the name of the sheet in your google sheets file to read constants from (\"Constants\" by default): ")
    if sheet:
        return sheet
    return "Constants"

# main function to run the configuration setup
def main():
    print("="*20,"Config Setup", "="*20)
    # prompt the user to enter configuration details
    id = prompt_id()
    oauth = prompt_oauth()
    scopes = prompt_scopes()
    data_inserts = prompt_data_inserts()
    token_path = prompt_token_path()
    constants = prompt_constants_sheet()

    # prompt the user to enter the path for the config file
    filename = input(f"Enter the path to keep your config file at (\"{configs.CONFIG_PATH}\" by default): ")

    if filename:
        if "." not in filename:
            filename += ".json"
    else:
        filename = configs.CONFIG_PATH
    
    # write the configuration details to the config file
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

# execute the main function if the script is run directly
if __name__ == "__main__":
    main()