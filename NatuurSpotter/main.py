#!/usr/bin/env python3
# NatuurSpotter/main.py
# Hoofdingangspunt voor de NatuurSpotter applicatie
# Start de Flask webserver op alle netwerkinterfaces

from NatuurSpotter.app import app

if __name__ == "__main__":
    # Start de Flask applicatie op alle netwerkinterfaces
    # Handig voor gebruik in Docker of virtuele machines
    app.run(host="0.0.0.0", port=5000, debug=True)
