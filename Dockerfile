# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container to /app
WORKDIR /app

# Add current directory code to /app in container
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ARG FINAZON_URL
ARG FINAZON_API_KEY
ARG TIMESERIES_INTERVAL
ARG DATA_SET
ARG SEND_TO_DISCORD="True"
ARG TICKER
ARG DISCORD_BOT_TOKEN
ARG DISCORD_CHANNEL_ID

# Run crypto_mfi_tracing.py when the container launches
CMD ["python", "crypto_mfi_tracing.py"]
