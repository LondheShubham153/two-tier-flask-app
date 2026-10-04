# Run the two-tier Flask app on AWS

You will take the small Flask + MySQL app from this repo and run it the way real teams do on AWS: in your own network, behind a load balancer, on servers that scale up and heal themselves, talking to a managed database.

**Time:** about 3 hours · **Mostly:** AWS Console · **Region used in examples:** `ap-south-1` (Mumbai). Pick one region and stay in it.

## What you will build

```
                    Internet
                       │  :80
                ┌──────▼───────┐
                │     ALB      │   alb-sg: 80 from anywhere
                └──┬────────┬──┘
     public subnet A│        │public subnet B        (two Availability Zones)
        ┌───────────▼─┐  ┌───▼─────────┐
        │ EC2 (Docker)│  │ EC2 (Docker)│   web-sg: 5000 only from alb-sg
        │  Flask app  │  │  Flask app  │   ← Auto Scaling group (1–4 instances)
        └──────┬──────┘  └──────┬──────┘
               └────────┬───────┘  :3306
     private subnet A   │   private subnet B
                ┌───────▼──────┐
                │ RDS MySQL 8.4│   db-sg: 3306 only from web-sg
                └──────────────┘
```

| # | You learn | Service |
|---|---|---|
| 1 | Your own private network | **VPC**, subnets, route tables, internet gateway |
| 2 | Who may talk to whom | **Security groups** |
| 3 | A managed database | **RDS for MySQL** |
| 4 | A server that configures itself | **EC2**, **user data**, **IAM role** |
| 5 | One front door, many servers | **Application Load Balancer** |
| 6 | Servers that scale and self-heal | **Launch template**, **Auto Scaling** |
| 7 | Seeing what is happening | **CloudWatch** |
| 8 | Where to go next | **ECR**, **ECS / EKS** |

## Before you start

