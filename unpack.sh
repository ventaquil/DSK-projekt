#!/usr/bin/env bash

TD=$(mktemp -d)

if [ -f "./.package.zip" ]
then
    unzip -qq ./.package.zip -d $TD

    cd $TD

    mv .env.example .env

    echo $TD
else
    echo "\`.package.zip\` not found"

    exit 1
fi

