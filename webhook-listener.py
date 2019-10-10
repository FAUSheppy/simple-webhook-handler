#!/usr/bin/python3
import flask
import sys
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

HTTP_FORBIDDEN      = 401
HTTP_NOT_FOUND      = 404
HTTP_UNPROCESSABLE  = 422
HTTP_INTERNAL_ERR   = 500

##### FRONTEND PATHS ########
@app.route('/', methods=["GET","POST"])
def rootPage():
    if flask.request.method == "GET":
        return "Webhook Listener ist running"
    else:
        data = flask.request.json
        if data == None:
            retString = "POST-request is missing payload."
            print(retString, file=sys.stderr)
            return (retString, HTTP_UNPROCESSABLE)

        print(json.dumps(flask.request.json, indent=4, sort_keys=True))

        # check for project in request
        project = None
        try:
            project = data["project"][PROJECT_IDENTIFIER]
        except KeyError:
            retString = "Rejected: missing project/{} json path".format(PROJECT_IDENTIFIER)
            print(retString, file=sys.stderr)
            return (retString, HTTP_UNPROCESSABLE)

        # check for project in config #
        if not project or project not in config:
            retString = "Rejected: project not identified in config"
            print(retString, file=sys.stderr)
            return (retString, HTTP_NOT_FOUND)

        token, scriptName = config[project]

        # check authentification #
        if TOKEN_HEADER not in flask.request.headers:
            retString = "Rejected: secret token not found in request"
            print(retString, file=sys.stderr)
            return (retString, HTTP_FORBIDDEN)
        elif token != flask.request.headers[TOKEN_HEADER]:
            retString = "Rejected: secret token found but is mismatch"
            print(retString, file=sys.stderr)
            return (retString, HTTP_FORBIDDEN)

        # try to execute script #
        try:
            executeScript(scriptName)
        except subprocess.CalledProcessError:
            retString = "Failed: script execution on the server failed"
            print(retString, file=sys.stderr)
            return (retString, HTTP_INTERNAL_ERR)

        # signal successfull completion #
        return ("Success", 200)


def executeScript(scriptName):
    path = os.path.expanduser(scriptName)
    subprocess.Popen(path)

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
