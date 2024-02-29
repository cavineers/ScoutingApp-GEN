from . import configs, tables # import modules from the current package (relative imports)
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
import os

COLUMNS_CONSTANT_NAME = "COLUMNS" # constant for the name of the columns in the Google Sheets

# class for interacting with Google Sheets
class SheetsService:
    def __init__(self, id:str=None, oauth:dict[str]=None, token_path:str=None, scopes:list[str]=None, data_inserts:list[str]=None,
                 constants_sheet_name:str=None, sheets_constants:dict[str]=None):
        # initialization of SheetsService object with various configuration parameters
        self.id = id
        self.oauth = oauth
        self.token_path = token_path
        self.scopes = [] if scopes is None else scopes
        self.data_inserts = [] if data_inserts is None else data_inserts
        self.constant_sheet_name = constants_sheet_name
        self.sheets_constants = {} if sheets_constants is None else sheets_constants
        self._api_service:Resource = None

    # context manager methods to handle resource cleanup
    def __enter__(self)->Resource:
        if self._api_service is None:
            self._api_service = build("sheets", "v4", credentials=self.get_sheets_api_creds())
        return self._api_service.spreadsheets()
            
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._api_service is not None:
            self._api_service.close()
            self._api_service = None

    # method to update SheetsService with values from Configs object
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

    # method to obtain Google Sheets API credentials
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

    # method to retrieve constants from the Google Sheets
    def get_sheet_constants(self)->dict[str]:
        "Get constants from the google sheets."

        with self as sheets:
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
        
    # method to validate columns in a table based on Google Sheets constants
    def validate_columns(self, table:"type[tables.Table]"):
        "Returns the names of columns defined in Constants but missing in the given Table."
        missing = []
        table_column_names = (column.column_name for column in table.get_columns())
        for name in self.sheets_constants.get(COLUMNS_CONSTANT_NAME, ()):
            if name not in table_column_names:
                missing.append(name)
        return missing

    # method to save processed data to Google Sheets
    def save_to_sheets(self, *datas:"tables.Table"):
        "Save processed data to the google sheets."

        with self as sheets:
            insert_range = "A2:A" #range to insert into
            
            rows = []
            for data in datas:
                column_map = {column.column_name:attr for attr, column in data.get_column_pairs()}
                rows.append([getattr(data, column_map[column_name]) for column_name in self.sheets_constants[COLUMNS_CONSTANT_NAME]])

            #insert data
            for name in self.data_inserts:
                sheets.values().append(
                    spreadsheetId=self.id,
                    range=f"'{name}'!{insert_range}",
                    valueInputOption="RAW", insertDataOption="INSERT_ROWS", body={"values":rows}
                ).execute()

    # method to enter multiple ranges to the spreadsheet interpreted as user input
    def enter_ranges(self, sheet_name:str=None, **ranges:list[str]|list[list[str]]|str):
        "Enter multiple ranges to the spreadsheet interpreted as user input."
        #https://developers.google.com/sheets/api/guides/values#write_multiple_ranges
        with self as sheets:
            return sheets.values().batchUpdate(spreadsheetId=self.id, body={
                "valueInputOption":"USER_ENTERED",
                "data":[
                    {"range":name if sheet_name is None or "!" in name else f"{sheet_name}!{name}", "values":values}
                    for name, values in ranges.items()
                ]
            }).execute()

    # method to create a new spreadsheet
    def create_spreadsheet(self, name:str)->str:
        "Create a new spreadsheet. Returns the ID of the generated spreadsheet."

        with self as sheets:
            spreadsheet = sheets.create(body={"properties":{"title":name}},
                          fields="spreadsheetId").execute()
            return spreadsheet.get("spreadsheetId")
        
    # method to add a sheet to the spreadsheet
    def add_sheet(self, title:str, index:int, sheetType:str="GRID", hidden:bool=False, **props):
        "Add sheet to the spreadsheet."

        with self as sheets:
            sheets.batchUpdate(spreadsheetId=self.id, body={
                "requests":[{"addSheet":{
                    "properties":{
                        "title":title,
                        "index":index,
                        "sheetType":sheetType,
                        "hidden":hidden,
                        **props
                    }
                }}]}).execute()