# aws cloudformation deploy \
#     --stack-name klubby-deployment-ios-prod \
#     --template template.yaml \
#     --region us-east-1 \
#     --capabilities CAPABILITY_IAM \
#     --parameter-override \
#       GitHubOAuthToken=$1 \
#       Stage=prod \
#       GitHubBranch=main

aws cloudformation deploy \
    --stack-name klubby-deployment-ios-dev \
    --template template.yaml \
    --region us-east-1 \
    --capabilities CAPABILITY_IAM \
    --parameter-override \
      GitHubOAuthToken=$1 \
      Stage=dev \
      GitHubBranch=dev