
FROM python:3.12-slim-bookworm

WORKDIR /app

# Python runtime settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_DEBUG=0

# Install system packages required by pyodbc
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        gnupg \
        gcc \
        g++ \
        unixodbc \
        unixodbc-dev && \
    rm -rf /var/lib/apt/lists/*

# Register Microsoft package repository for Debian 12
RUN curl -fsSLo /tmp/packages-microsoft-prod.deb \
        https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb && \
    dpkg -i /tmp/packages-microsoft-prod.deb && \
    rm /tmp/packages-microsoft-prod.deb

# Install Microsoft ODBC Driver 18 for SQL Server
RUN apt-get update && \
    ACCEPT_EULA=Y apt-get install -y \
        --no-install-recommends msodbcsql18 && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Run application as non-root user
RUN useradd --create-home appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

# Start Flask through Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--access-logfile", "-", "run:app"]
