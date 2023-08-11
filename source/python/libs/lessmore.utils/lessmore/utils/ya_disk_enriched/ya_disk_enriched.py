import os
import time

import yadisk

from yadisk.exceptions import DirectoryExistsError

from lessmore.utils.tested import tested
from lessmore.utils.ya_disk_enriched.unit_tests.test_ensure_directory_exists import test_ensure_directory_exists
from lessmore.utils.ya_disk_enriched.unit_tests.test_ensure_path_is_deleted import test_ensure_path_is_deleted
from lessmore.utils.ya_disk_enriched.unit_tests.test_force_upload import test_force_upload


class YaDiskEnriched(yadisk.YaDisk):
    @tested(tests=[test_ensure_directory_exists])
    def ensure_directory_exists(self, path):
        # - Prepare paths to create (from root to path: /a/b/c -> /a, /a/b, /a/b/c)

        path = path.removesuffix("/").removeprefix("/")  # "/a/b/c/" -> "a/b/c"
        parts = path.split("/")  # ["a", "b", "c"]
        paths = ["/" + "/".join(parts[:i]) for i in range(1, len(parts) + 1)]  # ["/a", "/a/b", "/a/b/c"]

        # - Create directories

        for path in paths:
            try:
                self.mkdir(path)
            except DirectoryExistsError:
                pass

    @tested(tests=[test_force_upload])
    def force_upload(self, filename, remote_filename):
        """Upload even if directory not exists or file exists."""

        # - Create directories if not exists

        self.ensure_directory_exists(os.path.dirname(remote_filename))

        # - Upload file

        if self.exists(remote_filename):
            time.sleep(1)  # needed for some reason, otherwise exception may be raised
            self.ensure_path_is_deleted(remote_filename)

        self.upload(filename, remote_filename)

    @tested(tests=[test_ensure_path_is_deleted])
    def ensure_path_is_deleted(self, path):
        if not self.exists(path):
            return
        else:
            self.remove(path, permanently=True)
