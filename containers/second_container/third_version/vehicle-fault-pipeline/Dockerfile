# 1. Use an official, lightweight Python engine base
FROM python:3.11-slim

# 2. Establish our working workshop chamber inside the container
WORKDIR /app

# 3. Copy our tool list inventory into the container first
COPY requirements.txt .

# 4. Install the required tools inside the container chamber
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy our core machinery application payload into the container
COPY app.py .

# 6. Expose the port that our Flask web portal runs on
EXPOSE 5000

# 7. The ignition command to turn the key and start the app
CMD ["python", "app.py"]
