#!/bin/bash
set -e

# Start systemd as the init system
exec /lib/systemd/systemd


# Wait for systemd to start
sleep 5

# Start ssh service
systemctl start ssh

# Wait indefinitely to keep the container running
tail -f /dev/null
