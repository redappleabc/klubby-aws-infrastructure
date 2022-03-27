aws cloudformation deploy \
    --stack-name klubby-storage-prod \
    --template template.yaml \
    --region us-east-1 \
    --capabilities CAPABILITY_IAM \
    --parameter-override \
      Stage=prod \
    
aws cloudformation deploy \
    --stack-name klubby-storage-dev \
    --template template.yaml \
    --region us-east-1 \
    --capabilities CAPABILITY_IAM