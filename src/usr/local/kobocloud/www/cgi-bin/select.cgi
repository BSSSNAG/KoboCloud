#!/bin/sh

# Load KoboCloud config
. /usr/local/kobocloud/config.sh

echo "Content-type: text/html; charset=utf-8"
echo ""
echo "<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'>"
echo "<style>
  body { font-family: sans-serif; padding: 15px; background: #fff; color: #000; }
  .book { display: flex; justify-content: space-between; align-items: center; padding: 14px 0; border-bottom: 2px solid #000; font-size: 18px; }
  .btn { border: 2px solid #000; padding: 8px 16px; text-decoration: none; color: #000; font-weight: bold; background: #eee; }
  .status { padding: 12px; border: 2px solid #000; margin-bottom: 15px; font-weight: bold; }
</style></head><body>"
echo "<h2>KoboCloud: Select Ebook</h2>"

# Check if user tapped Download on a specific book (?id=...&name=...)
if [ -n "$QUERY_STRING" ]; then
    FILE_ID=$(echo "$QUERY_STRING" | sed -n 's/.*id=\([^&]*\).*/\1/p')
    RAW_NAME=$(echo "$QUERY_STRING" | sed -n 's/.*name=\([^&]*\).*/\1/p')
    FILE_NAME=$(busybox httpd -d "$RAW_NAME")

    if [ -n "$FILE_ID" ] && [ -n "$FILE_NAME" ]; then
        linkLine="https://drive.google.com/uc?id=${FILE_ID}&export=download"
        localFile="$Lib/$FILE_NAME"
        
        # Create subfolder if book is inside a subfolder
        mkdir -p "$(dirname "$localFile")" >/dev/null 2>&1
        
        # Download only this selected file
        /usr/local/kobocloud/getRemoteFile.sh "$linkLine" "$localFile"
        
        # Trigger Kobo library refresh
        if [ -e /usr/local/KoboCloud/NickelDBus.sh ]; then
            /usr/local/KoboCloud/NickelDBus.sh
        elif command -v qndb >/dev/null 2>&1; then
            qndb -m pfmRescanBooksFull >/dev/null 2>&1
        else
            mount -o remount,rw "$SD" >/dev/null 2>&1
            echo "label" > "$SD"
            echo add >> /tmp/nickel-hardware-status
        fi
        
        echo "<div class='status'>Downloaded: ${FILE_NAME}</div>"
    fi
fi

# Read Google Drive URLs from kobocloudrc and list files using getGDriveFiles.sh
if [ -f "$UserConfig" ]; then
    grep -v '^#' "$UserConfig" | grep "drive.google.com" | while read -r url; do
        /usr/local/kobocloud/getGDriveFiles.sh "$url" | while IFS='|' read -r fcode fname; do
            [ -z "$fcode" ] && continue
            if [ -f "$Lib/$fname" ]; then
                echo "<div class='book'><span>$fname</span><span>[On Device]</span></div>"
            else
                echo "<div class='book'><span>$fname</span><a class='btn' href='/cgi-bin/select.cgi?id=${fcode}&name=${fname}'>Download</a></div>"
            fi
        done
    done
else
    echo "<p>Config file not found at $UserConfig</p>"
fi

echo "</body></html>"
