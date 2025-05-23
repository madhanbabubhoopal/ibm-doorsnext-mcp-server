# 1. Start from an official Python base image
FROM python:3.9-slim

# 2. Set a working directory inside the container
WORKDIR /opt/dng_mcp_server

# 3. Copy the requirements.txt file into the working directory
COPY requirements.txt .

# 4. Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the application code
COPY app ./app
# main.py is inside app directory, so copying app directory is enough.

# 6. Expose the port the application runs on
EXPOSE 5000

# 7. Provide placeholder ENV instructions for required runtime environment variables
ENV DNG_BASE_URL="YOUR_DNG_BASE_URL_HERE"
ENV DNG_USERNAME="YOUR_DNG_USERNAME_HERE"
ENV DNG_API_KEY="YOUR_DNG_API_KEY_HERE"

# 8. Set the default command to run the Flask application
CMD ["python", "app/main.py"]
