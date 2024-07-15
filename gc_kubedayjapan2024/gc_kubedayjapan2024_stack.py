import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_eks as eks,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_logs as logs,
    custom_resources as cr,
)
from constructs import Construct

class Kubedayjapan2024Stack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a VPC for the EKS cluster
        vpc = ec2.Vpc(self, "EksVpc", max_azs=3)

        # Create the EKS cluster
        cluster = eks.Cluster(self, "EksCluster",
                              vpc=vpc,
                              default_capacity=2,
                              version=eks.KubernetesVersion.V1_21)

        # Add the necessary IAM policy to the cluster role for Helm charts
        cluster.admin_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name('AmazonEKSClusterPolicy'))
        cluster.admin_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name('AmazonEKSVPCResourceController'))

        # Define the Lambda function that will run the Helm commands
        helm_lambda = lambda_.Function(
            self, "HelmLambda",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="helm.handler",
            code=lambda_.Code.from_asset("lambda"),
            timeout=cdk.Duration.minutes(5),
            log_retention=logs.RetentionDays.ONE_DAY,
            environment={
                "CLUSTER_NAME": cluster.cluster_name,
                "REGION": self.region,
                "CHARTS": "open5gs,ueransim-gnb"
            }
        )

        # Grant the Lambda function necessary permissions
        cluster.admin_role.grant(helm_lambda, "eks:DescribeCluster")
        helm_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["eks:DescribeCluster"],
            resources=[cluster.cluster_arn]
        ))

        # Run the Lambda function once the cluster is ready
        provider = cr.Provider(self, "HelmProvider", on_event_handler=helm_lambda)
        cr.AwsCustomResource(self, "HelmResource", on_create=cr.AwsSdkCall(
            service='Lambda',
            action='invoke',
            parameters={
                "FunctionName": helm_lambda.function_name,
                "InvocationType": "Event"
            },
            physical_resource_id=cr.PhysicalResourceId.of(helm_lambda.function_name)
        ), policy=cr.AwsCustomResourcePolicy.from_statements([
            iam.PolicyStatement(
                actions=["lambda:InvokeFunction"],
                resources=[helm_lambda.function_arn]
            )
        ]))
