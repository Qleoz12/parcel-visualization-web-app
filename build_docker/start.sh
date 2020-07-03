#!/bin/sh

# backend
cd /usr/src/app/backend && python setup.py install && python application/main.py &
#cd /usr/src/app/backend/application && uvicorn main:app &

# frontend
nginx &


while true
do
  sleep 15
done


