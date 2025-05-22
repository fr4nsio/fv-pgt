#!/bin/bash

set -euo pipefail

populate_with_errors='false'
if [ "${#}" -gt 0 ] && [ "${1}" = '--with-errors' ]; then
    populate_with_errors='true'
fi

echo "with errors: "${populate_with_errors}""
sleep 2

pushd frontend
npm run build
popd

(python app.py) &

echo "Will populate db in 3s"
sleep 3

pushd scripts

if [ "${populate_with_errors}" = 'true' ]; then
    python -m error_populate
else
    python -m populate

    # python -m list

    pushd 40_plant_module_system_sensor_reading
    python -m continuous_new_sensor_readings
    popd
fi


popd

while true; do
    sleep 1
done
