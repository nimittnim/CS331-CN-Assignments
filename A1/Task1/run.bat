@echo off
echo Starting the server and client...

REM The "start" command runs the following command in a new window.
start "Python Server" python server.py
start "Python Client" python client.py