from setuptools import setup


setup(
    name="discord-to-telegram-forwarder",
    version="0.1.0",
    description="",  # You can provide a description here
    author="marklidenberg",
    author_email="marklidenberg@gmail.com",
    python_requires=">=3.9",
    install_requires=[
        "aiohttp >=3.9,<4",
    ],
    packages=["discord-to-telegram-forwarder"],  # Replace with your actual package/directory name
)
