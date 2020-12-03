import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from json import dumps
import requests

load_balancer_client = boto3.client("elb", region_name="us-east-1")
loadbalancer = load_balancer_client.describe_load_balancers(
    LoadBalancerNames=["lb-bruno-nv"]
)
ip_address = loadbalancer["LoadBalancerDescriptions"][0]["DNSName"]
url = f"http://{ip_address}:8080/tasks"

while True:
    try:
        print("\nDatabase access\n")

        print("0: Test index")
        print("1: Create task")
        print("2: Get all tasks")
        print("3: Delete all tasks")

        print("Type the number corresponding to the action you want.")
        action = int(input("Action: "))

        if action == 0:
            print(f"\nResponse: {requests.get(url).text}")

        if action == 1:
            task = {
                "title": str(input("Task title: ")),
                "pub_date": datetime.now().isoformat(),
                "description": str(input("Task description: ")),
            }

            print(
                f"\nResponse: {requests.post(url + '/create_task', data=dumps(task)).text}"
            )

        if action == 2:
            print(f"\nResponse: {requests.get(url + '/get_tasks').text}")

        if action == 3:
            print(f"\nResponse: {requests.delete(url + '/delete_tasks').text}")

    except ValueError:
        print("INVALID ACTION")
        continue

    except:
        print("UNKNOWN ERROR")
        break
