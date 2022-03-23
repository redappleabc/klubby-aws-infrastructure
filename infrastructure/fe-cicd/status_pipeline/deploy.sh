aws cloudformation deploy \
    --stack-name klubby-fecicd-status-pipeline-dev \
    --template template.yaml \
    --region us-east-1 \
    --capabilities CAPABILITY_IAM \
    --parameter-override \
      IntegrationType=GitHub \
      IntegrationUser=bjudson1 \
      IntegrationPass=$1 \
      PipelineName=klubby-deployment-ios-dev-CodePipeline-1HEOE4FWXISLN