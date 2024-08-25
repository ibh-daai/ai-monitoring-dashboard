#!/bin/bash

# Allow prefect server to start
sleep 5

# Deploy monitoring flow
prefect deployment build flow/main.py:monitoring_flow \
                      -n monitoring-flow \
                      -q monitoring-pool \
                      -o prefect.yaml \
                      --skip-upload \
                      --apply

# Start the agent
prefect agent start -q 'monitoring-pool' --limit 1


