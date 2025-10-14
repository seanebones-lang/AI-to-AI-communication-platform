#!/bin/bash

echo "Starting Enterprise AI Integration Platform..."

# Start supervisord to manage processes
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
