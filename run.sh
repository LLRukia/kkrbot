#!/bin/bash

rm app.log > /dev/null
touch app.log
nohup python3 src/cqhttp.py >> app.log 2>&1 &
tailf app.log
