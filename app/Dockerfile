# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /code

# Copy the requirements file and install dependencies first for layer caching
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the rest of the application code
COPY . /code/

# Command to run the application using uvicorn
# Expose port 80 and run on 0.0.0.0 to be accessible from outside the container
CMD ["uvicorn", "iris_fastapi:app", "--host", "0.0.0.0", "--port", "80"]
