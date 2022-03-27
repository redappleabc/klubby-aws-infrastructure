aws cloudformation deploy \
    --stack-name klubby-storage-dynamodb-prod \
    --template template.yaml \
    --region us-east-1 \
    --capabilities CAPABILITY_IAM \
    --parameter-override \
      Stage=prod \
    
aws cloudformation deploy \
    --stack-name klubby-storage-dynamodb-dev \
    --template template.yaml \
    --region us-east-1 \
    --capabilities CAPABILITY_IAM