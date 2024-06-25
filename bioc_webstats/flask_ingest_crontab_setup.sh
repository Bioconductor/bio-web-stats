#!/bin/bash

# TODO correct directory?

# Define the script path
SCRIPT_PATH="flask_ingest.sh"

# Ensure the script is executable
chmod +x $SCRIPT_PATH

# Add a new cron job
(crontab -l 2>/dev/null; echo "12 1 * * * $SCRIPT_PATH") | crontab -
