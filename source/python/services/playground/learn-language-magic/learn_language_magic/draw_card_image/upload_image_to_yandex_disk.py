import asyncio
import os.path

import aiofiles
import aiohttp

from learn_language_magic.deps import Deps


async def upload_image_to_yandex_disk(filename: str, yandex_disk_token: str):
    OAUTH_TOKEN = yandex_disk_token

    async def get_upload_link(session, path, overwrite=False):
        url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = {"Authorization": f"OAuth {OAUTH_TOKEN}"}
        params = {"path": path, "overwrite": str(overwrite).lower()}
        async with session.get(url, headers=headers, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            return data["href"]

    async def upload_file(session, upload_url, file_path):
        async with aiofiles.open(file_path, "rb") as f:
            file_data = await f.read()
        async with session.put(upload_url, data=file_data) as response:
            response.raise_for_status()

    async def publish_file(session, path):
        url = "https://cloud-api.yandex.net/v1/disk/resources/publish"
        headers = {"Authorization": f"OAuth {OAUTH_TOKEN}"}
        params = {"path": path}
        async with session.put(url, headers=headers, params=params) as response:
            response.raise_for_status()

    async def get_direct_download_link(session, path):
        url = "https://cloud-api.yandex.net/v1/disk/resources/download"
        headers = {"Authorization": f"OAuth {OAUTH_TOKEN}"}
        params = {"path": path}
        async with session.get(url, headers=headers, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            return data["href"]

    async def upload_image_and_get_url(local_image_path, yandex_disk_path):
        async with aiohttp.ClientSession() as session:
            # Step 1: Get upload link
            upload_url = await get_upload_link(session, yandex_disk_path, overwrite=True)

            # Step 2: Upload file to Yandex Disk
            await upload_file(session, upload_url, local_image_path)

            # Step 3: Publish the file to get a public URL
            await publish_file(session, yandex_disk_path)

            # Step 4: Get direct download link for the raw file
            direct_download_url = await get_direct_download_link(session, yandex_disk_path)
            return direct_download_url

    yandex_disk_path = f"Apps/learning-language-magic/{os.path.basename(filename)}"

    return await upload_image_and_get_url(filename, yandex_disk_path)


def test():
    async def main():
        print(
            await upload_image_to_yandex_disk(
                filename="/tmp/image.png",
                yandex_disk_token=Deps.load().config.yandex_disk_token,
            )
        )

    asyncio.run(main())


if __name__ == "__main__":
    test()
