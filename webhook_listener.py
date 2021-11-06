#!/usr/bin/python3
import flask
import sys
import argparse
import json
import os
import requests

app = flask.Flask("webhook-listener")

HTTP_FORBIDDEN      = 401

##### FRONTEND PATHS ########
@app.route('/', methods=["GET","POST"])
def hook():
    if flask.request.args["token"] != app.config["TOKEN"]:
        return ("Bad Token", HTTP_FORBIDDEN)

    jsonFixed = flask.request.data.decode("utf-8").strip("'").replace("\n","")
    jsonDict = json.loads(jsonFixed)
    jsonDict.update({"group" : "family"})
    jsonDict.update({"message" : jsonDict["content"]})
    requests.post(app.config["SIGNAL_GATEWAY"], json=jsonDict)
    return ("", 204)

@app.before_first_request
def init():
    pass

if __name__ == "__main__":

    parser  = argparse.ArgumentParser(description="Simple Webhook listener", \
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-i", "--interface", default="0.0.0.0", help="Interface to listen on")
    parser.add_argument("-p", "--port", default="5000", help="Port to listen on")
    parser.add_argument("-t", "--token", required=True, help="Token in request for auth")
    parser.add_argument("-g", "--gateway", required=True, help="Gateway to forward message to")

    args = parser.parse_args()
    app.config["TOKEN"] = args.token
    app.config["SIGNAL_GATEWAY"] = args.gateway
    app.run(host=args.interface, port=args.port)
