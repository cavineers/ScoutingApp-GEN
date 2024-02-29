from collections.abc import MutableMapping
import json

# configuration file path
CONFIG_PATH = "config.json"

# keys for configuration parameters
SHEETS_ID = "SheetsId" #id of the google sheets file
SHEETS_OAUTH = "SheetsOAuth" #google sheets oauth json
SHEETS_TOKEN_PATH = "SheetsTokenPath" #path to the sheets oauth token file (generated) [optional]
SHEETS_SCOPES = "SheetsScopes" #sheets api scopes
DATA_INSERTS = "DataInserts" #sheets to insert data into
CONSTANTS = "ConstantsSheet" #sheet which contains constant values in each row where column A is the name and columns B onwards are the values.

# configs class for working with JSON config files as a dictionary
class Configs(MutableMapping):
    "Object for working with JSON config files as a dict."

    __slots__ = "path", "c", "auto_read", "auto_write"

    def __init__(self, path:str, c:dict[str]|None=None, auto_read:bool=True, auto_write:bool=True):
        # initialization of Configs object with file path, data dictionary, and auto-read/write settings
        self.path = path
        self.c = {} if c is None else c
        self.auto_read = auto_read
        self.auto_write = auto_write
        if auto_read:
            self.read()
    
    def __contains__(self, key:str):
        # check if a key is present in the data dictionary, optionally triggering an auto-read
        if self.auto_read:
            self.read()
        return key in self.c

    def __delitem__(self, key:str):
        # delete an item from the data dictionary, optionally triggering an auto-write
        del self.c[key]
        if self.auto_write:
            self.write()

    def __getitem__(self, key:str):
        # get an item from the data dictionary, optionally triggering an auto-read
        if self.auto_read:
            self.read()
        return self.c[key]

    def __iter__(self):
        if self.auto_read:
            self.read()
        return iter(self.c)

    def __len__(self):
        if self.auto_read:
            self.read()
        return len(self.c)

    def __setitem__(self, key:str, value):
        self.c[key] = value
        if self.auto_write:
            self.write()
    
    def clear(self):
        self.c.clear()
        if self.auto_write:
            self.write()
    
    def copy(self):
        t = type(self)
        rtv = t.__new__(t)
        for slot in t.__slots__:
            if slot != "c":
                setattr(rtv, slot, getattr(self, slot))
        if self.auto_read:
            self.read()
        rtv.c = self.c.copy()
        return rtv
    
    def get(self, key:str, default=None):
        if self.auto_read:
            self.read()
        return self.c.get(key, default)
    
    def items(self):
        if self.auto_read:
            self.read()
        return self.c.items()
    
    def keys(self):
        if self.auto_read:
            self.read()
        return self.c.keys()
    
    def pop(self, key:str, default=None):
        value = self.c.pop(key, default)
        if self.auto_write:
            self.write()
        return value
    
    def popitem(self):
        item = self.c.popitem()
        if self.auto_write:
            self.write()
        return item
    
    def setdefault(self, key:str, default=None):
        value = self.c.setdefault(key, default)
        if self.auto_write:
            self.write()
        return value
    
    def update(self, m, /, **kw):
        self.c.update(m, **kw)
        if self.auto_write:
            self.write()

    def values(self):
        if self.auto_read:
            self.read()
        return self.c.values()

    def read(self):
        "Read the file's JSON contents into the Configs object as a dict."
        # read JSON contents from the file into the data dictionary
        with open(self.path) as f:
            self.c.update(json.load(f))
    
    def write(self):
        "Write the Configs object's items into the file's contents as JSON."
        # write the data dictionary into the file as JSON
        with open(self.path, "w") as f:
            json.dump(self.c, f)


def load(path:str=None):
    "Load a config file at the given path, or at the default path if no path is given."
    # function to load a Configs object from a specified or default path
    return Configs(CONFIG_PATH if path is None else path)

def setdefaultpath(path:str):
    "Set the default config path and return the old value."
    # function to set the default config path and return the old value
    global CONFIG_PATH
    rtv = CONFIG_PATH
    CONFIG_PATH = path
    return rtv