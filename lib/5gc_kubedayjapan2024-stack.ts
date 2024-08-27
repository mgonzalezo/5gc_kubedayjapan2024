import * as cdk from 'aws-cdk-lib';
import * as blueprints from '@aws-quickstart/eks-blueprints';

class FluentBitAddOn implements blueprints.ClusterAddOn {
    deploy(clusterInfo: blueprints.ClusterInfo): void {
        const cluster = clusterInfo.cluster;
        
        // Define the Helm chart for Fluent Bit
        cluster.addHelmChart('fluent-bit', {
            chart: 'fluent-bit',
            release: 'fluent-bit',
            repository: 'https://fluent.github.io/helm-charts',
            namespace: 'kube-system',
            values: {
                serviceAccount: {
                    create: true,
                    name: 'fluent-bit'
                },
                config: {
                    service: {
                        Flush: 1,
                        Log_Level: 'info',
                    },
                    inputs: [
                        {
                            name: "tail",
                            path: "/var/log/containers/*.log",
                            parser: "docker"
                        }
                    ],
                    outputs: [
                        {
                            name: "cloudwatch",
                            match: "*",
                            region: region,
                            log_group_name: "/aws/eks/fluent-bit-cloudwatch",
                            log_stream_prefix: "fluent-bit-",
                        }
                    ]
                }
            }
        });
    }
}

const app = new cdk.App();
const account = '615956341945';
const region = 'us-east-1';
const version = 'auto';

blueprints.HelmAddOn.validateHelmVersions = true; // optional if you would like to check for newer versions

const addOns: Array<blueprints.ClusterAddOn> = [
    new blueprints.addons.ArgoCDAddOn(),
    new blueprints.addons.MetricsServerAddOn(),
    new blueprints.addons.ClusterAutoScalerAddOn(),
    new blueprints.addons.AwsLoadBalancerControllerAddOn(),
    new blueprints.addons.VpcCniAddOn(),
    new blueprints.addons.CoreDnsAddOn(),
    new blueprints.addons.KubeProxyAddOn(),
    new FluentBitAddOn() // Adding Fluent Bit
];

const stack = blueprints.EksBlueprint.builder()
    .account(account)
    .region(region)
    .version(version)
    .addOns(...addOns)
    .useDefaultSecretEncryption(true) // set to false to turn secret encryption off (non-production/demo cases)
    .build(app, 'eks-kubeday-2024');