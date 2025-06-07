#!/usr/bin/env python3
# NatuurSpotter/main.py
# Start de Flask webserver / kiestt poort

from NatuurSpotter.app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
