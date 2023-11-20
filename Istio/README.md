# Let's understand about istio service mesh

## 1) What is istio?
- Istio is a open-source service mesh implementation that manages the communication and data sharing between micro-services. This platform is added to reduce the complexity of managing network services.
- Once installed, it injects proxies inside a Kubernetes pod, next to the application container. Each proxy is configured to intercept requests and route traffic to the appropriate service while applying policies.

## 2) Why we need istio and service mesh in microservices?
- Moving from monolithic to microservice architecture, developers get the opportunity to build highly flexible, resilient, and scalable applications within much faster software development life cycles. Although the microservice architecture has many benefits, the evolution in application development also brings certain challenges.
- As the architecture consists of many individual services working together, it is important to ensure seamless communication. These autonomous components talk to each other through APIs. However, managing traffic flow and API calls requires a lot of time and effort from the development team.
- There was a need for a third-party solution that allowed team members to focus on developing the service logic instead of the network logic. Therefore, service meshes like Istio were designed to manage the network layer of service-to-service communication.

## 3) Challenges faced in microservices:
- Developers need lots of time for traffic management.
- All pods are running inside a cluster, and let's say any hacker or attacker enters the cluster, then he will misuse our secrets and services.

## 4) Features of istio:
- Manages whole network layer service-to-service communication.
- Injects proxies next to the running pods
- Security
- Traffic control
- Observability

## 5) Architecture of istio:

<img width="500" height="250" alt="image" src="https://github.com/LondheShubham153/two-tier-flask-app/assets/121779953/845ecbe3-1372-410b-ba71-c00c175d64d3">
