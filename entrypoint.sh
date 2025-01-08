#!/bin/bash

# Register the runner
./config.sh --url https://github.com/L1nwatch/auto_market --token "$RUNNER_TOKEN" --unattended --replace

# Run the runner
./run.sh