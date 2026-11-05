#!/bin/sh

baseURL="$1"

#load config
. $(dirname $0)/config.sh

find_files() #function to find all files in the folder 
{
$CURL -k -L --silent "https://drive.google.com/drive/folders/$1" |
grep -Eo "\\\x5b\\\x22[^\\\]*\\\x22,\\\x5b\\\x22$1\\\x22\\\x5d,\\\x22.{1,250}\\\x22,\\\x22[^\\\]*\\\/[^\\\]*" |
sed 's/\\\x/\\\\\x/g' |
while read entry
do
    entryType=`echo $entry | sed -n 's/.*\\\x22\(.*\)$/\1/p'` #Get the type. Needed to see if it's a file or a folder.
    entryCode=`echo $entry | sed -n 's/\\\x5b\\\x22\(.*\)\\\x22,\\\x5b\\\x22.*$/\1/p'` #Get the identifying code of the file/folder
    entryName=`echo $entry | sed -n 's|\\\x5b\\\x22.*,\\\x22\(.*\)\\\x22,\\\x22.*$|\1|p'`

    if [ "$entryType" = "application/vnd.google-apps.folder" ]; then #if it's a folder it runs this function for the folder
        find_files $entryCode "$entryName/"
    else
        echo "$2$entryName|$entryCode"
    fi
done
}

# Extract the folder code from the shared URL
gDirCode=`echo $baseURL | sed 's@.*/\([^/\?]*\).*@\1@'`

links=`find_files "$gDirCode"` # find links
echo "$links" |
sed 's/\\\x/\\\\\x/g' |
while read fileInfo
do
    [ -z "$fileInfo" ] && continue
    fileCode=`echo $fileInfo | sed -n 's/.*|\(.*\)/\1/p'` # extract the code for file download
    fileName=`echo $fileInfo | sed -n 's/\(.*\)|.*/\1/p'` # extract the file name
    outFileName=`/bin/echo -e "$fileName" | tr ' ' '_' `

    if [ -n "$fileCode" ] && [ -n "$outFileName" ]; then
        echo "$fileCode|$outFileName"
    fi
done
