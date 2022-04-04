sam deploy \
--stack-name status-pipeline-be-cicd-prod \
--region us-east-1 \
--s3-bucket klubby-prod-artifacts-bucket \
--capabilities CAPABILITY_IAM \
--parameter-overrides \
      ParameterKey=IntegrationType,ParameterValue=GitHub \
      ParameterKey=IntegrationUser,ParameterValue=bjudson1 \
      ParameterKey=IntegrationPass,ParameterValue=$1 \
      ParameterKey=PipelineName,ParameterValue=klubby-backend-cicd-prod-CodePipeline-14UEDUNV5K6IK \
      ParameterKey=Stage,ParameterValue=prod

      
sam deploy \
--stack-name status-pipeline-be-cicd-dev \
--region us-east-1 \
--s3-bucket klubby-dev-artifacts-bucket \
--capabilities CAPABILITY_IAM \
--parameter-overrides \
      ParameterKey=IntegrationType,ParameterValue=GitHub \
      ParameterKey=IntegrationUser,ParameterValue=bjudson1 \
      ParameterKey=IntegrationPass,ParameterValue=$1 \
      ParameterKey=PipelineName,ParameterValue=klubby-backend-cicd-dev-CodePipeline-1EZT8GA8NQZZQ \
