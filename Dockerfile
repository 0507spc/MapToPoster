# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Install build deps
RUN apt-get update -y \
 && apt-get install -y --no-install-recommends \
      git build-essential \
 && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -g 10000 python && useradd -u 10000 -g 10000 -m python

WORKDIR /home/python/app

# Clone maptoposter source
RUN git clone https://github.com/originalankur/maptoposter.git .

# Fix ownership
RUN chown -R python:python .

USER python

# Install deps
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Default command: keep container alive; you will exec create_map_poster manually or via entrypoint
CMD ["sleep", "infinity"]
