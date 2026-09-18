FROM python:3.10-slim

# Prevent Python from buffering logs
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# System dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ffmpeg \
       unzip \
       gcc \
       build-essential \
       curl \
       git \
       procps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Deno
ENV DENO_INSTALL=/usr/local/deno
RUN mkdir -p $DENO_INSTALL && \
    curl -fsSL https://deno.land/install.sh | sh
ENV PATH=$DENO_INSTALL/bin:$PATH

WORKDIR /app/

# Copy dependency file first for Docker layer caching
COPY requirements.txt /app/

# Upgrade pip & install deps
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . /app/

CMD python3 -m Fubuki
