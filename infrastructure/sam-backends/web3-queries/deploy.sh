sam build
sam deploy \
    --stack-name klubby-dev-web3-queries \
    --s3-bucket klubby-dev-artifacts-bucket \
    --capabilities CAPABILITY_IAM \
    --region us-east-1 \
    --no-fail-on-empty-changeset