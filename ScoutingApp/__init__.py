from . import competition, configs
from datetime import datetime, tzinfo
from flask import abort, Flask, redirect, render_template, Response, request, send_file, url_for; import flask.app
import json
import os
import pytz
import traceback
import waitress #production quality WSGI server to host the flask app with. more: https://docs.pylonsproject.org/projects/waitress/en/stable/index.html


DEFAULT_TIMEZONE = datetime.now().astimezone().tzinfo

app = Flask(__name__)
app.url_map.strict_slashes = False

comps:"list[competition.Competition]" = []
not_content = []

def not_content_route(rule:str, onto=app, **options):
    "Mark route as a not-content-returning route. Internally uses route decorator from the object passed to onto. Default is app."
    def decor(f):
        not_content.append(rule)
        return onto.route(rule, **options)(f)
    return decor

#event handlers
@app.before_request
def before_request():
    print(f"[{datetime.now().strftime('%m/%d/%y - %H:%M:%S.%f')}] Got request {request.method} from {request.remote_addr}: {request.url}")

@app.after_request
def after_request(response:Response):
    print(f"[{datetime.now().strftime('%m/%d/%y - %H:%M:%S.%f')}] Got response {request.method} ({response.status}) from {request.remote_addr}: {request.url}")
    return response

#define routes
#for info on decorators, see https://realpython.com/primer-on-python-decorators/, or look up "python decorators"
@not_content_route("/")
def to_first_page():
    return redirect(url_for(compselect.__name__))

@app.route("/manifest.json")
def get_manifest():
    return send_file(os.path.abspath("manifest.json"))

@not_content_route("/sw.js")
def get_serviceworker():
    return send_file(os.path.join(app.static_folder, "js", "sw.js"))

@app.route("/index.html")
def index():
    return render_template("index.html")

@app.route("/help.html")
def help():
    return render_template("help.html")

@app.route("/compselect.html")
def compselect():
    return render_template("compselect.html", competitions={comp.display_name:f"/comps/{comp.name}/{comp.start_url}" for comp in comps})

#api routes
#cite: https://stackoverflow.com/a/13318415
def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

def _get_static_routes(dir=app.static_folder, name="static")->"list[str]":
    rtv = []
    for filename in os.listdir(dir):
        path = os.path.join(dir, filename)
        if os.path.isdir(path):
            rtv.extend(_get_static_routes(path, name=name+"/"+filename))
        elif os.path.isfile(path):
            rtv.append(f"/{name}/{filename}")
    return rtv

@not_content_route("/assets")
def assets():
    routes = list({
        url_for(rule.endpoint, **(rule.defaults or {}))
        for rule in app.url_map.iter_rules()
        if "GET" in rule.methods and has_no_empty_params(rule) and url_for(rule.endpoint, **(rule.defaults or {})) not in not_content
    })
    return json.dumps(routes+_get_static_routes())

@not_content_route("/ping")
def ping():
    return request.remote_addr or ""


#functions

def serve(host:str="localhost", port:int=8080):
    "Serve the webapp."
    print(f"Serving on {host}:{port}.")
    waitress.serve(app, host=host, port=int(port), threads=48)

def load_competitions(dir:str):
    "Load competition blueprints from the competitions folder. Default is 'comps'."
    dir = os.path.abspath(dir)
    for filename in os.listdir(dir): #get paths to all files
        path = os.path.join(dir, filename)
        if os.path.isdir(path):
            path = os.path.join(path, "__init__.py")
        if os.path.isfile(path) and path.endswith((".py", ".pyw")):
            try:
                comp = competition.import_competition(path, filename)
            except:
                traceback.print_exc() #print caught exception's traceback and message, continue
            else:
                #handle the rest outside of try as to not skip over any exceptions raised here
                add_competition(comp)
                print(f"Loaded blueprint for competition '{comp.name}'.")

def _request_get_key(d:dict, *keys:str, **defaults):
    rtv = {}
    for key in keys:
        if key not in d and key not in defaults:
            abort(400, f"Missing form key '{key}'.")
        rtv[key] = d[key] if key in d else defaults[key]

def form_get_key(*keys:str, **defaults):
    return _request_get_key(request.form, *keys, **defaults)

def args_get_key(*keys:str, **defaults):
    return _request_get_key(request.args, *keys, **defaults)

def add_competition(comp:competition.Competition):
    "Add the competition to the list if it hasn't already been added, register its blueprint."
    if comp in comps:
        return
    app.register_blueprint(comp.blueprint)
    comps.append(comp)

def get_timezone():
    "Get timezone set in configs, else use current timezone."
    c = configs.read_configs()
    return pytz.timezone(c[configs.TIMEZONE]) if configs.TIMEZONE in c else DEFAULT_TIMEZONE

def from_timestamp(value:int, tz:tzinfo=...)->datetime: #assuming that value is a javascript timestamp in ms since python takes timestamp in seconds
    return datetime.fromtimestamp(value/1000, tz=get_timezone() if tz is ... else tz)

def to_timestamp(dt:datetime)->int:
    return int(dt.timestamp()*1000) #from {seconds}.{microseconds} -> milliseconds