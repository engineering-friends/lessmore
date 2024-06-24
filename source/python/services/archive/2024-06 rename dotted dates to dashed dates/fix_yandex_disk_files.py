import os
import re
import time

import yadisk


# Function to authenticate with Yandex Disk
def authenticate_yadisk():
    # get from here: https://oauth.yandex.com for id and secret of the app and https://oauth.yandex.com/authorize?response_type=token&client_id=<app ID> for token (token will appear in url)
    disk = yadisk.YaDisk(
        id="<client_id>",
        secret="<client_secret>",
        token="<token>",
    )
    if disk.check_token():
        return disk
    else:
        raise Exception("Invalid Yandex Disk token")


# Function to rename files and directories on Yandex Disk
def rename_recursively(disk, path):
    for item in disk.listdir(path):
        item_path = item.path
        item_name = os.path.basename(item_path)

        # Replace dots in the date format with dashes
        new_name = re.sub(r'([0-9]{4})\.([0-9]{2})\.([0-9]{2})', r'\1-\2-\3', item_name)
        new_name = re.sub(r'([0-9]{4})\.([0-9]{2})', r'\1-\2', new_name)

        if item_name != new_name:
            new_path = os.path.join(os.path.dirname(item_path), new_name)
            disk.move(item_path, new_path)
            print(f"Renamed: {item_path} -> {new_path}")
            item_path = new_path  # Update item_path to the new path after renaming

            while True:
                try:
                    disk.get_meta(item_path)
                    break
                except yadisk.exceptions.PathNotFoundError:
                    time.sleep(1)
                    print('Waiting for the file to appear on the disk...')

        if item.type == "dir":
            rename_recursively(disk, item_path)


def test():
    # Authenticate with Yandex Disk
    disk = authenticate_yadisk()

    # Specify the root directory of your Yandex Disk
    root_directory = "/Apps"

    # Start renaming process
    rename_recursively(disk, root_directory)


if __name__ == "__main__":
    test()
