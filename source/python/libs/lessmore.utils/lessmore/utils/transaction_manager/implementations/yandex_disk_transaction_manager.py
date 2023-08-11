import os

from loguru import logger

from lessmore.utils.transaction_manager.transaction_manager import TransactionManager
from lessmore.utils.ya_disk_enriched.ya_disk_enriched import YaDiskEnriched


class YandexDiskTransactionManager(TransactionManager):
    def __init__(self, yandex_disk_client, root, local_path="transactions"):
        self.yandex_disk_client = yandex_disk_client
        self.root = root
        self.local_path = local_path

        self.transactions_path = os.path.join(self.root, self.local_path)

    @staticmethod
    def create(yandex_config, transactions_root):
        yandex_disk_client = YaDiskEnriched(**yandex_config)

        if not yandex_disk_client.exists(transactions_root):
            yandex_disk_client.ensure_directory_exists(transactions_root)

        return YandexDiskTransactionManager(yandex_disk_client, root=transactions_root)

    def _get_statuses(self):
        paths = [value.path for value in self.yandex_disk_client.listdir(self.transactions_path)]
        return [os.path.basename(path) for path in paths]

    def get_status(self, id: str):
        path = self.get_path(id)
        if path is None:
            return None
        return os.path.basename(os.path.dirname(path))

    def get_path(self, id: str):
        for status in self._get_statuses():
            if self.yandex_disk_client.exists(os.path.join(self.transactions_path, status, id + ".txt")):
                return os.path.join(self.transactions_path, status, id + ".txt")

        return None

    def is_submitted(self, id: str):
        return self.get_path(id) is not None

    def submit(self, id: str, status: str, body: str = ""):

        # - Remove transaction if already submitted

        if self.is_submitted(id):
            path = self.get_path(id)
            logger.debug("Transaction already submitted, updating...", id=id, path=path)
            self.yandex_disk_client.ensure_path_is_deleted(path)

        # - Write transaction file

        with open(id + ".txt", "w") as f:
            f.write(body)

        # - Upload transaction file to yandex disk

        self.yandex_disk_client.force_upload(id + ".txt", os.path.join(self.transactions_path, status, id + ".txt"))

        # - Remove transaction file

        os.remove(id + ".txt")

    def reset(self):
        self.yandex_disk_client.ensure_path_is_deleted(self.transactions_path)
