#!/bin/bash

# Register the runner
./config.sh --url "git@github.com:L1nwatch/auto_market.git" --token "$RUNNER_TOKEN" --unattended --replace

# Run the runner
./run.sh