#!/usr/bin/env bash

fail=false

echo "Checking programs"
programs=(curl docker docker-compose)
counter=0
for program in "${programs[@]}"
do
    isThere=$(whereis "$program" | awk -F ':' '{print $2}' | tr -d ' ')
    if [ -z "$isThere" ]
    then
        fail=true

        echo "  [ ] $program: $program is not installed"
    else
        counter=$((counter+1))

        echo "  [x] $program: Found"
    fi
done
echo -e "Status: $counter/${#programs[*]}\n"

echo "Checking paths"
directories=(\/ \/var\/run \/sys \/var\/lib\/docker \/dev\/disk)
counter=0
for directory in "${directories[@]}"
do
    if [ ! -d "$directory" ]
    then
        echo "  [ ] \"$directory\": Cannot find \"$directory\""
    else
        counter=$((counter+1))

        echo "  [x] \"$directory\": Found"
    fi
done
echo -e "Status: $counter/${#directories[*]}\n"

if $fail
then
    echo "Found errors"
    exit 1
else
    echo "Everything is okay"
fi

