#!/usr/bin/python3
import flask
import argparse

app = flask.Flask("webhook-listener")

##### FRONTEND PATHS ########
@app.route('/', methods=["GET","POST"])
def rootPage():
    if flask.request.method == "GET":
        return "Webhook Listener ist running"
    else:
        data = json.loads(flask.request.body)
        print(json.dumps(data))

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
