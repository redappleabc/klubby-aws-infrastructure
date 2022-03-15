REGION=us-east-1

aws cloudformation deploy \
  --template-file ./template.yaml \
  --region $REGION \
  --capabilities CAPABILITY_IAM \
  --stack-name klubby-webapp-fe-hosting \
  --parameter-overrides \
      ProjectName=klubby-webapp \
      Repository=https://github.com/bjudson1/klubby-react-app	\
      OauthToken=$OAUTH \
      Domain=klubby.me \
      Branch=main

# source awsume lea-staging-kernel

# aws cloudformation deploy \
#   --template-file ./template.yaml \
#   --capabilities CAPABILITY_IAM \
#   --stack-name lea-frontend-staging \
#   --parameter-overrides \
#       Repository=https://github.com/outsidesource/LEA-ConnectAmpSPA \
#       Domain=test.leaprofessional.cloud \
#       Branch=develop

# source awsume lea-prod-kernel

# aws cloudformation deploy \
#   --template-file ./template.yaml \
#   --capabilities CAPABILITY_IAM \
#   --stack-name lea-frontend-prod \
#   --parameter-overrides \
#       Repository=https://github.com/outsidesource/LEA-ConnectAmpSPA \
#       Domain=leaprofessional.cloud \
#       Branch=master