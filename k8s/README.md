### How to setup two-tier application deployment on kubernetes cluster
## First setup kubernetes kubeadm cluster
Use this repository to setup kubeadm https://github.com/LondheShubham153/kubestarter/blob/main/kubeadm_installation.md

## SetUp
- First clone the code to your machine
```bash
git clone https://github.com/LondheShubham153/two-tier-flask-app.git
```
- Move to k8s directory
```bash
cd two-tier-flask-app/k8s
```
- Create namespace so that both the containers (flaskapp & mysql) can communicate with each other
```bash
kubectl create namespace twotier
```
- Now, execute below commands one by one
```bash
kubectl apply -f twotier-deployment.yml
```
