# Use the official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the contents of the app directory into the container at /app
COPY ./app .

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable to store where the log files will be stored
ENV LOG_DIR /app/logs

# Create a directory to store the log files
RUN mkdir -p ${LOG_DIR}

# Define environment variable
ENV PYTHONUNBUFFERED 1

# Run main.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
