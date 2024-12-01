#!/bin/bash

# Allow prefect server to start
sleep 5

# define the workpool
prefect work-pool create --type process monitoring-pool

# Deploy monitoring flow
python /app/flow/deploy.py --concurrency-limit 5

# Start the agent
prefect worker start -p 'monitoring-pool'


