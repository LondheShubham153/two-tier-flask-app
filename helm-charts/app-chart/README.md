# Step by step guide for 2 tier application deployment using HELM Charts on Kubernetes Cluster
## Pre-requisites for helm chart deployment
- AWS account
- 2 Ubuntu OS Machines with t2.medium or above instance type
- Kubeadm setup

If you don't know how to setup Kubeadm follow this repository: https://github.com/LondheShubham153/kubestarter/blob/main/kubeadm_installation.md

After Pre-requisites are done, let's begin with HELM charts deployment.

## Installing HELM:
### On Master:
- Install HELM
```bash
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
sudo apt-get install apt-transport-https --yes
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm
```
- Verify HELM installation
```bash
helm version
```
