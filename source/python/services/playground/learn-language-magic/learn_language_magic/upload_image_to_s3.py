from typing import Optional

import boto3

from learn_language_magic.deps import Deps


def upload_file_to_s3(
    filename: str,
    bucket: str,
    object_name: Optional[str] = None,
):
    object_name = object_name or filename
    boto3.client("s3").upload_file(filename, bucket, object_name, ExtraArgs={"ACL": "public-read"})
    return f"https://{bucket}.s3.amazonaws.com/{object_name}"


def test():
    Deps.load()
    public_url = upload_file_to_s3(filename="upload_image_to_s3.py", bucket="lessmore")
    print(f"File uploaded successfully. Public URL: {public_url}")


if __name__ == "__main__":
    test()
