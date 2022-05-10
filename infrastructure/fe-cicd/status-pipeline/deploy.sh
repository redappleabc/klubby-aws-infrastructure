sam deploy \
--stack-name status-pipeline-fe-prod \
--region us-east-1 \
--s3-bucket klubby-prod-artifacts-bucket \
--capabilities CAPABILITY_IAM \
--parameter-overrides \
      ParameterKey=IntegrationType,ParameterValue=GitHub \
      ParameterKey=IntegrationUser,ParameterValue=bjudson1 \
      ParameterKey=IntegrationPass,ParameterValue=$1 \
      ParameterKey=iOSPipelineName,ParameterValue=ios-pipeline-name-prod \
      ParameterKey=AndroidPipelineName,ParameterValue=android-pipeline-name-prod \
      ParameterKey=Stage,ParameterValue=prod

      
sam deploy \
--stack-name status-pipeline-fe-dev \
--region us-east-1 \
--s3-bucket klubby-dev-artifacts-bucket \
--capabilities CAPABILITY_IAM \
--parameter-overrides \
      ParameterKey=IntegrationType,ParameterValue=GitHub \
      ParameterKey=IntegrationUser,ParameterValue=bjudson1 \
      ParameterKey=IntegrationPass,ParameterValue=$1 \
      ParameterKey=iOSPipelineName,ParameterValue=ios-pipeline-name-dev \
      ParameterKey=AndroidPipelineName,ParameterValue=android-pipeline-name-dev