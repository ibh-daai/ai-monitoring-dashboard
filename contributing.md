# Contribution Guide for AI Monitoring Dashboard
Thank you for considering contributing to the AI Monitoring Dashboard! This guide will give you a quick overview of how you can help improve and maintain the system.

## Project Overview
Our dashboard monitors the performance of clinical AI models over time. It's built using Python, Pandas, React, MongoDB, Flask, and Docker, with data processing handled by Pandas and Evidently AI. The system is designed to be modular, allowing for easy adaptation to different healthcare AI models.

## How to Contribute
1. **Set Up**: 
   - Fork the repo
   - Clone your fork
   - Follow the setup instructions in the Technical Instructions document

2. **Find Something to Work On**:
   - Got an idea? Create a new issue to discuss it

3. **Make Changes**:
   - Create a new branch for your work
   - Code code code
   - Run tests (currently, tests are not implemented in the Docker env, only locally. Feel free to add tests!)
   - Don't forget to update documentation

4. **Submit Your Work**:
   - Push your changes to your fork
   - Create a Pull Request (PR) to the main repository
   - Describe your changes in the PR description

## Coding Standards
Just follow whats already in the codebase.
 
## File Hierarchy and Explanation
- `api/`: Contains the Flask APIs for the dashboard filtering and the data ingestion.
- `config/`: Contains the configuration file for the dashboard (and it's README.md), as well as the data schema.
- `data/`: Contains the data for the dashboard. Created in the Docker environment.
- `flow/`: Contains the main Prefect flow for the dashboard, as well as the `start.sh` script.
- `frontend/`: Contains the two React frontends for the project: the dashboard and the data ingestion.
- `scripts/`: Contains scripts that do not fit into the other directories.
- `snapshots/`: Contains the saved JSON metrics and test results for the dashboard. Created in the Docker environment as a Docker volume. Organized by date.
- `src/`: Contains the Python source code for the dashboard, including the data preprocessing, monitoring calculations, and the dashboard creation.
- `tests/`: Contains the pytests for the data preprocessing and monitoring pipelines. Currently not implemented in the Docker environment, only locally. Feel free to add tests!
- `workspace/`: Created as a Docker volume for the Docker environment. Created by Evidently AI to store the UI files for your project.

## Thanks
Thanks, you're awesome! 🎉