# klubby-aws-infrastructure
This repo contains the AWS infrastructure for the Klubby Application.

## Infrastructure Components
The following section goes through the major components of the AWS infrastructure.


### Front-End CICD

A high level overview for the architecture of the Front-End CICD can be seen in the following diagram.

<img src="documentation/images/fe-cicd-arch.png" width="900"/>

### Back-End CICD
TODO need to add this section
### AppSync GraphQL API

This is the main point of integration between the front end and the back end. The GraphQL API contains the following routes:

#TODO list all routes
- createConversataion
- createMessage
- listConversations
- listMessages


Resolvers can be found at `infrastructure/appsync/resolvers`.

### DynamoDB Storage
DynamoDB is the main storage solution for managing the state of the Klubby Application. It was selected for its simplicity, scalability, and real-time capabilities. The following figure shows and Entity Relationship Diagram outlining the major data tables managing the state of the Klubby application and their relationships.

<img src="documentation/images/erd.png" width="1200"/>


## Refrences

[AWS Blog Post - iOS GitPipeline](https://aws.amazon.com/blogs/devops/building-and-testing-ios-and-ipados-apps-with-aws-devops-and-mobile-services/)

[Deploying Capacitor iOS App](https://www.joshmorony.com/deploying-capacitor-applications-to-ios-development-distribution/#do-i-need-a-mac-to-deploy-to-ios)

[Pushing CodePipeline Status to Github](https://aws.amazon.com/blogs/devops/aws-codepipeline-build-status-in-a-third-party-git-repository/)

[AWS Blog Post - Android GitPipeline](https://aws.amazon.com/blogs/mobile/build-a-cicd-pipeline-for-your-android-app-with-aws-services/)

[Example Android CICD Docker Image](https://github.com/javiersantos/android-ci)