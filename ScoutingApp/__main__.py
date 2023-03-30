from . import app, competition, configs, serve, sheets, load_competitions
import os
import sys

DIR = os.path.dirname(os.path.dirname(__file__))

def handle_configs(c:"dict[str]"):
    #set sheets values
    sheets.ID = c[configs.SHEETS_ID]
    sheets.OAUTH = c[configs.SHEETS_OAUTH]
    token_path = c.get(configs.SHEETS_TOKEN_PATH, "token.json")
    sheets.TOKEN_PATH = (token_path if os.path.isabs(token_path) else
                         os.path.join(DIR, token_path))
    sheets.SCOPES = c[configs.SHEETS_SCOPES]
    #set submission history file
    submissions_path = c.get(configs.SUBMISSIONS_FILE, "submissions.txt")
    sheets.SUBMISSIONS_FILE = (submissions_path if os.path.isabs(submissions_path) else
                               os.path.join(DIR, submissions_path))
    #set comps dir
    comps_dir = c.get(configs.COMPETITIONS, "comps")
    #save all default values if missing
    configs.write_config({
        configs.SHEETS_TOKEN_PATH:token_path,
        configs.SUBMISSIONS_FILE:submissions_path,
        configs.COMPETITIONS:comps_dir
    })
    sheets.setup()
    load_competitions(comps_dir if os.path.isabs(comps_dir) else
                      os.path.join(DIR, comps_dir))

def main(**kw):
    global DIR
    if "configs" in kw:
        configs.CONFIG_PATH = kw.pop("configs")
    if "dir" in kw:
        DIR = kw.pop("dir")
    handle_configs(configs.read_configs())
    serve(**kw)


def _get_args():
    for a in sys.argv[1:]:
        yield a.split("=",1)

if __name__ == "__main__":
    main(**{a[0]:a[1] for a in _get_args() if len(a)==2})