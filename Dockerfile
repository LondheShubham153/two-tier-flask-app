#----------------------------stage 1 started -----------------------------------------
# Use an official Python runtime as the base image
FROM python:3.9-slim AS Backend_flask

# Set the working directory in the container
WORKDIR /app

# install required packages for system
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install app dependencies
RUN pip install mysqlclient
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

#------------------------stage 2 started ------------------
#Used compressed version of stage 1
FROM python:3.9-slim

#Set working directory for stage 2
WORKDIR /app

#Copy libraries
COPY --from=Backend_flask /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.11/site-packages/

#Copy Src code from stage 1
COPY --from=Backend_flask /app /app

# Specify the command to run your application
CMD ["python", "app.py"]

