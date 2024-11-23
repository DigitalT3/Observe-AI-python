# Use the official Python base image
FROM python:3.11.0-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt ./requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app to the container
COPY . .

# Expose the port Streamlit uses
EXPOSE 8501

# Set Streamlit to run with minimal configurations
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Command to run the Streamlit app
CMD ["streamlit", "run", "main.py"]
