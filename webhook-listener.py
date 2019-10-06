#!/usr/bin/python3
import flask
import argparse
import json

app = flask.Flask("webhook-listener")
TOKEN_HEADER = "X-Gitlab-Token"
PROJECT_IDENTIFIER  = "web_url"
config = {}

##### FRONTEND PATHS ########
@app.route('/', methods=["GET","POST"])
def rootPage():
    if flask.request.method == "GET":
        return "Webhook Listener ist running"
    else:
        data = flask.request.json
        print(json.dumps(flask.request.json, indent=4, sort_keys=True))

        # check request against configuration #
        if data["project"][PROJECT_IDENTIFIER] not in config:
            return ("Rejected: project not identified in config", 400)
        if TOKEN_HEADER not in flask.request.headers:
            return ("Rejected: secret token not found in request", 403)
        if config[data["project"][PROJECT_IDENTIFIER]] != flask.request.headers[TOKEN_HEADER]:
            return ("Rejected: secret token found but is mismatch", 403)


def readExecutionConfig():
    pass

if __name__ == "__main__":

    parser  = argparse.ArgumentParser(description="Simple Webhook listener", \
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-i", "--interface", default="0.0.0.0", help="Interface to listen on")
    parser.add_argument("-p", "--port", default="5000", help="Port to listen on")
    parser.add_argument("-c", default="webhook.config", help="Config for handling of webhooks")
    args = parser.parse_args()
    app.run(host=args.interface, port=args.port)
