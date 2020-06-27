#!/bin/bash

nohup python3 src/cqhttp.py > log/app.log 2>&1 &
