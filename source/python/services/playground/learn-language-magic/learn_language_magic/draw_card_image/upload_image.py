import asyncio

import httpx

from learn_language_magic.deps import Deps


async def upload_image_to_imgur(image_path: str, client_id: str):
    url = "https://api.imgur.com/3/image"
    headers = {"Authorization": f"Client-ID {client_id}"}

    async with httpx.AsyncClient() as client:
        with open(image_path, "rb") as image_file:
            files = {"image": image_file}
            response = await client.post(url, headers=headers, files=files)
            response_data = response.json()
            return response_data["data"]["link"]


def test():
    async def main():
        await upload_image_to_imgur(
            image_path="/tmp/image.png",
            client_id=Deps.load().config.imgur_client_id,
        )

    # Run the main function
    asyncio.run(main())


if __name__ == "__main__":
    test()
