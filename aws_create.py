# Import default class
from aws import AWSDefault

# Boto3 imports
import boto3
from botocore.exceptions import ClientError

# OS import for managing key pair files
import os


class AWSCreate(AWSDefault):
    def generate_key_pair(self, keyname: str, filename: str):
        print(f"\nGenerating a key pair with name {keyname}...\n")

        try:
            self.key_pair_name = keyname

            # Creates key pair via EC2 client
            keypair = self.client.create_key_pair(
                KeyName=keyname,
                TagSpecifications=[
                    {"ResourceType": "key-pair", "Tags": [self.key_tags]}
                ],
            )

            print("\nKey pair was generated successfully.")
            print(f"Name: {keyname}")
            print(f"ID: {keypair['KeyPairId']}")

            # Checks if a .ssh folder exists, creates one if it doesn't
            file_path = os.path.join(os.getcwd(), ".ssh")

            if not os.path.exists(file_path):
                os.mkdir(file_path)

            # Creates full path
            file_path = os.path.join(file_path, filename)

            # If key pair already exists, delete it
            if os.path.exists(file_path):
                os.remove(file_path)

            # Creates new key pair
            with open(file_path, "w+") as out:
                out.write(keypair["KeyMaterial"])

            # Change file permissions in order to connect to the instance
            os.chmod(file_path, 0o600)

            print(f"\nKey par with name {keyname} has been saved to {file_path}.")

        except ClientError as c_error:
            print(f"\nERROR: {c_error}")

    def create_security_group(self, sec_group_name: str, permissions: dict):
        print(f"\nCreating new security group named {sec_group_name}...")
        try:
            # Creates security group via EC2 client
            security_group = self.client.create_security_group(
                Description="Security group created by Bruno",
                GroupName=sec_group_name,
                TagSpecifications=[
                    {"ResourceType": "security-group", "Tags": [self.security_tags]}
                ],
                VpcId=self.vpc_id,
            )

            # Stores security group id
            self.sec_group_id = security_group["GroupId"]
            print(
                f"Security group with ID {self.sec_group_id} using Vpc {self.vpc_id} created successfully."
            )

            # Configures security group ingress access
            ingress = self.client.authorize_security_group_ingress(
                GroupId=self.sec_group_id, IpPermissions=permissions
            )

            print("Security group authorizations configured successfully.")

            return self.sec_group_id

        except ClientError as c_error:
            print(f"\nERROR: {c_error}")

        return

    def create_instance(self, img_id: str, user_data: str):
        print(
            f"\nCreating a new instance with image_id {img_id} using keypair {self.key_pair_name}..."
        )

        try:
            # Creates a new waiter
            instance_waiter = self.client.get_waiter("instance_status_ok")

            # Creates the instance via EC2 resource
            instance = self.resource.create_instances(
                ImageId=img_id,
                InstanceType="t2.micro",
                KeyName=self.key_pair_name,
                MaxCount=1,
                MinCount=1,
                SecurityGroupIds=[self.sec_group_id],
                TagSpecifications=[
                    {"ResourceType": "instance", "Tags": [self.instance_tags]}
                ],
                UserData=user_data,
            )

            # Saves the ID returned as a variable for easier referencing
            instance_id = instance[0].id

            # Checks if instance was created and is running
            instance_waiter.wait(InstanceIds=[instance_id])

            # Getting the instance's public IP address
            describe = self.client.describe_instances(InstanceIds=[instance_id])
            instances = describe["Reservations"][0]["Instances"][0]
            private_ip = instances["NetworkInterfaces"][0]["PrivateIpAddresses"][0]
            public_ip = private_ip["Association"]["PublicIp"]

            print("Instance created successfully.")
            print(f"ID: {instance_id}")
            print(f"Public IP address: {public_ip}")

            # Stores the ID as class variable
            self.instance_id = instance_id

            return public_ip

        except ClientError as c_error:
            print(f"\nERROR: {c_error}")

        return

    def create_ami_image(self, ami_name: str):
        print(
            f"\nCreating an AMI with name {ami_name} from instance with ID {self.instance_id}"
        )
        try:
            # Creates a new waiter
            ami_waiter = self.client.get_waiter("image_available")

            # Creates the AMI image using EC2 client
            ami_image = self.client.create_image(
                InstanceId=self.instance_id, NoReboot=True, Name=ami_name
            )

            # Checks if AMI has been created
            ami_waiter.wait(ImageIds=[ami_image["ImageId"]])
            print(f"AMI {ami_name} has been created successfully.")

            # Stores the ID as class variable
            self.ami_id = ami_image["ImageId"]

        except ClientError as c_error:
            print(f"\nERROR: {c_error}")

        return

    def create_load_balancer(
        self, load_name: str, security_group: dict, load_tags: dict
    ):
        print(f"\nCreating ElasticLoadBalancer with name {load_name}")
        try:
            # Creates the LoadBalancer via ELB client
            load_balancer = self.load_balancer.create_load_balancer(
                LoadBalancerName=load_name,
                Listeners=[
                    {
                        "InstancePort": 8080,
                        "LoadBalancerPort": 8080,
                        "Protocol": "HTTP",
                    },
                ],
                Subnets=self.subnets,
                SecurityGroups=[self.sec_group_id],
                Tags=[load_tags],
            )

            # Checks if LoadBalancer has been created every 10s
            created = False
            while not created:
                loadbalancers = self.load_balancer.describe_load_balancers()[
                    "LoadBalancerDescriptions"
                ]
                for loadbalancer in loadbalancers:
                    if loadbalancer["LoadBalancerName"] == load_name:
                        created = True

                self.stopwatch(10)

            print(f"ElasticLoadBalancer {load_name} created successfully")

        except ClientError as c_error:
            print(f"\nERROR: {c_error}")

    def create_launch_configuration(self, launch_name: str):
        print(f"\nCreating launch configuration with name {launch_name}...")
        print(
            f"Configuration is using key pair {self.key_pair_name}, security group with ID {self.sec_group_id} and AMI with ID {self.ami_id}."
        )
        try:
            # Creates launch configuration using autoscaling client
            launch_config = self.autoscaling.create_launch_configuration(
                LaunchConfigurationName=launch_name,
                ImageId=self.ami_id,
                InstanceMonitoring={"Enabled": True},
                InstanceType="t2.micro",
                KeyName=self.key_pair_name,
                SecurityGroups=[self.sec_group_id],
            )

            print(f"Launch configuration {launch_name} created successfully.")

        except ClientError as c_error:
            print(f"\nERROR: {c_error}")

    def create_autoscaling(self, auto_name: str, launch_name: str, load_name: str):
        print(f"\nCreating autoscaling with name {auto_name}")
        print(
            f"Autoscaling is using launch configuration {launch_name} and LoadBalancer {load_name}."
        )
        try:
            # Creates autoscaling using autoscaling client
            autoscaling = self.autoscaling.create_auto_scaling_group(
                AutoScalingGroupName=auto_name,
                LaunchConfigurationName=launch_name,
                MinSize=2,
                MaxSize=3,
                LoadBalancerNames=[load_name],
                DesiredCapacity=2,
                AvailabilityZones=self.zones,
            )

            # Describes the autoscaling created
            describe = self.autoscaling.describe_auto_scaling_groups(
                AutoScalingGroupNames=[auto_name]
            )

            # Checks if describe has values, if not, autoscaling hasn't been created yet
            while len(describe["AutoScalingGroups"]) == 0:
                self.stopwatch(10)

            print(f"Autoscaling {auto_name} created successfully.")

        except ClientError as c_error:
            print(f"\nERROR: {c_error}")
