# Flask App with MySQL Docker Setup

A small two-tier app: a Flask web app that stores messages in MySQL. Submit a message in the form; it is saved in the database and listed on the page.

Stack: Python 3.13, Flask 3.1, gunicorn, PyMySQL, MySQL 8.4.

| Route | What it does |
|---|---|
| `GET /` | Lists all messages and shows which server answered |
| `POST /submit` | Saves `new_message` (form field), returns it as JSON |
| `GET /health` | Returns `{"status":"ok"}` (no database call), used by health checks |

## Prerequisites

- Docker with the Compose plugin (`docker compose`)
- Git (optional, for cloning the repository)

## Run with Docker Compose

1. Clone and enter the repo:

   ```bash
   git clone https://github.com/LondheShubham153/two-tier-flask-app.git
   cd two-tier-flask-app
   ```

2. (Optional) set your own database credentials. Without a `.env` file the defaults in `docker-compose.yml` are used.

   ```bash
   cp .env.example .env   # then edit the passwords
   ```

3. Start everything:

   ```bash
   docker compose up --build
   ```

4. Open http://localhost:5000, send a few messages. The `messages` table is created automatically.

   > On macOS, port 5000 may already be used by *AirPlay Receiver*. Turn it off in System Settings, or change the left side of `"5000:5000"` in `docker-compose.yml`.

5. Stop and remove the containers (`-v` also deletes the database volume):

   ```bash
   docker compose down        # keep data
   docker compose down -v     # delete data too
   ```

`make build`, `make run`, `make stop`, `make test` and `make clean` are shortcuts for the common commands.

## Run without Docker Compose

1. Build the image and create a network:

   ```bash
   docker build -t flaskapp .
   docker network create twotier
   ```

2. Start MySQL:

   ```bash
   docker run -d \
       --name mysql \
       -v mysql-data:/var/lib/mysql \
       --network=twotier \
       -e MYSQL_DATABASE=mydb \
       -e MYSQL_ROOT_PASSWORD=admin \
       -p 3306:3306 \
       mysql:8.4
   ```

3. Start the app (wait a few seconds for MySQL to be ready first):

   ```bash
   docker run -d \
       --name flaskapp \
       --network=twotier \
       -e MYSQL_HOST=mysql \
       -e MYSQL_USER=root \
       -e MYSQL_PASSWORD=admin \
       -e MYSQL_DB=mydb \
       -p 5000:5000 \
       flaskapp:latest
   ```

## Configuration

The app reads its database settings from environment variables:

| Variable | Default |
|---|---|
| `MYSQL_HOST` | `localhost` |
| `MYSQL_PORT` | `3306` |
| `MYSQL_USER` | `default_user` |
| `MYSQL_PASSWORD` | `default_password` |
| `MYSQL_DB` | `default_db` |
| `FLASK_DEBUG` | off (`1` enables debug when running `python app.py`) |

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## What's in the repo

| Path | Purpose |
|---|---|
| `Dockerfile`, `Dockerfile-multistage` | Container images (the second shows the multi-stage pattern) |
| `docker-compose.yml`, `Makefile` | Local run |
| `Jenkinsfile` | CI/CD pipeline |
| `k8s/`, `eks-manifests/` | Kubernetes manifests (kubeadm cluster / Amazon EKS) |
| **`aws/`** | **Step-by-step guide to run this app on AWS: VPC, EC2, RDS, ALB, Auto Scaling, CloudWatch** |

## Notes

- This is a demo setup. For production use real secrets management, TLS and backups.
- If something fails, check `docker compose logs`.
