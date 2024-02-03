import data_manage
from datetime import datetime, timezone
from flask import Flask, redirect, render_template, Response, request, send_file, url_for
import json
import os
import waitress # production quality WSGI server to host the flask app with. more: https://docs.pylonsproject.org/projects/waitress/en/stable/index.html
import traceback

# directory and file paths
DIR = os.path.dirname(__file__)
SUBMISSIONS_FILE = os.path.join(DIR, "submissions.txt")
NAMES_FILE = os.path.join(DIR, "names.txt")

# flask app instantiation
app = Flask("routes")
app.url_map.strict_slashes = False

# cache control
not_content = []

# function to mark a route as a not-content-returning route
def not_content_route(rule:str, onto=app, **options):
    "Mark route as a not-content-returning route. Internally uses route decorator with the object passed to onto. Default is app."
    def decor(f):
        not_content.append(rule)
        return onto.route(rule, **options)(f)
    return decor

# serving manifest.json file
@app.route("/manifest.json")
def get_manifest():
    return send_file(os.path.abspath("manifest.json"))

# serving service worker JavaScript file (sw.js)
@not_content_route("/sw.js")
def get_serviceworker():
    return send_file(os.path.join("static", "js", "sw.js"), mimetype="text/javascript")

# api routes
# cite: https://stackoverflow.com/a/13318415
def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

# function to get static routes
def _get_static_routes(dir="static", name="static")->"list[str]":
    rtv = []
    for filename in os.listdir(dir):
        path = os.path.join(dir, filename)
        if os.path.isdir(path):
            rtv.extend(_get_static_routes(path, name=name+"/"+filename))
        elif os.path.isfile(path):
            rtv.append(f"/{name}/{filename}")
    return rtv

# serving assets
@not_content_route("/assets")
def assets():
    routes = list({
        url_for(rule.endpoint, **(rule.defaults or {}))
        for rule in app.url_map.iter_rules()
        if "GET" in rule.methods and has_no_empty_params(rule) and url_for(rule.endpoint, **(rule.defaults or {})) not in not_content
    })
    return json.dumps(routes+_get_static_routes())

# ping route
@not_content_route("/ping")
def ping():
    return "pong" #TODO return something more useful later
# ping pong (like the game, yk? jk its not like the game, but still funny to think about)

# event handlers
@app.before_request
def before_request():
    print(f"[{datetime.now(timezone.utc).strftime('%m/%d/%y - %H:%M:%S.%f')}] Got request {request.method} from {request.remote_addr}: {request.url}")

@app.after_request
def after_request(response:Response):
    print(f"[{datetime.now(timezone.utc).strftime('%m/%d/%y - %H:%M:%S.%f')}] Got response {request.method} ({response.status}) from {request.remote_addr}: {request.url}")
    return response

# define routes
# for info on decorators, see https://realpython.com/primer-on-python-decorators/, or look up "python decorators"
@app.get("/")
def to_first_page():
    return redirect(url_for("home"))

# scouting routes
@app.route("/home.html")
def home():
    with open(NAMES_FILE) as f:
        return render_template("home.html", names=[name.strip() for name in f.readlines()])

@app.route("/scout.html")
def scout():
    return render_template("scout.html")

@app.route("/prematch.html")
def auto():
    return render_template("prematch.html")

@app.route("/result.html")
def result():
    return render_template("result.html")

@app.route("/names")
def names():
    with open(NAMES_FILE) as f:
        return json.dumps([name.strip() for name in f.readlines()])

# api routes
UPLOAD_DATA_KEY = "data"
@app.post("/upload")
def upload():
    try:
        if UPLOAD_DATA_KEY in request.form:
            data = json.loads(json.loads(request.form[UPLOAD_DATA_KEY]))
        else:
            return f"You must upload a JSON data under key '{UPLOAD_DATA_KEY}'.", 400
    except Exception as e:
        traceback.print_exception(e)
        return "Got error while reading uploaded data.", 500
    try:
        data_manage.handle_upload(data)
    except Exception as e:
        traceback.print_exception(e)
        return "Got error while storing uploaded data.", 500
    else:
        print(request.remote_addr, "uploaded data:", repr(data))
        return "Committed uploaded data.", 200

# function to serve the webapp 
def serve(host:str="0.0.0.0", port:int=80):
    "Serve the webapp."
    print("Serving", host, f"on port {port}.")
    waitress.serve(app, host=host, port=int(port), threads=48)