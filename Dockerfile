# Use the official Python 3.10 slim image as the base
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies required for CodeQL
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Download and install CodeQL
# TODO: This URL will need to be updated based on architecture and base image's OS
RUN curl -L -o codeql.zip https://github.com/github/codeql-cli-binaries/releases/latest/download/codeql-linux64.zip \
    && unzip codeql.zip -d /opt \
    && rm codeql.zip

# Add CodeQL to the PATH
ENV PATH="/opt/codeql/:${PATH}"

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required Python packages and dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

WORKDIR /app/graph/codeql/python
RUN codeql pack install

WORKDIR /app/graph/codeql/javascript
RUN codeql pack install

WORKDIR /app
# Set environment variables if needed
# ENV VARIABLE_NAME=value

# Run your scripts
CMD ["python", "main.py"]