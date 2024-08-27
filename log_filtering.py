import boto3
import os
import datetime

"""
This portion will obtain the Environment variables from AWS Lambda.
DESTINATION_BUCKET kubeday-5gcore-logs-ingestion
GROUP_NAME         /aws/containerinsights/eks-blueprint/application
NDAYS              1
PREFIX             ip-
"""

GROUP_NAME = os.environ['GROUP_NAME']
DESTINATION_BUCKET = os.environ['DESTINATION_BUCKET']
PREFIX = os.environ['PREFIX']
NDAYS = os.environ['NDAYS']
nDays = int(NDAYS)

currentTime = datetime.datetime.now()
StartDate = currentTime - datetime.timedelta(days=nDays)
EndDate = currentTime - datetime.timedelta(days=nDays - 1)


"""
Convert the from & to Dates to milliseconds
"""

fromDate = int(StartDate.timestamp() * 1000)
toDate = int(EndDate.timestamp() * 1000)


BUCKET_PREFIX = os.path.join(PREFIX, StartDate.strftime('%Y{0}%m{0}%d').format(os.path.sep))


def lambda_handler(event, context):
    client = boto3.client('logs')
    client.create_export_task(
         logGroupName=GROUP_NAME,
         fromTime=fromDate,
         to=toDate,
         destination=DESTINATION_BUCKET,
         destinationPrefix=BUCKET_PREFIX
        )
