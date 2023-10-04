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
- Clone the code
```bash
git clone https://github.com/LondheShubham153/two-tier-flask-app.git
```
- Move to `two-tier-flask-app/helm-charts/app-chart` directory
```bash
cd two-tier-flask-app/helm-charts/app-chart
```
- Create a HELM Chart
```bash
helm create application-chart
```
- Move to `application-chart` directory and do `ls -l`, you will see lots of files and folders
- Replace values.yml file's content with the following content,
```bash
# Default values for app.
# This is a YAML-formatted file.
# Declare variables to be passed into your templates.

replicaCount: 2

image:
  repository: madhupdevops/two-tier-microservice-app
  pullPolicy: Always
  # Overrides the image tag whose default is the chart appVersion.
  tag: "latest"

container:
  name: two-tier-app

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  # Specifies whether a service account should be created
  create: true
  # Automatically mount a ServiceAccount's API credentials?
  automount: true
  # Annotations to add to the service account
  annotations: {}
  # The name of the service account to use.
  # If not set and create is true, a name is generated using the fullname template
  name: ""

podAnnotations: {}
podLabels: {}

podSecurityContext: {}
  # fsGroup: 2000

securityContext: {}
  # capabilities:
  #   drop:
  #   - ALL
  # readOnlyRootFilesystem: true
  # runAsNonRoot: true
  # runAsUser: 1000

service:
  type: NodePort
  port: 80
  targetport: 5000
  protocol: TCP
  nodeport: 30007

ingress:
  enabled: false
  className: ""
  annotations: {}
    # kubernetes.io/ingress.class: nginx
    # kubernetes.io/tls-acme: "true"
  hosts:
    - host: chart-example.local
      paths:
        - path: /
          pathType: ImplementationSpecific
  tls: []
  #  - secretName: chart-example-tls
  #    hosts:
  #      - chart-example.local

resources: {}
  # We usually recommend not to specify default resources and to leave this as a conscious
  # choice for the user. This also increases chances charts run on environments with little
  # resources, such as Minikube. If you do want to specify resources, uncomment the following
  # lines, adjust them as necessary, and remove the curly braces after 'resources:'.
  # limits:
  #   cpu: 100m
  #   memory: 128Mi
  # requests:
  #   cpu: 100m
  #   memory: 128Mi

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 100
  targetCPUUtilizationPercentage: 80
  # targetMemoryUtilizationPercentage: 80

# Additional volumes on the output Deployment definition.
volumes: []
# - name: foo
#   secret:
#     secretName: mysecret
#     optional: false

# Additional volumeMounts on the output Deployment definition.
volumeMounts: []
# - name: foo
#   mountPath: "/etc/foo"
#   readOnly: true

nodeSelector: {}

tolerations: []

affinity: {}
```
