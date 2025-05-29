#!/usr/bin/env python3
# main.py

from NatuurSpotter.app import app

if __name__ == "__main__":
    # draai op alle interfaces (handig bij Docker of VM)
    app.run(host="0.0.0.0", port=5000, debug=True)
