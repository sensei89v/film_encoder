#!/bin/bash

function killall()
{
    kill -9 $service_id
    kill SIGTERM $celery_id
}

trap killall SIGINT

celery  --app=app.celery.celery_app worker --loglevel=DEBUG &
celery_id=$!
python server.py &
service_id=$!

echo "$service_id  $celery_id"
wait $service_id $celery_id
echo "$service_id  $celery_id"

