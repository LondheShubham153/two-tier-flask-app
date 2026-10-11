# Run the two-tier Flask app on Elastic Beanstalk

Elastic Beanstalk is a powerful PaaS: you hand it your application and it creates and manages the instances, load balancer and health monitoring around it. This guide runs the Flask + MySQL app from this repo on Beanstalk in two ways.

| Mode | What you upload | Database |
|---|---|---|
| Standard Mode | one file, `beanstalk/docker-compose.yml` | MySQL container next to the app, on the same instance |
| Cluster Mode | nothing, you point it at the Docker Hub image | Amazon RDS for MySQL |

Both modes use the public image `trainwithshubham/two-tier-flask-app` on Docker Hub, built for linux/amd64 and linux/arm64. The app listens on port 5000 and reads its database settings from environment variables.

| Variable | Meaning |
|---|---|
| `MYSQL_HOST` | database host name |
| `MYSQL_PORT` | database port, 3306 for MySQL |
| `MYSQL_USER` | database user |
| `MYSQL_PASSWORD` | password for that user |
| `MYSQL_DB` | database name |

The app creates its `messages` table the first time a page is requested, so there is no SQL to run. `GET /health` returns `{"status":"ok"}` without touching the database, which makes it a good health check path.

## Standard Mode with the compose file

You upload only `docker-compose.yml`. There is no ZIP, no Dockerfile and no SQL file, because Beanstalk pulls both images from Docker Hub.

The file starts two containers, `flask-app` and `mysql` (MySQL 8.4). Flask waits until MySQL reports healthy, then starts. The port mapping `80:5000` publishes the app on port 80 of the instance, which is the port Beanstalk's Docker platform sends traffic to.

1. Download `beanstalk/docker-compose.yml` from this repo. Open it and change `change-me-root-password` and `change-me-app-password` to your own values. The app password appears twice, once for each container, and both must match.
2. In the Elastic Beanstalk console choose Create application, then create a Web server environment.
3. Pick the Docker platform (the Amazon Linux 2023 branch) and leave the platform version on the recommended one.
4. Under Application code choose Upload your code, select Local file and upload `docker-compose.yml` on its own.
5. Choose Single instance as the preset for the first run. It is cheaper and it keeps the database container and the app on one machine.
6. Finish the wizard with an instance profile and service role (the console can create these for you) and create the environment.
7. When the environment turns green, open its URL. Post a few messages and reload the page to see them listed.

To check things, open the environment's Logs page and request the last lines, or use Session Manager on the instance and run `docker ps`.

### Things to know about this variant

- The MySQL data lives on the instance's disk, in a Docker volume. If Beanstalk replaces the instance, for example after a failed health check, a platform update or a rebuild, the data is gone.
- Keep the instance count at 1, for both min and max. Two instances would each get their own private MySQL container, so a message saved through one instance would not show up on the other.
- This variant suits demos and learning. For anything real, use the Cluster Mode setup below with RDS.
- The passwords sit in the file in plain text. That is fine for a throwaway demo. Do not reuse real passwords there.
- Update the image tag in `docker-compose.yml` when you want a newer version of the app, then upload the file as a new application version.

## Cluster Mode with the Docker Hub image and RDS

Cluster Mode runs one prebuilt image and cannot use a compose file, so MySQL has to live somewhere else. RDS fits well: it keeps the data when instances come and go, and many app instances can share it.

### 1. Create the database

1. In RDS create a MySQL 8.4 database in the same VPC you will use for Beanstalk. A `db.t4g.micro` instance is enough for a lab.
2. Set an initial database name of `devops`, and choose a master username and password you will remember.
3. Leave Public access off.
4. Put the database in a security group of its own, for example `eb-db-sg`.
5. Wait until the status is Available and copy the endpoint, for example `mydb.abc123.ap-south-1.rds.amazonaws.com`.

### 2. Allow the environment to reach the database

The RDS security group must accept traffic from the Beanstalk environment on port 3306. Edit `eb-db-sg` and add an inbound rule of type MySQL/Aurora, port 3306, with the source set to the security group your Beanstalk instances use. Referring to that security group works better than listing IP addresses because instances change over time. Create the environment first if you need to find that security group, then come back to add the rule.

### 3. Create the environment

1. Create a Web server environment on the Docker platform in Cluster Mode and choose to run a prebuilt image.
2. Use the image `trainwithshubham/two-tier-flask-app:1.0.0`.
3. Set the service port to 5000, the port the app listens on in the container.
4. Set the health check path to `/health` if the setup asks for one.
5. Use the same VPC as the database and place the instances in subnets that can reach it.
6. Add these environment properties, using your own endpoint and password:

| Name | Value |
|---|---|
| `MYSQL_HOST` | your RDS endpoint |
| `MYSQL_PORT` | `3306` |
| `MYSQL_USER` | your RDS master username, for example `admin` |
| `MYSQL_PASSWORD` | your RDS password |
| `MYSQL_DB` | `devops` |

7. Create the environment and wait for it to turn green.
8. Open the environment URL, post a message and reload. Refresh several times: with more than one instance, the "Served by" line at the bottom changes while the messages stay the same, because they come from RDS.

### If the page shows Internal Server Error

Open the environment logs. A message such as `Can't connect to MySQL server` points to the security group rule from step 2 or to a wrong endpoint. An access denied message points to the user, password or database name.

## Clean up

Terminate the Beanstalk environment, then delete the RDS instance (skip the final snapshot for a lab) and any security groups you created. RDS and load balancers cost money for as long as they exist.
