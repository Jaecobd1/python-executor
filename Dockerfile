FROM python:3.12-slim

# Install build dependencies and clean up in the same layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    flex \
    bison \
    clang \
    linux-libc-dev \
    ca-certificates \
    pkg-config \
    protobuf-compiler \
    libprotobuf-dev \
    libnl-3-dev \
    libnl-route-3-dev \
    && rm -rf /var/lib/apt/lists/* \
    # Build and install nsjail
    && git clone https://github.com/google/nsjail \
    && cd nsjail \
    && make \
    && chmod +x nsjail \
    && mv nsjail /usr/local/bin/ \
    && cd .. \
    && rm -rf nsjail \
    # Create sandbox directory
    && mkdir /sandbox

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN ln -s /usr/local/bin/python /usr/bin/python3

# Copy app code and config
COPY app /app
COPY nsjail.json /app/nsjail.json
WORKDIR /app

EXPOSE 8080
CMD ["python", "main.py"]
