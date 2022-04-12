sam build
sam deploy \
    --stack-name add-new-user-function-dev \
    --s3-bucket klubby-prod-artifacts-bucket \
    --capabilities CAPABILITY_IAM \
    --region us-east-1 \
    --no-fail-on-empty-changeset