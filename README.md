 
# Flask App with MySQL Docker Setup

This is a simple Flask app that interacts with a MySQL database. The app allows users to submit messages, which are then stored in the database and displayed on the frontend.

## Prerequisites

Before you begin, make sure you have the following installed:

- Docker
- Git (optional, for cloning the repository)

## Setup

1. Clone this repository (if you haven't already):

   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   ```

2. Navigate to the project directory:

   ```bash
   cd your-repo-name
   ```

3. Create a `.env` file in the project directory to store your MySQL environment variables:

   ```bash
   touch .env
   ```

4. Open the `.env` file and add your MySQL configuration:

   ```
   MYSQL_HOST=mysql
   MYSQL_USER=your_username
   MYSQL_PASSWORD=your_password
   MYSQL_DB=your_database
   ```

## Usage

1. Start the containers using Docker Compose:

   ```bash
   docker-compose up --build
   ```

2. Access the Flask app in your web browser:

   - Frontend: http://localhost
   - Backend: http://localhost:5000

3. Create the `messages` table in your MySQL database:

   - Use a MySQL client or tool (e.g., phpMyAdmin) to execute the following SQL commands:
   
     ```sql
     CREATE TABLE messages (
         id INT AUTO_INCREMENT PRIMARY KEY,
         message TEXT
     );
     ```

4. Interact with the app:

   - Visit http://localhost to see the frontend. You can submit new messages using the form.
   - Visit http://localhost:5000/insert_sql to insert a message directly into the `messages` table via an SQL query.

## Cleaning Up

To stop and remove the Docker containers, press `Ctrl+C` in the terminal where the containers are running, or use the following command:

```bash
docker-compose down
```

## To run this two-tier application using  without docker-compose

- First create a docker image from Dockerfile
```bash
docker build -t flaskapp .
```

- Now, make sure that you have created a network using following command
```bash
docker network create twotier
```

- Attach both the containers in the same network, so that they can communicate with each other

i) MySQL container 
```bash
docker run -d --name mysql -v mysql-data:/var/lib/mysql -v ./message.sql:/docker-entrypoint-initdb.d/message.sql --network=twotier -e MYSQL_DATABASE=mydb -e MYSQL_USER=root -e MYSQL_ROOT_PASSWORD="admin" -p 3360:3360 mysql:5.7
```
ii) Backend container
```bash
docker run -d --name flaskapp -v mysql-data:/var/lib/mysql -v ./message.sql:/docker-entrypoint-initdb.d/message.sql --network=twotier -e MYSQL_HOST=mysql -e MYSQL_USER=root -e MYSQL_PASSWORD=admin -e MYSQL_DB=mydb -p 5000:5000 flaskapp:latest
```

## Notes

- Make sure to replace placeholders (e.g., `your_username`, `your_password`, `your_database`) with your actual MySQL configuration.

- This is a basic setup for demonstration purposes. In a production environment, you should follow best practices for security and performance.

- Be cautious when executing SQL queries directly. Validate and sanitize user inputs to prevent vulnerabilities like SQL injection.

- If you encounter issues, check Docker logs and error messages for troubleshooting.



## To run this two-tier application in EKS Cluster 

- Create namespace "two-tier-ns" before applying manifests.

#### Pre-requisites: 
  - an EC2 Instance (Note : If Using Ubuntu EC2 Instance instead of Amazon Linux then Make Sure to have **aws-iam-authenticator** installed.)


#### Article to Install aws-iam-authenticator :
```sh
https://docs.aws.amazon.com/eks/latest/userguide/install-aws-iam-authenticator.html
```

#### AWS EKS Setup 

### IAM Setup

1. **Create an IAM User:**
   - Go to the AWS IAM console.
   - Create a new IAM user named "eks-admin."
   - Attach the "AdministratorAccess" policy to this user.

2. **Create Security Credentials:**
   - After creating the user, generate an Access Key and Secret Access Key for this user. You will need these credentials later.

### EC2 Instance Setup

3. **Launch an EC2 Instance:**
   - Choose the desired region (e.g., us-west-2).
   - Launch an Ubuntu instance. Make sure to configure the security group to allow SSH access.

4. **SSH to the EC2 Instance:**
   - Use your local terminal to SSH into the instance:
     ```
     ssh -i <path-to-your-key-file> ubuntu@<instance-public-ip>
     ```

5. **Install AWS CLI v2:**
   - Download and install the AWS CLI v2:
     ```
     curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
     sudo apt install unzip
     unzip awscliv2.zip
     sudo ./aws/install -i /usr/local/aws-cli -b /usr/local/bin --update
     ```

6. **Configure AWS CLI:**
   - Configure the AWS CLI with the Access Key and Secret Access Key from step 2:
     ```
     aws configure
     ```

### Kubernetes Tools Setup

7. **Install kubectl:**
   - Download and install kubectl:
     ```
     curl -o kubectl https://amazon-eks.s3.us-west-2.amazonaws.com/1.19.6/2021-01-05/bin/linux/amd64/kubectl
     chmod +x ./kubectl
     sudo mv ./kubectl /usr/local/bin
     kubectl version --short --client
     ```

8. **Install eksctl:**
   - Download and install eksctl:
     ```
     curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
     sudo mv /tmp/eksctl /usr/local/bin
     eksctl version
     ```

### EKS Cluster Setup

9. **Create an EKS Cluster:**
   - Use eksctl to create the EKS cluster (replace `<cluster-name>` and `<region>` with your desired values):
     ```
     eksctl create cluster --name <cluster-name> --region <region> --node-type t2.micro --nodes-min 2 --nodes-max 2
     ```

10. **Update Kubeconfig:**
    - Update your kubeconfig to connect to the newly created EKS cluster:
      ```
      aws eks update-kubeconfig --region <region> --name <cluster-name>
      ```

11. **Verify Nodes:**
    - Verify that the EKS nodes are running:
      ```
      kubectl get nodes
      ```

### Deploying and Managing Applications

12. **Run Manifests:**
    - Create a Kubernetes namespace (replace `<namespace>` with your desired namespace name):
      ```
      kubectl create namespace <namespace>
      ```
    - Apply your Kubernetes manifests (replace `<path-to-manifests>` with the path to your manifests):
      ```
      kubectl apply -f <path-to-manifests>
      ```

13. **Delete Manifests:**
    - If needed, delete the deployed resources:
      ```
      kubectl delete -f <path-to-manifests>
      ```

### Cleaning Up

14. **Delete EKS Cluster:**
    - When you're done with your EKS cluster, you can delete it:
      ```
      eksctl delete cluster --name <cluster-name> --region <region>
      ```

This guide should help you set up and manage an AWS EKS cluster step by step. Make sure to replace `<cluster-name>`, `<region>`, `<namespace>`, and `<path-to-manifests>` with your specific values and paths as needed.



