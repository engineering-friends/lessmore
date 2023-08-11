import os

import psutil

from lessmore.utils.system import execute_system_command


def get_kubernetes_container_memory_usage():
    if os.path.exists("/sys/fs/cgroup/memory.current"):
        # working from kubernetes pod or alike
        return int(execute_system_command("cat /sys/fs/cgroup/memory.current"))
    else:
        return psutil.virtual_memory().used


if __name__ == "__main__":
    print(get_kubernetes_container_memory_usage())
