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

        # Create a VPC for the EKS cluster with public subnets
        vpc = ec2.Vpc(self, "EksVpc",
                      max_azs=2,
                      subnet_configuration=[
                          ec2.SubnetConfiguration(
                              name="Public",
                              subnet_type=ec2.SubnetType.PUBLIC,
                              cidr_mask=24
                          )
                      ])

        # Create the IAM role for the EKS cluster
        eks_cluster_role = iam.Role(self, "EksClusterRole",
            assumed_by=iam.ServicePrincipal("eks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKSClusterPolicy"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKSServicePolicy"),
            ]
        )

        # Create the IAM role for the EC2 nodes
        node_role = iam.Role(self, "EksNodeRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKSWorkerNodePolicy"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKS_CNI_Policy"),
            ]
        )

        # Create the EKS cluster
        cluster = eks.Cluster(self, "EksCluster",
            vpc=vpc,
            default_capacity=0,
            version=eks.KubernetesVersion.V1_24,
            role=eks_cluster_role,
            vpc_subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)]
        )

        # Add a node group with the node role
        cluster.add_nodegroup_capacity("EksNodeGroup",
            desired_size=2,
            node_role=node_role
        )

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
        cluster.aws_auth.add_masters_role(helm_lambda.role)
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

app = cdk.App()
Kubedayjapan2024Stack(app, "Kubedayjapan2024Stack")
app.synth()
