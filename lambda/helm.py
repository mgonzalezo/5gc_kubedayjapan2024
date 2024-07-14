import os
import subprocess

def handler(event, context):
    cluster_name = os.environ['CLUSTER_NAME']
    region = os.environ['REGION']
    charts = os.environ['CHARTS'].split(',')

    # Update kubeconfig
    subprocess.run([
        "aws", "eks", "--region", region, "update-kubeconfig", "--name", cluster_name
    ], check=True)

    # Define Helm chart details
    chart_details = {
        "open5gs": {
            "chart": "oci://registry-1.docker.io/gradiant/open5gs",
            "version": "2.2.0",
            "values": "https://gradiant.github.io/5g-charts/docs/open5gs-ueransim-gnb/5gSA-values.yaml"
        },
        "ueransim-gnb": {
            "chart": "oci://registry-1.docker.io/gradiant/ueransim-gnb",
            "version": "0.2.6"
        }
    }

    # Pull and install each chart
    for chart_name in charts:
        details = chart_details[chart_name]

        # Pull the Helm chart
        subprocess.run([
            "helm", "pull", details['chart'], "--version", details['version']
        ], check=True)

        # Install the Helm chart
        install_command = [
            "helm", "install", chart_name, details['chart'],
            "--version", details['version']
        ]

        if 'values' in details:
            install_command.extend(["--values", details['values']])

        subprocess.run(install_command, check=True)

    return {
        "statusCode": 200,
        "body": "Helm charts installed successfully"
    }
