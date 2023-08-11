import os
import time

from typing import Dict

from loguru import logger

from lessmore.utils.legacy.minio_client import MinioClient
from lessmore.utils.transaction_manager.transaction_manager import TransactionManager


class MinioTransactionManager(TransactionManager):
    def __init__(self, minio_client, root, local_path="transactions"):
        self.minio_client = minio_client
        self.root = root
        self.local_path = local_path

        # - Remove directory symbol from local_path

        if self.local_path.endswith("/"):
            self.local_path = self.local_path[:-1]

        self.transactions_path = os.path.join(self.root, self.local_path)

    @staticmethod
    def create(transactions_root, minio_kwargs):
        return MinioTransactionManager(minio_client=MinioClient(**minio_kwargs), root=transactions_root)

    def _get_statuses(self):
        paths = [
            i.object_name
            for i in self.minio_client.list_objects(
                bucket_name=self.minio_client.bucket_name,
                recursive=False,
                start_after=self.transactions_path + "/",
                prefix=self.transactions_path + "/",  # for some reason, start_after is not enough :(
            )
        ]
        return [os.path.basename(os.path.dirname(path)) for path in paths]

    def get_status(self, id: str):
        path = self.get_path(id)
        if path is None:
            return None
        return os.path.basename(os.path.dirname(path))

    def get_path(self, id: str):
        for status in self._get_statuses():
            try:
                self.minio_client.minio_connect.get_object(
                    bucket_name=self.minio_client.bucket_name,
                    object_name=os.path.join(self.transactions_path, status, id + ".txt"),
                )
                return os.path.join(self.transactions_path, status, id + ".txt")
            except Exception as e:
                if "code: NoSuchKey" in str(e):
                    continue
                raise

        return None

    def is_submitted(self, id: str):
        return self.get_path(id) is not None

    def submit(self, id: str, status: str, body: str = ""):
        logger.debug("Submitting transaction", id=id, status=status, body=body)

        # - Remove transaction if already submitted

        while path := self.get_path(id):  # todo later: limit tries [@marklidenberg]
            logger.debug("Transaction already submitted, updating...", id=id, path=path)
            self.minio_client.remove_safe(path)
            time.sleep(1)

        # - Write transaction file

        with open(id + ".txt", "w") as f:
            f.write(body)

        # - Upload transaction file to minio

        self.minio_client.upload_to_minio(
            path=id + ".txt", object_name=os.path.join(self.transactions_path, status, id + ".txt")
        )

        # - Remove transaction file

        os.remove(id + ".txt")

    def reset(self):
        for status, base_paths in self.get_all().items():
            for base_path in base_paths:
                self.minio_client.remove_safe(os.path.join(self.transactions_path, status, base_path))

    def get_all(self) -> Dict:
        # - Get statuses

        statuses = self._get_statuses()

        # - Iterate over statuses

        return {
            status: [
                os.path.basename(i.object_name)
                for i in self.minio_client.list_objects(
                    bucket_name=self.minio_client.bucket_name,
                    recursive=True,
                    start_after=os.path.join(self.transactions_path, status + "/"),
                    prefix=os.path.join(
                        self.transactions_path, status
                    ),  # for some reason, start_after is not enough :(
                )
            ]
            for status in statuses
        }
