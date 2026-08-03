import pytest
from app import run_engine_sandbox
from botocore.exceptions import ClientError

class DummyS3Client:
    def __init__(self):
        self.buckets = set()
        self.objects = {}

    def head_bucket(self, Bucket):
        if Bucket not in self.buckets:
            raise ClientError({'Error': {'Code': '404', 'Message': 'Not Found'}}, 'HeadBucket')
        return {}

    def create_bucket(self, Bucket):
        self.buckets.add(Bucket)

    def put_object(self, Bucket, Key, Body):
        self.objects[f"{Bucket}/{Key}"] = Body

    def get_object(self, Bucket, Key):
        content = self.objects.get(f"{Bucket}/{Key}")
        class BodyStream:
            def read(self):
                return content.encode('utf-8') if isinstance(content, str) else content
        return {"Body": BodyStream()}

def test_run_engine_sandbox_p0300():
    mock_s3 = DummyS3Client()
    result = run_engine_sandbox(custom_s3_client=mock_s3)
    
    assert "P0300" in result
    assert "RANDOM/MULTIPLE CYLINDER MISFIRE DETECTED" in result
