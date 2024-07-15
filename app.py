#!/usr/bin/env python3
import aws_cdk as cdk
from gc_kubedayjapan2024.gc_kubedayjapan2024_stack import Kubedayjapan2024Stack

app = cdk.App()
Kubedayjapan2024Stack(app, "Kubedayjapan2024Stack")

app.synth()
