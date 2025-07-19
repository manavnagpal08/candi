# Use a slim Python base image, matching Python 3.13 as seen in your error traceback
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Install system dependencies for WeasyPrint
# These include libraries for rendering text, graphics, and images
# Ensure these are compatible with the Debian/Ubuntu version that python:3.13-slim is based on.
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
