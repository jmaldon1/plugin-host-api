"""Development configuration file.
"""
DESCRIPTION = "Plugin host api"
ENVIRONMENT = "DEV"

config = {
    "name": __name__,
    "description": DESCRIPTION,
    "environment": ENVIRONMENT,
    # Log level options: NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
    "log_level": "INFO",
    "api": {
        "host": "localhost",
        "port": 5000,
        "debug": True,
    },
    "postgrest": {
        "host": "http://127.0.0.1:3000/",
    }
}
