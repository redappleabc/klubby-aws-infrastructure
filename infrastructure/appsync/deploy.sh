delete-resolver
    --api-id klubby-graphql-dev
    --type-name Query
    --field-name getUsers getUserWallets

aws cloudformation deploy \
    --stack-name klubby-appsync-dev \
    --template template.yaml \
    --region us-east-1 \
    --capabilities CAPABILITY_IAM
    