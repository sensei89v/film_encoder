#!/bin/bash

if [ "$#" -ge 1 ]; then
    config_file=$1
else
    config_file="config.yaml"
fi

function killall()
{
    kill -9 $service_id
    kill SIGTERM $celery_id
}

trap killall SIGINT

CONFIG_FILE=$1 celery --app=app.celery.celery_app worker --loglevel=DEBUG &
celery_id=$!
python server.py --config ${config_file} &
service_id=$!

echo "$service_id  $celery_id"
wait $service_id $celery_id
echo "$service_id  $celery_id"

