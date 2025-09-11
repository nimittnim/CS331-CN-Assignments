#!/bin/bash

# Start server in background
python3 server.py &
SERVER_PID=$!

# Run client in foreground (waits until done)
python3 client.py 

# Stop the server after client finishes
kill $SERVER_PID
