from . import configs
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
import os
import traceback
from typing import Any, Callable

COLUMNS_CONSTANT_NAME = "COLUMNS"

class Column:
    "Defines how data should be processed from raw data, and what google sheets column it should end up in."

    default_get:"Callable[[ProcessingContext], Any]" = lambda ctx: ctx.data

    def __init__(self, column_name:str, raw_attr:str|None=None, process_data:"Callable[[ProcessingContext], Any]"=default_get, strict=False):
        self.raw_attr = raw_attr
        self.column_name = column_name
        self.process_data = process_data
        self.strict = strict

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

class ProcessingContext:
    "Context used when processing raw data into column data."
    __slots__ = "sheets", "column", "raw", "data"

    def __init__(self, sheets:"SheetsData", column:"Column", raw:dict[str], data=None):
        self.sheets = sheets
        self.column = column
        self.raw = raw
        self.data = data

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
    def process_data(cls, raw_data:dict[str]):
        instance = cls.__new__(cls)
        for attr, column in cls.get_column_pairs():
            value = column.process_data(ProcessingContext(
                instance,
                column,
                raw_data,
                None if column.raw_attr is None else raw_data[column.raw_attr] if column.strict else raw_data.get(column.raw_attr)
            ))
            setattr(instance, attr, value)
        return instance

class SheetsService:
    def __init__(self, id:str=None, oauth:dict[str]=None, token_path:str=None, scopes:list[str]=None, data_inserts:list[str]=None,
                 constants_sheet_name:str=None, sheets_constants:dict[str]=None):
        self.id = id
        self.oauth = oauth
        self.token_path = token_path
        self.scopes = [] if scopes is None else scopes
        self.data_inserts = [] if data_inserts is None else data_inserts
        self.constant_sheet_name = constants_sheet_name
        self.sheets_constants = {} if sheets_constants is None else sheets_constants


    def config(self, c:"configs.Configs"):
        "Update SheetsService to use Configs values."
        #id
        self.id = c[configs.SHEETS_ID]
        #oauth
        self.oauth = c[configs.SHEETS_OAUTH]
        #token path
        token_path = c.get(configs.SHEETS_TOKEN_PATH, "token.json")
        self.token_path = (token_path if os.path.isabs(token_path) else
                            os.path.join(os.getcwd(), token_path))
        #scopes
        self.scopes = c[configs.SHEETS_SCOPES]
        #data inserts
        self.data_inserts = c[configs.DATA_INSERTS]
        #constants
        self.constant_sheet_name = c.get(configs.CONSTANTS, "Constants")
        #save all default values if missing
        c.update({
            configs.SHEETS_TOKEN_PATH:token_path,
            configs.CONSTANTS:self.constant_sheet_name
        })

        self.get_sheet_constants()

    def get_sheets_api_creds(self):
        "Get google sheets api creds from local files."
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(self.oauth, self.scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.token_path, "w") as token:
                token.write(creds.to_json())

        return creds


    def get_sheet_constants(self)->dict[str]:
        "Get constants from the google sheets."

        creds = self.get_sheets_api_creds()

        try:
            service:Resource = build("sheets", "v4", credentials=creds)
            sheets:Resource = service.spreadsheets()
            rtv = {}
            data = sheets.values().get(spreadsheetId=self.id, range=f"'{self.constant_sheet_name}'!A1:ZZZ").execute()
            if "values" in data:
                for row in data["values"]:
                    if not (row and row[0]):
                        continue #no name specified
                    name = row[0]
                    values = [v for v in row[1:] if v not in (None, "")]
                    if not values:
                        continue #no values, skip
                    elif len(values) > 1:
                        rtv[name] = values
                    else:
                        rtv[name] = values[0]
                self.sheets_constants.update(rtv)
                return rtv
            return self.sheets_constants.copy()
        except HttpError as e:
            traceback.print_exception(e)
        finally:
            if "service" in locals():
                service.close()

    def save_to_sheets(self, *datas:SheetsData):
        "Save processed data to the google sheets."

        creds = self.get_sheets_api_creds()

        try:
            insert_range = "A2:A" #range to insert into
            service:Resource = build("sheets", "v4", credentials=creds)
            sheets:Resource = service.spreadsheets()
            
            rows = []
            for data in datas:
                column_map = {column.column_name:attr for attr, column in data.get_column_pairs()}
                rows.append([getattr(data, column_map[column_name]) for column_name in self.sheets_constants[COLUMNS_CONSTANT_NAME]])

            #insert data
            for name in self.data_inserts:
                print(sheets.values().append(
                    spreadsheetId=self.id,
                    range=f"'{name}'!{insert_range}",
                    valueInputOption="RAW", insertDataOption="INSERT_ROWS", body={"values":rows}
                ).execute())
        except HttpError as e:
            traceback.print_exception(e)
        finally:
            if "service" in locals():
                service.close()