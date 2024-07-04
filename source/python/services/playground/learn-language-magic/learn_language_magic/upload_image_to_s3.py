import asyncio

from typing import Optional

import aioboto3

from learn_language_magic.deps import Deps


async def upload_file_to_s3(
    filename: str,
    bucket: str,
    object_name: Optional[str] = None,
):
    object_name = object_name or filename
    session = aioboto3.Session()
    async with session.client("s3") as client:
        # Using async file open to read the file content
        with open(filename, "rb") as file_data:
            await client.upload_fileobj(file_data, bucket, object_name, ExtraArgs={"ACL": "public-read"})
    return f"https://{bucket}.s3.amazonaws.com/{object_name}"


def test():
    async def main():
        Deps.load()
        public_url = await upload_file_to_s3(filename="upload_image_to_s3.py", bucket="lessmore")
        print(f"File uploaded successfully. Public URL: {public_url}")

    asyncio.run(main())


if __name__ == "__main__":
    test()
