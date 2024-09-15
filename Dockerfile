# Use Python 3.10 (required by Lean)
FROM python:3.10-slim

# Set environment variables to avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies including generic kernel headers (for evdev), git, curl, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    unzip \
    build-essential \
    linux-headers-generic \
    && rm -rf /var/lib/apt/lists/*


# Create a workspace directory and set it as the working directory
RUN mkdir /workspace
WORKDIR /workspace

# Set up entrypoint for interactive shell (optional)
CMD ["tail", "-f", "/dev/null"]
