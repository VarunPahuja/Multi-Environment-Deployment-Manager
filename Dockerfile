# Use python:3.10
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ /app/src/

# Expose port 8080
EXPOSE 8080

# Environment variable default, can be overridden by docker-compose
ENV APP_ENV=default

# Run Flask on port 8080
CMD ["python", "src/app.py"]
