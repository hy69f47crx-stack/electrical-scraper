#!/bin/bash

echo "Agent started at $(date)" >> /Users/fahadalkandri/Desktop/electrical-scraper/log.txt

export PATH="/Library/Frameworks/Python.framework/Versions/3.14/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

cd /Users/fahadalkandri/Desktop/electrical-scraper

/Library/Frameworks/Python.framework/Versions/3.14/bin/python3 scraper.py >> log.txt 2>&1



