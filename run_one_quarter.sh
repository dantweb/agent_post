#!/bin/bash

# Run run_6_days.sh 12 times
for j in {1..12}; do
    echo "Execution $j of 12 - Running run_6_days.sh..."

    # Execute the run_6_days.sh script
    ./run_6_days.sh

    if [ $j -lt 12 ]; then
        echo "Waiting 10 seconds before the next execution..."
        sleep 10
    else
        echo "All executions of run_6_days.sh completed!"
    fi
done