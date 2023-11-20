# Pull base pythin image

FROM python:3 

# set working directory in the container

WORKDIR /data

# install required packages for system

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy the required file into container

COPY requirements.txt .

RUN pip install mysqlclient

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]