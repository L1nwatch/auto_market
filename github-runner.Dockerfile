FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install required dependencies
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    git \
    sudo \
    wget \
    unzip \
    libicu-dev \
    tzdata \
    sqlite3 \
    libsqlite3-dev \
    libnss3 \
    libgconf-2-4 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxtst6 \
    libxcomposite1 \
    libxrandr2 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgbm1 \
    chromium-browser \
    chromium-chromedriver \
    xvfb && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb || apt-get -fy install && \
    rm google-chrome-stable_current_amd64.deb

# Install Python and pip
RUN apt-get update && apt-get install -y python3 python3-pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python libraries for Selenium
RUN pip3 install --no-cache-dir selenium webdriver-manager pyvirtualdisplay

# Set up a directory for the runner
WORKDIR /runner

# Download and extract the GitHub Actions runner
RUN curl -o actions-runner.tar.gz -L https://github.com/actions/runner/releases/download/v2.321.0/actions-runner-linux-arm64-2.321.0.tar.gz && \
    tar xzf actions-runner.tar.gz && \
    rm actions-runner.tar.gz

# Set the API key using a build argument
ARG OPENAI_API_KEY
ARG RUNNER_TOKEN
ARG LOTTO_USER
ARG LOTTO_PASSWORD
ENV OPENAI_API_KEY=$OPENAI_API_KEY
ENV RUNNER_TOKEN=$RUNNER_TOKEN
ENV LOTTO_USER=$LOTTO_USER
ENV LOTTO_PASSWORD=$LOTTO_PASSWORD

# Copy entrypoint script
COPY entrypoint.sh /runner/entrypoint.sh
RUN chmod +x /runner/entrypoint.sh

# Create a non-root user and group
RUN groupadd --gid 1001 runner && \
    useradd --uid 1001 --gid runner --shell /bin/bash --create-home runner

# Change ownership of the /runner directory to the non-root user
RUN chown -R runner:runner /runner

# git config --global
RUN git config --global user.email "automated-market-github-runner@gmail.com"
RUN git config --global user.name "automated-market-github-runner"

# Set GitHub SSH token
RUN mkdir -p /runner/.ssh
COPY id_rsa /runner/.ssh/id_rsa
RUN chmod 600 /runner/.ssh/id_rsa
RUN ssh-keyscan github.com >> /runner/.ssh/known_hosts

# Switch to the non-root user
USER runner

# Set display for headless mode
ENV DISPLAY=:99

# Set entrypoint
ENTRYPOINT ["/runner/entrypoint.sh"]