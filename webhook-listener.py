#!/usr/bin/python3
import flask
import argparse
import json

app = flask.Flask("webhook-listener")
SECRET_TOKEN_HEADER = "X-Gitlab-Token"
PROJECT_IDENTIFIER  = "web_url"
config = {}

##### FRONTEND PATHS ########
@app.route('/', methods=["GET","POST"])
def rootPage():
    if flask.request.method == "GET":
        return "Webhook Listener ist running"
    else:
        data = flask.request.json

        # check request against configuration #
        if data[PROJECT_IDENTIFIER] not in config:
            return ("Rejected: project not identified in config", 400)
        if SECRET_TOKEN_HEADER not in flask.request.headers:
            return ("Rejected: secret token not found in request", 403)
        if config[data[PROJECT_IDENTIFIER]] != flask.request.headers[SECRET_TOKEN_HEADER]:
            return ("Rejected: secret token found but is mismatch", 403)

        print(json.dumps(flask.request.json))

def readExecutionConfig():
    pass

if __name__ == "__main__":

    parser  = argparse.ArgumentParser(description="Simple Webhook listener", \
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-i", "--interface",     default="0.0.0.0",         help="Interface to listen on")
    parser.add_argument("-p", "--port",          default="5000",            help="Port to listen on")
    parser.add_argument("-e", "--execution-map", default="webhooks.config", help="Config for handling of webhooks")
    args = parser.parse_args()
    app.run(host=args.interface, port=args.port)
