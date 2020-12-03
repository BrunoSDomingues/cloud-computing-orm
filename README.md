# cloud-computing-orm

Python program used to create a simple task manager that resides in AWS.

### AWS Functionalities
- Usage of tags in order to filter more efficiently
- Usage of autoscaling and load balancers

### What the script does, step-by-step
1) Clears all instances, security groups and key pairs in the Ohio region
2) Creates a new key pair and stores it locally on a new `.ssh` folder
3) Creates a new security group
4) Launches an instance using the key pair and security group created 
5) Clears all autoscaling groups, load balancers, launch configs, AMI images, instances, security groups and key pairs in the North Virginia region
6) Creates a new key pair and stores it locally
7) Creates a new security group
8) Launches an instance using the key pair and security group created
9) Generates an AMI image from the instance launched and then deletes it
10) Creates a Classic load balancer 
11) Creates a Launch Configuration that uses the key pair, security group and AMI image created
12) Creates an Autoscaling Group that uses the launch config and load balancer created

### Task manager functionalities
- Create a task
- Get all tasks
- Delete all tasks

## Running the program
1) Install `boto3` and `aws-cli` on your machine
2) Run `aws configure` to setup your access key ID, secret access key and region
3) Run `python main.py` (the script takes about 10 minutes to run)
4) Run `python client.py` to use a local client for the task manager (if it isn't working at first, wait a while because the LoadBalancer may be offline)
