# What is this
This is a simple webhook listener, primarily built for GitLab. It listens for request containing a secret token and executes scripts according to config file. The tool expects a request to be a **POST**-request, to be in a *JSON* format, to carry the correct type **application/json**, to contain a a header with **secret token** (see *$TOKEN_HEADER*) and to contain the json path **project/$PROJECT\_IDENTIFIER**.

# Config file structure
The config file uses *COMMA* as a separator, lines are comments if they start with a *#*. Each line must feature a web\_url of the project, the authorization token and the script to be executed. Scripts referenced in the config must be executable.

    PROJECT,TOKEN,PATH_TO_SCRIPT

# Running behind NGINX for SSL
You can (and should) run this tool behind a reverse proxy handling SSL. I recommend nginx with this configuration. Note the *proxy_next_upstream*-directive which tells nginx, that it should only report a timeout as bad gateway, since the backend will respond with certain error codes to ease debugging.

    server {
        listen 443 ssl;
        location / {
            proxy_pass http://localhost:5184;
        }

        proxy_next_upstream timeout;
    }

# Response Codes
## 400 - project not identified in request
The field **project/$PROJECT\_IDENTIFIER** doesn't exist in the request.

## 401 - project not identified in config
The projects identification was found in the request, but not in the config file.

## 402 - secret token not found in request
The header with the name specified in *$TOKEN_HEADER* doesn't exist.

## 403 - secret token found but is mismatch
The project was found in the configuration and the correct header exists, but the header is either empty or the content (the token) of the header doesn't match the token specified in the configuration file.

# Contribution & Feature-Requests
Contributions and feature requests are welcomed but must retain the spirit of this been a simple solution for simple problems.
