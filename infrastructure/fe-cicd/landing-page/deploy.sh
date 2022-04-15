REGION=us-east-1

aws cloudformation deploy \
  --template-file ./template.yaml \
  --region $REGION \
  --capabilities CAPABILITY_IAM \
  --stack-name klubby-deployment-landingpage-prod \
  --parameter-overrides \
      ProjectName=klubby-landingpage \
      Repository=https://github.com/bjudson1/klubby-landing-page	\
      OauthToken=$OAUTH \
      Domain=klubby.io \
      Branch=main


aws cloudformation deploy \
  --template-file ./template.yaml \
  --region $REGION \
  --capabilities CAPABILITY_IAM \
  --stack-name klubby-deployment-landingpage-dev \
  --parameter-overrides \
      ProjectName=klubby-landingpage \
      Repository=https://github.com/bjudson1/klubby-landing-page	\
      OauthToken=$OAUTH \
      Domain=dev.klubby.io \
      Branch=dev