#!/bin/bash

# Loop 6 times
for i in {1..6}; do
    echo "Iteration $i of 6"

    # Run first command
    echo "Running Command 1..."
    # Replace the following line with your first actual command
    python run_message_exchange.py

    # Wait 1 minute
    echo "Waiting 10 seconds, sir..."
    sleep 10

    # Run second command
    echo "Running Command 2..."
    # Replace the following line with your second actual command
    python run_all_cycles.py

    if [ $i -lt 6 ]; then
        echo "Waiting 20 seconds, sir..."
        sleep 20
    else
        echo "All iterations completed, sir!"
    fi
done

python run_reflex.py
sleep 20
