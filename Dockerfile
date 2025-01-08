FROM ubuntu:20.04

# Install required dependencies
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    git \
    sudo && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y libicu-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set up a directory for the runner
WORKDIR /runner

# Download and extract the GitHub Actions runner
RUN curl -o actions-runner.tar.gz -L https://github.com/actions/runner/releases/download/v2.321.0/actions-runner-linux-arm64-2.321.0.tar.gz && \
    tar xzf actions-runner.tar.gz && \
    rm actions-runner.tar.gz

# Copy entrypoint script
COPY entrypoint.sh /runner/entrypoint.sh
RUN chmod +x /runner/entrypoint.sh

# Create a non-root user and group
RUN groupadd --gid 1001 runner && \
    useradd --uid 1001 --gid runner --shell /bin/bash --create-home runner

# Change ownership of the /runner directory to the non-root user
RUN chown -R runner:runner /runner

# Switch to the non-root user
USER runner

# Set entrypoint
ENTRYPOINT ["/runner/entrypoint.sh"]
