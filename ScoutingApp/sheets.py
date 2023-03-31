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