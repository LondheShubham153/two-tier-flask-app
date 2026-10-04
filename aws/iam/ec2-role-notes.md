# IAM role for the web instances

EC2 instances get AWS permissions through an **IAM role** (wrapped in an *instance profile*), never through access keys stored on the box.

## Create it (console)

IAM → Roles → **Create role**
1. Trusted entity: **AWS service** → use case **EC2**.
2. Attach policies:
   - `AmazonSSMManagedInstanceCore` (lets you open a shell with **Session Manager**, so no SSH key and no port 22)
   - the custom policy below (lets Docker send container logs to CloudWatch Logs)
3. Name it `twotier-web-role`.

Then use it in your launch template: **Advanced details → IAM instance profile → `twotier-web-role`**.

## Trust policy (what the console creates for you)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Service": "ec2.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

## Custom policy: `twotier-cloudwatch-logs`

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/two-tier-flask-app*"
    }
  ]
}
```

The `Resource` line is the point of the lesson: the instance can write to *this one* log group and nothing else (least privilege).
