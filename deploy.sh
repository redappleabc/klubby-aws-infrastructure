aws cloudformation deploy \
    --stack-name klubby-backend-cicd-prod \
    --template template.yaml \
    --region us-east-1 \
    --capabilities CAPABILITY_IAM \
    --parameter-override \
        GitHubOAuthToken=$1 \
        Stage=prod \
        GitHubBranch=main

aws cloudformation deploy \
    --stack-name klubby-backend-cicd-dev \
    --template template.yaml \
    --region us-east-1 \
    --capabilities CAPABILITY_IAM \
    --parameter-override \
        GitHubOAuthToken=$1