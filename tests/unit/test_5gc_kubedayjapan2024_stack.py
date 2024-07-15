import aws_cdk as core
import aws_cdk.assertions as assertions

from 5gc_kubedayjapan2024.5gc_kubedayjapan2024_stack import 5GcKubedayjapan2024Stack

# example tests. To run these tests, uncomment this file along with the example
# resource in 5gc_kubedayjapan2024/5gc_kubedayjapan2024_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = 5GcKubedayjapan2024Stack(app, "5gc-kubedayjapan2024")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
