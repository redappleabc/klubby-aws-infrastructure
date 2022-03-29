aws cloudformation deploy \
    --stack-name klubby-backend-cicd-dev \
    --template template.yaml \
    --region us-east-1 \
    --capabilities CAPABILITY_IAM \
    --parameter-override \
        GitHubOAuthToken=$1