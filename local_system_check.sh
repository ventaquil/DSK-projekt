#!/usr/bin/env bash

fail=false

echo "Checking programs"
programs=(curl jmeter pip3 python3 scp ssh zip)
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

if $fail
then
    echo "Found errors"
    exit 1
else
    echo "Everything is okay"
fi

