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
    xvfb && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python and pip
RUN apt-get update && apt-get install -y python3 python3-pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set higher priority for the Chromium PPA
RUN sudo tee /etc/apt/preferences.d/chromium-ppa.pref <<EOF
Package: *
Pin: release o=LP-PPA-saiarcot895-chromium-beta
Pin-Priority: 1001
EOF

# Add the Chromium PPA repository
RUN echo "deb http://ppa.launchpadcontent.net/saiarcot895/chromium-beta/ubuntu jammy main" | sudo tee /etc/apt/sources.list.d/chromium-beta.list

# Add the Chromium PPA GPG key
RUN sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 4B2F369E32D934F066ACB0C3F6C3EADDA7D08424

# Update package lists
RUN sudo apt update

# Install Chromium browser
RUN sudo apt install -y chromium-browser

# Verify Chromium installation
RUN /usr/bin/chromium-browser --version

# Install ChromeDriver
RUN sudo apt install -y chromium-chromedriver

# Verify ChromeDriver installation
RUN /usr/lib/chromium-browser/chromedriver --version

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
    useradd --uid 1001 --gid 1001 --shell /bin/bash --create-home runner && \
    echo "runner ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set a password for the root user
RUN echo "root:rootpassword" | chpasswd

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
