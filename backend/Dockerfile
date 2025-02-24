# Use the official Python 3.11 image
FROM python:3.11

# Install system dependencies
RUN apt-get update && apt-get install -y cmake libboost-all-dev

# Set the working directory in the container
WORKDIR /app

# Copy all files from backend folder to container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for FastAPI
EXPOSE 8000

# Start FastAPI server using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
