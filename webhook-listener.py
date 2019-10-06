#!/usr/bin/python3
import flask
import argparse
import json
import os
import subprocess as sp

app = flask.Flask("webhook-listener")
TOKEN_HEADER = "X-Gitlab-Token"
PROJECT_IDENTIFIER  = "web_url"
SEPERATOR           = ","
config = {}

##### FRONTEND PATHS ########
@app.route('/', methods=["GET","POST"])
def rootPage():
    if flask.request.method == "GET":
        return "Webhook Listener ist running"
    else:
        data = flask.request.json
        print(json.dumps(flask.request.json, indent=4, sort_keys=True))

        # check for project in config #
        if data["project"][PROJECT_IDENTIFIER] not in config:
            return ("Rejected: project not identified in config", 400)

        token, scriptName = data["project"][PROJECT_IDENTIFIER]

        # check authentification #
        if TOKEN_HEADER not in flask.request.headers:
            return ("Rejected: secret token not found in request", 403)
        elif token != flask.request.headers[TOKEN_HEADER]:
            return ("Rejected: secret token found but is mismatch", 403)

        # try to execute script #
        try:
            executeScript(scriptName)
        except subprocess.CalledProcessError:
            return ("Failed: script execution on the server failed", 500)

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
