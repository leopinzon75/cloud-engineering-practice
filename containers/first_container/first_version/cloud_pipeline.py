import boto3
from moto import mock_aws

@mock_aws
def cloud_step_four():
    s3 = boto3.resource("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="step-by-step-bucket")
    
    with open("baseline_test.txt", "r") as file:
        local_data = file.read()
    s3.Object("step-by-step-bucket", "cloud_misfire_copy.txt").put(Body=local_data)
    
    cloud_object = s3.Object("step-by-step-bucket", "cloud_misfire_copy.txt")
    cloud_data = cloud_object.get()['Body'].read().decode('utf-8')
    
    print("📥 Data pulled back down from S3 Bucket:")
    print(cloud_data)

if __name__ == "__main__":
    cloud_step_four()
