# boto3 (AWS) client injection

A boto3 S3 client is wired as a `@Singleton` (built once, from `@Config` AWS
settings) and injected into a `Storage` service by type. The same pattern works
for any boto3 client (DynamoDB, SQS, …).

```bash
AWS_REGION=us-east-1 python -m examples.di.boto3.services   # needs AWS credentials
pytest examples/di/boto3 --no-cov      # overrides the client with a fake — no AWS needed
```
