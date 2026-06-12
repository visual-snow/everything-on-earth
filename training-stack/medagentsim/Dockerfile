FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git curl gcc g++ \
    libjpeg-dev zlib1g-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone MedAgentSim
RUN git clone --depth 1 https://github.com/MAXNORM8650/MedAgentSim.git .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy trauma scenarios
COPY scenarios/ /app/scenarios/

# Django runs on port 8000
EXPOSE 8000

# Start the Django server
CMD ["python", "-m", "medsim.server"]
