from setuptools import find_packages, setup


# Read the content of the README.md file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="discord-to-telegram-forwarder",
    version="0.1.3",
    author="marklidenberg",
    author_email="marklidenberg@gmail.com",
    description="A Discord to Telegram forwarder.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.9",
)
