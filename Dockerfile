# Use official lightweight Python image
FROM python:3.11-slim

# Install dependencies (OpenCV + Chrome support)
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libgtk-3-0 \
    fonts-liberation \
    libgbm1 \
    libu2f-udev \
    libvulkan1 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb || apt-get -fy install && \
    rm google-chrome-stable_current_amd64.deb

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code
COPY . .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Expose FastAPI port
EXPOSE 8000

# Default entrypoint
ENTRYPOINT ["sh", "entrypoint.sh"]
