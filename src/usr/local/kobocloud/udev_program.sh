#!/bin/sh

# udev kills slow scripts
if [ "$SETSID" != "1" ]
then
    SETSID=1 setsid "$0" "$@" &
    exit
fi

#load config
. $(dirname $0)/config.sh

#create work dirs
[ ! -e "$Logs" ] && mkdir -p "$Logs" >/dev/null 2>&1
[ ! -e "$Lib" ] && mkdir -p "$Lib" >/dev/null 2>&1
[ ! -e "$SD" ] && mkdir -p "$SD" >/dev/null 2>&1

# Make select.cgi executable on the Kobo
chmod +x "$KC_HOME/www/cgi-bin/select.cgi" >/dev/null 2>&1

# Start local web server for on-demand book selection instead of auto-syncing all files
if ! pgrep -f "httpd -p 127.0.0.1:8088" >/dev/null 2>&1; then
    busybox httpd -p 127.0.0.1:8088 -h "$KC_HOME/www" >> "$Logs/httpd.log" 2>&1
fi
