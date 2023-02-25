# Use an official Python runtime as a parent image
FROM python:3.10-slim-bullseye

# Set the working directory to /app
WORKDIR /app

# Copy the parent directory's pyproject.toml to /app
COPY ../pyproject.toml .

# Set an environment variable for the bot API key
ENV BOT_API_KEY $BOT_API_KEY

# Install Poetry version 1.3.2
RUN pip install "poetry==1.3.2"

# Install dependencies
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Create a logs directory and make it writable by everyone
RUN mkdir /app/logs && chmod 777 /app/logs

# Copy the rest of the app files to /app
COPY ../app .

# Run app.py when the container launches
CMD ["python", "main.py"]
