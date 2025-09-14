#!/bin/bash
NOTE_ID=$1

if [ -z "$NOTE_ID" ]; then
    echo "Usage: $0 <note_id>"
    exit 1
fi

LAST_STATUS=""

while true; do
    STATUS=$(sqlite3 ./fastapi_db.db "SELECT status FROM note WHERE id=$NOTE_ID;")
    if [ "$STATUS" != "$LAST_STATUS" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Note $NOTE_ID status changed to: $STATUS"
        LAST_STATUS="$STATUS"
    fi
done
