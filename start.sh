#!/bin/bash

# Allow prefect server to start
sleep 5

# Deploy monitoring flow
prefect deployment build src/monitoring/monitoring_flow.py:monitoring_flow \
                      -n monitoring-flow \
                      -q monitoring-queue \
                      -o prefect.yaml \
                      --skip-upload \
                      --apply

# # Deploy data ingestion flow
# prefect deployment build ingestion_flow.py:data_ingestion_flow \
#                       -n data-ingestion-flow \
#                       -q ingestion-queue \
#                       -o prefect.yaml \
#                       --skip-upload \
#                       --apply

# # Start the agent
# prefect agent start -q 'monitoring-queue,ingestion-queue' --limit 5

# Start the agent
prefect agent start -q 'monitoring-queue' --limit 5