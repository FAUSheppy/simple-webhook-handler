#!/usr/bin/python3
import flask
import argparse
import json
import os
import subprocess

app = flask.Flask("webhook-listener")
TOKEN_HEADER = "X-Gitlab-Token"
PROJECT_IDENTIFIER  = "web_url"
SEPERATOR           = ","
COMMENT_INDICATOR   = "#"
config = {}

##### FRONTEND PATHS ########
@app.route('/', methods=["GET","POST"])
def rootPage():
    if flask.request.method == "GET":
        return "Webhook Listener ist running"
    else:
        data = flask.request.json
        print(json.dumps(flask.request.json, indent=4, sort_keys=True))

        # check for project in request
        project = None
        try:
            project = data["project"][PROJECT_IDENTIFIER]
        except KeyError:
            return ("Rejected: missing project/{} json path".format(PROJECT_IDENTIFIER), 400)

        # check for project in config #
        if not project or project not in config:
            return ("Rejected: project not identified in config", 401)

        token, scriptName = config[project]

        # check authentification #
        if TOKEN_HEADER not in flask.request.headers:
            return ("Rejected: secret token not found in request", 402)
        elif token != flask.request.headers[TOKEN_HEADER]:
            return ("Rejected: secret token found but is mismatch", 403)

        # try to execute script #
        try:
            executeScript(scriptName)
        except subprocess.CalledProcessError:
            return ("Failed: script execution on the server failed", 501)

        # signal successfull completion #
        return ("Success", 200)


def executeScript(scriptName):
    path = os.path.expanduser(scriptName)
    proc = subprocess.run(path)
    proc.check_returncode()

def readExecutionConfig(configFile):
    global config
    with open(configFile, "r") as f:
        for line in f:
            line = line.strip("\n")
            if line.startswith(COMMENT_INDICATOR):
                continue
            projectIdent, token, scriptName = line.split(SEPERATOR)
            config.update({projectIdent:(token, scriptName)})

if __name__ == "__main__":

    parser  = argparse.ArgumentParser(description="Simple Webhook listener", \
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-i", "--interface", default="0.0.0.0", help="Interface to listen on")
    parser.add_argument("-p", "--port", default="5000", help="Port to listen on")
    parser.add_argument("-c", default="webhook.config", help="Config for handling of webhooks")
    args = parser.parse_args()

    readExecutionConfig(args.c)
    app.run(host=args.interface, port=args.port)
