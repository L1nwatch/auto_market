FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install required dependencies
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    git \
    sudo && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y libicu-dev tzdata && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


# Set up a directory for the runner
WORKDIR /runner

# Download and extract the GitHub Actions runner
RUN curl -o actions-runner.tar.gz -L https://github.com/actions/runner/releases/download/v2.321.0/actions-runner-linux-arm64-2.321.0.tar.gz && \
    tar xzf actions-runner.tar.gz && \
    rm actions-runner.tar.gz

# Set the API key using a build argument
ARG OPENAI_API_KEY
ARG RUNNER_TOKEN
ENV OPENAI_API_KEY=$OPENAI_API_KEY
ENV RUNNER_TOKEN=$RUNNER_TOKEN

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
#CMD ["/bin/bash"]