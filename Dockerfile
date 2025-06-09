# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy only requirements first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the actual app code
COPY dash_app/ ./dash_app/
COPY sample_data/ ./sample_data/

# Set environment variables (optional but good)
ENV PYTHONUNBUFFERED=1

# Run the Dash app
CMD ["python", "dash_app/app.py"]
