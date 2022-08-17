# aws cloudformation deploy \
#     --stack-name klubby-appsync-dev \
#     --template template.yaml \
#     --region us-east-1 \
#     --capabilities CAPABILITY_IAM


ARTIFACTS_BUCKET=klubby-sandbox-artifacts
STAGE=dev

aws cloudformation package \
    --s3-bucket $ARTIFACTS_BUCKET \
    --template-file template.yaml \
    --output-template-file template.package.yaml
    # --region us-east-1 \
    # --capabilities CAPABILITY_IAM \
    # --parameter-override \
    #     Stage=$STAGE


aws cloudformation deploy \
    --s3-bucket $ARTIFACTS_BUCKET \
    --stack-name klubby-appsync-$STAGE \
    --template template.package.yaml \
    --region us-east-1 \
    --capabilities CAPABILITY_IAM \
    --parameter-override \
        Stage=$STAGE 
        # UserTableName=user-table-name-$STAGE 
        # ConversationTableName=conversation-table-name-$STAGE
        # UserConversationBridgeTableName=userconversationbridge-table-name-$STAGE
        # UserKlubBridgeTableName=userklubbridge-table-name-$STAGE
        # KlubConversationBridgeTableName=klubconversationbridge-table-name-$STAGE
        # MessageTableName=message-table-name-$STAGE
        # KlubTableName=klub-table-name-$STAGE
        # UserPoolId=userpool-id-$STAGE
        # CreateKlubAvatarPresignedUrlFunctionArn=create-klub-avatar-presigned-url-function-arn-$STAGE
        # JoinKlubFunctionArn=join-klub-function-arn-$STAGE