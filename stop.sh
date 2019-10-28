#!/bin/bash

p=`ps -ef | grep -E "cqhttp" | grep -v grep|awk '{print $2}'`
kill -9 $p