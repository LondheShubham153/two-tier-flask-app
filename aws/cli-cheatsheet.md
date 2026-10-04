# AWS CLI cheat sheet

The labs are done in the console. These few commands are optional extras. Set your region once:

```bash
aws configure set region ap-south-1
aws sts get-caller-identity          # who am I?
```

## Find the latest Ubuntu 24.04 AMI (x86_64) — handy for launch templates
```bash
aws ssm get-parameter \
  --name /aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id \
  --query Parameter.Value --output text
```
Use `arm64` instead of `amd64` for Graviton (`t4g`) instances.

## What's running (and costing money)?
```bash
aws ec2 describe-instances \
  --filters Name=instance-state-name,Values=running \
  --query 'Reservations[].Instances[].[InstanceId,InstanceType,PrivateIpAddress,Tags[?Key==`Name`]|[0].Value]' \
  --output table
```

## Target health behind the load balancer
```bash
aws elbv2 describe-target-health --target-group-arn <your-tg-arn> \
  --query 'TargetHealthDescriptions[].[Target.Id,TargetHealth.State]' --output table
```

## Tail the container logs
```bash
aws logs tail /two-tier-flask-app --follow
```

## Push your own image to ECR (teaser)
```bash
aws ecr create-repository --repository-name two-tier-flask-app
aws ecr get-login-password | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-south-1.amazonaws.com
docker buildx build --platform linux/amd64,linux/arm64 \
  -t <account-id>.dkr.ecr.ap-south-1.amazonaws.com/two-tier-flask-app:latest --push .
```
