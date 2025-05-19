# Use an official Python runtime as a parent image
FROM python:3.13.3-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Set the working directory
WORKDIR /app

# Copy the app code into the container
COPY . /app

RUN mkdir -p /app/tmp && chmod 777 /app/tmp

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create a volume for the SQLite database
#VOLUME /app/data

# Expose the port that Gunicorn will listen on
EXPOSE 5000

# Start the app with Gunicorn (production WSGI server)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:create_app('production')"]
