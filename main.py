from aws_create import AWSCreate
from aws_delete import AWSDelete

################### PARAMETERS ###################

# Image IDs
nv_img_id = "ami-00ddb0e5626798373"
oh_img_id = "ami-0dd9f0e7df0f0a138"

# Regions
nv_region = "us-east-1"
oh_region = "us-east-2"

# Security Groups
ohio_permissions = [
    {
        "FromPort": 22,
        "IpProtocol": "tcp",
        "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
        "ToPort": 22,
    },
    {
        "FromPort": 5432,
        "IpProtocol": "tcp",
        "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
        "ToPort": 5432,
    },
]

north_virginia_permissions = [
    {
        "FromPort": 22,
        "IpProtocol": "tcp",
        "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
        "ToPort": 22,
    },
    {
        "FromPort": 8080,
        "IpProtocol": "tcp",
        "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
        "ToPort": 8080,
    },
]

######################## TAGS ########################

# Key pair
nv_key_tag = {"Key": "Name", "Value": "key_tag_bruno_nv"}
oh_key_tag = {"Key": "Name", "Value": "key_tag_bruno_ohio"}

# Security Group
sec_group_tag = {"Key": "Name", "Value": "security_tags_bruno"}

# Instances
nv_instance_tag = {"Key": "Name", "Value": "instance_tag_bruno_nv"}
oh_instance_tag = {"Key": "Name", "Value": "instance_tag_bruno_ohio"}

# Load Balancer
nv_load_tag = {"Key": "Name", "Value": "load_balancer_tag_bruno_nv"}


if __name__ == "__main__":

    ######################## RUNNING OHIO INSTANCE ########################

    # Reads postgres script
    with open("scripts/postgres.sh", "r") as p:
        postgres_script = p.read()

    # Sets postgres IP address
    postgres_ip = 0

    # Deletes everything before creation
    print("\nClearing Ohio region...")
    ohio_delete = AWSDelete(
        region=oh_region,
        key_tags=oh_key_tag,
        security_tags=sec_group_tag,
        instance_tags=oh_instance_tag,
    )

    ohio_delete.delete_instances()
    ohio_delete.delete_security_group()
    ohio_delete.delete_key_pairs()

    # Creates and starts the instance
    print("\nCreating Ohio instance...")
    ohio_create = AWSCreate(
        region=oh_region,
        key_tags=oh_key_tag,
        security_tags=sec_group_tag,
        instance_tags=oh_instance_tag,
    )

    ohio_create.generate_key_pair(keyname="brunosd1_ohio", filename="ohio_instance")
    ohio_create.create_security_group(
        sec_group_name="postgres", permissions=ohio_permissions
    )
    postgres_ip = ohio_create.create_instance(
        img_id=oh_img_id, user_data=postgres_script
    )

    ######################## RUNNING N. VIRGINIA INSTANCE ########################

    # Reads django script
    with open("scripts/django.sh", "r") as d:
        django_script = d.read().replace("ADD_IP_HERE", postgres_ip)

    # Deletes everything before creation
    print("\nClearing North Virginia region...")
    nv_delete = AWSDelete(
        region=nv_region,
        key_tags=nv_key_tag,
        security_tags=sec_group_tag,
        instance_tags=nv_instance_tag,
    )

    nv_delete.delete_autoscaling("autoscaling_bruno_nv")
    nv_delete.delete_load_balancers("lb-bruno-nv")
    nv_delete.delete_launch_configuration(launch_name="launch_configs_bruno_nv")
    nv_delete.delete_ami_image(ami_name="django_ami_bruno")
    nv_delete.delete_instances()
    nv_delete.delete_security_group()
    nv_delete.delete_key_pairs()

    # Runs the instance
    print("\nCreating North Virginia instance...")
    nv_create = AWSCreate(
        region=nv_region,
        key_tags=nv_key_tag,
        security_tags=sec_group_tag,
        instance_tags=nv_instance_tag,
    )

    # Starts instance, loadbalancer and autoscaling
    nv_create.generate_key_pair(keyname="brunosd1_nv", filename="nv_instance")
    nv_create.create_security_group(
        sec_group_name="orm-bruno",
        permissions=north_virginia_permissions,
    )
    django_ip = nv_create.create_instance(img_id=nv_img_id, user_data=django_script)
    nv_create.create_ami_image(ami_name="django_ami_bruno")
    nv_delete.delete_instances()
    nv_create.create_load_balancer(
        load_name="lb-bruno-nv",
        security_group="orm-bruno",
        load_tags=nv_load_tag,
    )
    nv_create.create_launch_configuration(launch_name="launch_configs_bruno_nv")
    nv_create.create_autoscaling(
        auto_name="autoscaling_bruno_nv",
        launch_name="launch_configs_bruno_nv",
        load_name="lb-bruno-nv",
    )
