# Use the official lightweight Python image
FROM python:3.11-slim

# Set environment variables (optional but helpful)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY . .

# Expose the Streamlit default port
EXPOSE 8501

# Run your Streamlit app
CMD ["streamlit", "run", "index.py", "--server.port=8501", "--server.enableCORS=false"]

