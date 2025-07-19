# Use a more stable Python base image (e.g., 3.10-slim) for better compatibility with WeasyPrint's dependencies.
# Python 3.13 is a very new release and might have compatibility issues with some C-extension libraries.
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Install system dependencies for WeasyPrint
# These include libraries for rendering text, graphics, and images.
# libpangocairo-1.0-0 is explicitly added for robustness.
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libpangocairo-1.0-0 \
    shared-mime-info \
    python3-dev \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Create a virtual environment and activate it
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port Streamlit runs on (default is 8501)
EXPOSE 8501

# Command to run your Streamlit application
CMD ["streamlit", "run", "app.py"]
