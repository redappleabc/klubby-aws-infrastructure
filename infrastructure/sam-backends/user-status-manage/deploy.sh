sam build

sam deploy \
    --stack-name user-status-manage-function-prod \
    --s3-bucket klubby-prod-artifacts-bucket \
    --capabilities CAPABILITY_IAM \
    --region us-east-1 \
    --no-fail-on-empty-changeset \
    --parameter-overrides \
        ParameterKey=Stage,ParameterValue=prod

    
sam deploy \
    --stack-name user-status-manage-function-dev \
    --s3-bucket klubby-dev-artifacts-bucket \
    --capabilities CAPABILITY_IAM \
    --region us-east-1 \
    --no-fail-on-empty-changeset \
    --parameter-overrides \
        ParameterKey=Stage,ParameterValue=dev
