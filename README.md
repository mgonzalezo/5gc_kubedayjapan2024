# KubeDay Japan 2024

Below are the steps to initialize a base app using typescript language, then you will install related EKS blueprints

```sh
cdk init app --language typescript
npm i @aws-quickstart/eks-blueprints

```

Then you will execute this command to prepare your AWS environment (specified by the AWS account ID and region) for deployment of CDK applications. It creates necessary resources, such as an S3 bucket for storing deployment assets. You then export the AWS_REGION variable and proceed with the CDK deployment.

```sh
cdk bootstrap aws://615956341945/us-east-1
export AWS_REGION=us-east-1
cdk deploy

```