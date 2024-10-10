#!/bin/bash

zip -r src.zip . -x "*.zip" > /dev/null 2>&1
if [ -f src.zip ]; then
    echo "Compressed successfully"
else
    echo "Error: Compression failed"
    exit 1
fi