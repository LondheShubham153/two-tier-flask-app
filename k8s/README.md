# How to setup two-tier application deployment on kubernetes cluster
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
- Apply the manifests (database first, then the app):
```bash
kubectl apply -f mysql-pv.yml -f mysql-pvc.yml
kubectl apply -f mysql-deployment.yml -f mysql-svc.yml
kubectl apply -f two-tier-app-deployment.yml -f two-tier-app-svc.yml
```
- The app finds MySQL through the `mysql` Service DNS name, so there is no IP to edit.
- Open the app at `http://<node-ip>:30004`.
