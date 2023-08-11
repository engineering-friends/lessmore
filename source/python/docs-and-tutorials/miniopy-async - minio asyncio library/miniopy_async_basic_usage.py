import asyncio

from miniopy_async import Minio


client = Minio("minio-hl.data.deeplay.io", access_key="", secret_key="", secure=True)


async def main():
    url = await client.fput_object(
        bucket_name="cg-public", object_name="miniopy_async_basic_usage.py", file_path="miniopy_async_basic_usage.py"
    )
    print("url:", url)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
