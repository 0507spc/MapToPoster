FROM python:3.12-slim

# System deps
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    git build-essential \
 && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN groupadd -g 10000 python && useradd -u 10000 -g 10000 -m python

WORKDIR /home/python/app

# Clone MapToPoster repo
RUN git clone https://github.com/originalankur/maptoposter.git /home/python/app/maptoposter

# Copy API wrapper files
COPY --chown=python:python main.py requirements.txt uvicorn_start.sh ./

RUN chmod +x uvicorn_start.sh

USER python

# Install python deps: first MapToPoster requirements, then API deps[web:24][web:14][web:31]
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r /home/python/app/maptoposter/requirements.txt \
 && pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["./uvicorn_start.sh"]
