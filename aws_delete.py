# Import default class
from aws import AWSDefault

# Boto3 imports
import boto3
from botocore.exceptions import ClientError


class AWSDelete(AWSDefault):
    def delete_autoscaling(self, auto_name: str):
        print(f"\nDeleting autoscaling {auto_name}...")
        try:
            # Describes the autoscaling with the name specified
            describe_auto = self.autoscaling.describe_auto_scaling_groups(
                AutoScalingGroupNames=[auto_name]
            )

            # Checks if describe has values
            if len(describe_auto["AutoScalingGroups"]) != 0:
                # Deletes values
                delete_auto = self.autoscaling.delete_auto_scaling_group(
                    AutoScalingGroupName=auto_name, ForceDelete=True
                )

                # Checks if there are new values, if there are, wait
                while len(describe_auto["AutoScalingGroups"]) != 0:
                    self.stopwatch(10)

                print(f"Autoscaling {auto_name} has been deleted successfully.")

        except ClientError as c_error:
            print(f"\nERROR: {c_error}")

    def delete_launch_configuration(self, launch_name: str):
        print(f"\nDeleting launch configuration {launch_name}...")
        try:
            # Describes the launch configuration with the name specified
            describe_launch = self.autoscaling.describe_launch_configurations(
                LaunchConfigurationNames=[launch_name]
            )

            # Checks if describe has values
            if len(describe_launch["LaunchConfigurations"]) != 0:
                # Deletes values
                delete_launch = self.autoscaling.delete_launch_configuration(
                    LaunchConfigurationName=launch_name
                )

                print(
                    f"Launch configuration {launch_name} has been deleted successfully."
                )

        except ClientError as c_error:
            print(f"\nERROR: {c_error}")

    def delete_load_balancers(self, load_name: str):
        print(f"\nDeleting LoadBalancer {load_name}...")
        try:
            # Gets list of all LoadBalancers
            load_balancers = self.load_balancer.describe_load_balancers()[
                "LoadBalancerDescriptions"
            ]

            # Checks if there is a LoadBalancer with the name specified
            load_exists = False
            for lb in load_balancers:
                if lb["LoadBalancerName"] == load_name:
                    load_exists = True

            # If the LoadBalancer exists, it needs to be deleted
            if load_exists:
                delete_load = self.load_balancer.delete_load_balancer(
                    LoadBalancerName=load_name
                )

                # Sets that there are more values to check
                has_values = True
                while has_values:
                    # Gets a new describe
                    loadbalancers = self.load_balancer.describe_load_balancers()[
                        "LoadBalancerDescriptions"
                    ]

                    # If there are no new values, we have deleted the LoadBalancers
                    if len(loadbalancers) == 0:
                        has_values = False

                    # If there are LoadBalancers, check if it is the same one.
                    # If it is, it may be a delay, so we can say that the LoadBalancer has been deleted.
                    for loadbalancer in loadbalancers:
                        if loadbalancer["LoadBalancerName"] == load_name:
                            has_values = False

                    # Waits 10s
                    self.stopwatch(10)

                print(f"LoadBalancer {load_name} has been deleted successfully.")

        except ClientError as c_error:
            print(f"\nERROR: {c_error}")

    def delete_ami_image(self, ami_name: str):
        print(f"\nDeleting AMI image {ami_name}...")
        try:
            # Searches for an AMI with the name specified
            image_id = self.client.describe_images(
                Filters=[{"Name": "name", "Values": [ami_name]}]
            )

            # Checks if any AMI has been found
            if len(image_id["Images"]) != 0:
                # Gets the AMI ID
                image_id = image_id["Images"][0]["ImageId"]

                # Deregisters the image
                delete_image = self.client.deregister_image(ImageId=image_id)
                print(
                    f"Image {delete_image['ResponseMetadata']['RequestId']} has been deleted successfully."
                )

        except ClientError as c_error:
            print(f"\nERROR: {c_error}")

    def delete_instances(self):
        print("\nDeleting all instances...")
        try:
            # Lists all instances with the class tags that are currently running
            instances = self.client.describe_instances(
                Filters=[
                    {
                        "Name": f"tag:{self.instance_tags['Key']}",
                        "Values": [self.instance_tags["Value"]],
                    },
                    {"Name": "instance-state-name", "Values": ["running"]},
                ]
            )

            # Checks if there are any instances
            if len(instances["Reservations"]) != 0:
                # Saves the instance ID
                instance = instances["Reservations"][0]["Instances"][0]
                instance_id = instance["InstanceId"]

                # Creates a new waiter
                instance_waiter = self.client.get_waiter("instance_terminated")

                # Terminates instance
                delete_instance = self.client.terminate_instances(
                    InstanceIds=[instance_id]
                )

                # Checks if instance hass been terminated
                instance_waiter.wait(InstanceIds=[instance_id])
                print(f"Instance {instance_id} has been deleted successfully.")

        except ClientError as c_error:
            print(f"\nERROR: {c_error}")

    def delete_security_group(self):
        print("\nDeleting all security groups in region...")
        try:
            # Lists all security groups using tags as filters
            sec_group_id = self.client.describe_security_groups(
                Filters=[
                    {
                        "Name": f"tag:{self.security_tags['Key']}",
                        "Values": [self.security_tags["Value"]],
                    }
                ]
            )

            # If there are security groups, they need to be deleted
            if len(sec_group_id["SecurityGroups"]) != 0:
                # Saves the ID for the security group (only one exists)
                sec_group_id = sec_group_id["SecurityGroups"][0]["GroupId"]

                # Tries to delete the security group
                while True:
                    try:
                        delete_security = self.client.delete_security_group(
                            GroupId=sec_group_id
                        )
                        break

                    except ClientError as c_error:
                        self.stopwatch(10)

                print(f"Security group {sec_group_id} has been deleted successfully.")

        except ClientError as c_error:
            print(f"\nERROR: {c_error}")

    def delete_key_pairs(self):
        print("\nDeleting all key pairs...")
        try:
            # Gets all key pairs with the class tags
            keys = self.client.describe_key_pairs(
                Filters=[
                    {
                        "Name": f"tag:{self.key_tags['Key']}",
                        "Values": [self.key_tags["Value"]],
                    }
                ]
            )

            # Checks if there are any keys
            if len(keys["KeyPairs"]) != 0:
                # Saves the key pair ID
                key_id = keys["KeyPairs"][0]["KeyPairId"]

                # Deletes the key pair
                delete_key = self.client.delete_key_pair(KeyPairId=key_id)
                print(f"Key pair {key_id} has been deleted successfully.")

        except ClientError as c_error:
            print(f"\nERROR: {c_error}")