- An AWS account you can use freely. New accounts (created after 15 July 2025) get a credit-based Free Tier, so read [Free Tier plans](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html) first. **RDS, the load balancer and any NAT gateway cost money while they exist.** Do the [Clean up](#9-clean-up-do-not-skip) step when you finish.
- Do not work as the root user. Sign in as an IAM / Identity Center user with admin rights in a sandbox account.
- Create a **budget alert**: Billing → Budgets → *Zero spend budget* (or a monthly $10 budget).
- Run the app locally first so you know what "working" looks like. From the repo root: `docker compose up --build`, then open <http://localhost:5000> (on macOS port 5000 is sometimes taken by AirPlay Receiver; turn that off or change the port mapping).

The app has two routes you will use all session: `/` (shows messages, plus the **name of the server that answered**) and `/health` (returns `{"status":"ok"}`, used by the load balancer).

Naming used below: prefix everything with `twotier-` so it is easy to find and delete.

---

## 1. VPC: your private network  (~25 min)

A **VPC** is a private network inside AWS. **Subnets** slice it up, one per Availability Zone (AZ) at a time. A subnet is *public* if its route table sends internet traffic to an **internet gateway**; otherwise it is *private*.

**Console → VPC → Create VPC → "VPC and more"**

| Setting | Value |
|---|---|
| Name tag auto-generation | `twotier` |
| IPv4 CIDR | `10.0.0.0/16` |
| Number of AZs | **2** |
| Public subnets | **2** |
| Private subnets | **2** |
| NAT gateways | **None** (saves money; see the note below) |
| VPC endpoints | None |
| DNS options | enable DNS hostnames and DNS resolution |

Create it, then open the **Resource map** and look at what the wizard made for you.

**You should see:** `twotier-vpc`, 2 public + 2 private subnets in different AZs, 2 route tables, 1 internet gateway. Click the public route table: it has a route `0.0.0.0/0 → igw-…`. Click the private one: it has no such route. That single route is the difference between public and private.

> **Why no NAT gateway?** A NAT gateway lets private instances reach the internet outbound. We keep the web servers in public subnets (locked down by security groups) so we don't pay for NAT. The database never needs the internet.

---

## 2. Security groups: who may talk to whom  (~15 min)

A **security group** is a stateful firewall attached to a resource. By default it blocks all inbound traffic. Instead of IP addresses we will let one security group refer to another, which keeps working as instances come and go.

**Console → VPC → Security groups → Create security group** (choose `twotier-vpc` each time)

| Name | Inbound rule |
|---|---|
| `twotier-alb-sg` | HTTP, port 80, source **Anywhere-IPv4** |
| `twotier-web-sg` | Custom TCP, port **5000**, source **`twotier-alb-sg`** |
| `twotier-db-sg` | MySQL/Aurora, port **3306**, source **`twotier-web-sg`** |

Leave the default outbound rule (all traffic) on each.

**You should see:** each group listing the *other group's ID* as its source, not an IP range. The internet can reach the load balancer only; the load balancer can reach the web servers only; the web servers can reach the database only.

---

## 3. RDS: a managed MySQL database  (~30 min)

**RDS** runs MySQL for you: backups, patching and (optionally) a standby in another AZ. You still choose the engine, size and network.

First, tell RDS which subnets it may use: **RDS → Subnet groups → Create DB subnet group**
- Name: `twotier-db-subnets`, VPC: `twotier-vpc`
- AZs: both. Subnets: the **two private** ones.

Then **RDS → Databases → Create database**

| Setting | Value |
|---|---|
| Creation method | Standard create |
| Engine | **MySQL**, version **8.4.x** |
| Template | **Sandbox** or **Free tier** if offered (otherwise Dev/Test) |
| DB instance identifier | `twotier-db` |
| Master username | `admin` |
| Credentials | *Self managed*, choose a password and write it down |
| Instance class | `db.t4g.micro` (burstable) |
| Storage | gp3, 20 GiB, turn off storage autoscaling |
| Connectivity | VPC `twotier-vpc`, subnet group `twotier-db-subnets`, **Public access: No**, security group **`twotier-db-sg`** only (remove `default`) |
| Additional configuration → Initial database name | **`devops`** |
| Backups | 1 day retention is fine for a lab; turn off Enable deletion protection |

Create it. It takes 5–10 minutes. While you wait, move on to reading step 4.

When it is *Available*, open it and copy the **Endpoint** (like `twotier-db.xxxx.ap-south-1.rds.amazonaws.com`).

**You should see:** the database is not reachable from your laptop (Public access: No). That is on purpose.

> You do not create the `messages` table. The app creates it on first use.

---

## 4. EC2, user data and an IAM role: one server  (~35 min)

Get **one** server working by hand before you automate many.

### 4a. Create the IAM role

The server needs permission to send logs to CloudWatch, and you want to open a shell without SSH keys. Follow [`iam/ec2-role-notes.md`](iam/ec2-role-notes.md) to create the role **`twotier-web-role`**. Takes about 5 minutes.

### 4b. Prepare the user data script

**User data** is a script EC2 runs once, as root, the first time an instance boots. Open [`user-data/web.sh`](user-data/web.sh) and read it. It does two things: installs Docker, then starts the app container with your database settings as environment variables. Edit the values at the top: `DB_HOST` (your RDS endpoint), `DB_PASSWORD`, and `AWS_REGION`.

### 4c. Launch the instance

**EC2 → Instances → Launch instances**

| Setting | Value |
|---|---|
| Name | `twotier-web-test` |
| AMI | **Ubuntu Server 24.04 LTS** (Quick Start, 64-bit x86) |
| Instance type | `t3.micro` |
| Key pair | **Proceed without a key pair** (we use Session Manager) |
| Network | VPC `twotier-vpc`, a **public** subnet, **Auto-assign public IP: Enable** |
| Security group | existing: `twotier-web-sg` |
| Advanced → IAM instance profile | `twotier-web-role` |
| Advanced → User data | paste your edited `web.sh` |

Launch. Wait for **Status checks: 2/2 passed**.

### 4d. Look inside

**EC2 → select the instance → Connect → Session Manager → Connect.** (It can take a minute or two for the instance to appear after boot.)

```bash
sudo tail -n 30 /var/log/user-data.log   # did the script finish?
sudo docker ps                           # is flask-app running?
curl -s localhost:5000/health            # {"status":"ok"}
```

**You should see:** the container `flask-app` running and `{"status":"ok"}`.

The web security group only allows the load balancer, so you cannot open the instance's public IP in a browser yet. That is correct. If you want a quick check, temporarily add an inbound rule for port 5000 from **My IP** to `twotier-web-sg`, open `http://<public-ip>:5000`, post a message, then **delete that rule again**.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| Instance not in Session Manager | Role not attached, or no public IP / no route to the internet |
| `docker: command not found` | User data failed: read `/var/log/user-data.log` |
| App page shows *Internal Server Error* | Wrong DB endpoint or password, or `twotier-db-sg` doesn't allow `twotier-web-sg`. `sudo docker logs flask-app` shows the real error |
| `Can't connect to MySQL server` | Security group chain from step 2 is wrong |

---

## 5. Application Load Balancer: one front door  (~20 min)

**EC2 → Target groups → Create target group**
- Type: **Instances**, name `twotier-tg`, protocol HTTP, port **5000**, VPC `twotier-vpc`
- Health checks: path **`/health`**
- Skip registering targets for now (the Auto Scaling group will do it).

**EC2 → Load balancers → Create → Application Load Balancer**
- Name `twotier-alb`, **Internet-facing**, IPv4
- VPC `twotier-vpc`, mappings: **both public subnets**
- Security group: `twotier-alb-sg` only
- Listener: HTTP :80 → forward to `twotier-tg`

Now register your test server to see it work: open `twotier-tg` → **Register targets** → tick `twotier-web-test` → *Include as pending* → *Register*. Wait for health to turn **Healthy**, then open the ALB's **DNS name** in your browser.

**You should see:** the app, with "Served by ip-10-0-…" at the bottom. Post a message; it is now stored in RDS.

Then deregister the test server; the Auto Scaling group takes over next.

---

## 6. Launch template and Auto Scaling: many servers  (~25 min)

A **launch template** is a saved "launch instance" form. An **Auto Scaling group (ASG)** uses it to keep the right number of instances running and replaces any that fail.

**EC2 → Launch templates → Create launch template**
- Name `twotier-lt`, AMI **Ubuntu Server 24.04 LTS**, type `t3.micro`, no key pair
- Security group `twotier-web-sg` (don't set a subnet here; the ASG chooses)
- Advanced: IAM instance profile `twotier-web-role`, user data = your edited `web.sh`

**EC2 → Auto Scaling groups → Create**
- Name `twotier-asg`, template `twotier-lt`
- VPC `twotier-vpc`, subnets: **both public**
- Load balancing: **Attach to an existing load balancer** → target group `twotier-tg`
- Health checks: turn on **Elastic Load Balancing health checks**, grace period 120 s
- Group size: desired **2**, min **1**, max **4**
- Scaling policy: **Target tracking**, metric *Average CPU utilization*, target **50**

**You should see:** two new instances launching, one in each AZ. After a few minutes both are *Healthy* in the target group. **Refresh the ALB URL repeatedly**: the "Served by" name changes between servers.

### Try to break it

1. **Self-healing.** Terminate one instance (EC2 → Instances → Instance state → Terminate). The ASG notices and launches a replacement. The site stays up on the other server.
2. **Scale out.** Open Session Manager on one instance and burn CPU for a few minutes:
   ```bash
   sudo apt-get install -y stress-ng && stress-ng --cpu 2 --timeout 600s
   ```
   Watch **Auto Scaling group → Activity** and **Monitoring**. When average CPU passes 50% it adds instances (this can take 3–5 minutes). Stop the stress test and it scales back in.

---

## 7. CloudWatch: see what is happening  (~10 min)

- **Metrics:** EC2 → select an instance → *Monitoring* tab (CPU, network). Compare with **ALB → Monitoring** (request count, target response time) and **RDS → Monitoring** (connections, CPU).
- **Logs:** CloudWatch → Log groups → **`/two-tier-flask-app`**. Each instance has its own log stream with the container's output. This works because the user data told Docker to use the `awslogs` driver and the IAM role allowed `logs:PutLogEvents`.
- **Alarm:** CloudWatch → Alarms → Create alarm → metric *ApplicationELB → HTTPCode_Target_5XX_Count* (or ASG CPU). Add an SNS email notification and give it a threshold you can trigger, e.g. stop the RDS instance, refresh the page and watch the 5xx alarm fire.

---

## 8. Where next: ECR, ECS and EKS  (~10 min, demo or read-through)

You ran the container by hand on EC2. AWS has services that run containers *for* you:

- **ECR** is a private image registry (like Docker Hub). Commands to push your own image are in [`cli-cheatsheet.md`](cli-cheatsheet.md).
- **ECS (Fargate)** runs a container from a *task definition* without you managing any server. Same idea as your launch template, but for containers.
- **EKS** is managed Kubernetes. This repo already has manifests: see [`../k8s/`](../k8s/) and [`../eks-manifests/`](../eks-manifests/).

Going further on your own:
- **Secrets Manager / SSM Parameter Store:** `web.sh` puts the DB password in plain text in user data. That is fine for a lab and wrong for production. Store the password in Secrets Manager, give the role `secretsmanager:GetSecretValue`, and fetch it in the script.
- **Private subnets + NAT gateway** for the web tier, **HTTPS** with ACM and a Route 53 domain, **Multi-AZ** RDS.

---

## 9. Clean up (do not skip)

Delete in this order, because each item depends on the next:

1. **Auto Scaling group** `twotier-asg` (this terminates its instances), then the launch template
2. Any leftover EC2 instance `twotier-web-test`
3. **Load balancer** `twotier-alb`, then the target group `twotier-tg`
4. **RDS** `twotier-db` (skip the final snapshot; wait until it is gone), then the DB subnet group
5. **CloudWatch** log group `/two-tier-flask-app` and any alarm
6. **VPC** `twotier-vpc`. Deleting it removes its subnets, route tables and internet gateway. Delete the three `twotier-*-sg` security groups first if it complains.
7. IAM role `twotier-web-role` and policy `twotier-cloudwatch-logs`

Tomorrow, check **Billing → Cost Explorer** to confirm nothing is still running.
