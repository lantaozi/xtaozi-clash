import os
import boto3


class R2Client:
    class Option:
        def __init__(self, account_id, access_key_id, access_key_secret, domain, bucket):
            self.account_id = account_id
            self.access_key_id = access_key_id
            self.access_key_secret = access_key_secret
            self.domain = domain
            self.bucket = bucket

    def __init__(self, option: Option) -> None:
        self.r2 = boto3.resource(
            "s3",
            endpoint_url=f"https://{option.account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=f"{option.access_key_id}",
            aws_secret_access_key=f"{option.access_key_secret}",
        )
        self.domain = option.domain
        self.bucket = self.r2.Bucket(option.bucket)

    def list_buckets(self):
        # Output the bucket names
        print("Existing buckets:")
        for bucket in self.r2.buckets.all():
            print(f"  {bucket.name}")

    def list_objects(self):
        for obj in self.bucket.objects.all():
            print(obj.key, obj.e_tag, obj.last_modified)

    def upload_file(self, file_name, object_name=None):
        if object_name is None:
            object_name = os.path.basename(file_name)
        self.bucket.upload_file(file_name, object_name)
        return f"{self.domain}/{object_name}"

    def delete_object(self, object_name):
        self.bucket.Object(object_name).delete()
