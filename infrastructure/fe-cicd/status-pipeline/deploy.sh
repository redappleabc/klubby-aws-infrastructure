sam deploy \
--stack-name status-pipeline-prod \
--region us-east-1 \
--s3-bucket klubby-prod-artifacts-bucket \
--capabilities CAPABILITY_IAM \
--parameter-overrides \
      ParameterKey=IntegrationType,ParameterValue=GitHub \
      ParameterKey=IntegrationUser,ParameterValue=bjudson1 \
      ParameterKey=IntegrationPass,ParameterValue=$1 \
      ParameterKey=iOSPipelineName,ParameterValue=klubby-deployment-ios-prod-CodePipeline-RHMM4MNU0QKD \
      ParameterKey=AndroidPipelineName,ParameterValue=klubby-deployment-android-prod-CodePipeline-G5GUTQ9FI6IP \
      ParameterKey=Stage,ParameterValue=prod

      
sam deploy \
--stack-name status-pipeline-dev \
--region us-east-1 \
--s3-bucket klubby-dev-artifacts-bucket \
--capabilities CAPABILITY_IAM \
--parameter-overrides \
      ParameterKey=IntegrationType,ParameterValue=GitHub \
      ParameterKey=IntegrationUser,ParameterValue=bjudson1 \
      ParameterKey=IntegrationPass,ParameterValue=$1 \
      ParameterKey=iOSPipelineName,ParameterValue=klubby-deployment-ios-dev-CodePipeline-1HEOE4FWXISLN \
      ParameterKey=AndroidPipelineName,ParameterValue=klubby-deployment-android-dev-CodePipeline-N29K3HGHUFTU
