# Boto3 imports
import boto3
from botocore.exceptions import ClientError

# Extra imports
from time import time


class AWSDefault:
    def __init__(
        self, region: str, key_tags: dict, security_tags: dict, instance_tags: dict
    ):
        # Boto3 methods
        self.client = boto3.client("ec2", region_name=region)
        self.resource = boto3.resource("ec2", region_name=region)
        self.load_balancer = boto3.client("elb", region_name=region)
        self.autoscaling = boto3.client("autoscaling", region_name=region)

        # Tags (for filtering)
        self.key_tags = key_tags
        self.security_tags = security_tags
        self.instance_tags = instance_tags

        # Subnets, VPC and zones
        self.subnets = [
            subnet["SubnetId"] for subnet in self.client.describe_subnets()["Subnets"]
        ]
        self.vpc_id = self.client.describe_vpcs().get("Vpcs", [{}])[0].get("VpcId", "")
        self.zones = [
            zone["ZoneName"]
            for zone in self.client.describe_availability_zones()["AvailabilityZones"]
        ]

        # Variables used to save values for later
        self.ami_id = None
        self.instance_id = None
        self.key_pair_name = None
        self.sec_group_id = None

    def stopwatch(self, t):
        t0 = time()
        t1 = time()
        while t1 - t0 <= t:
            t1 = time()