REGION=us-east-1

aws cloudformation deploy \
  --template-file ./template.yaml \
  --region $REGION \
  --capabilities CAPABILITY_IAM \
  --stack-name klubby-deployment-webapp-prod \
  --parameter-overrides \
      ProjectName=klubby-webapp \
      Repository=https://github.com/bjudson1/klubby-react-app	\
      OauthToken=$OAUTH \
      Domain=klubby.me \
      Branch=main

# source awsume klubby-dev

aws cloudformation deploy \
  --template-file ./template.yaml \
  --region $REGION \
  --capabilities CAPABILITY_IAM \
  --stack-name klubby-deployment-webapp-dev \
  --parameter-overrides \
      ProjectName=klubby-webapp \
      Repository=https://github.com/bjudson1/klubby-react-app \
      OauthToken=$OAUTH \
      Domain=dev.klubby.me \
      Branch=dev