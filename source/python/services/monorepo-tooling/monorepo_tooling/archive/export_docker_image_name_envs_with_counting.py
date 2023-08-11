import os
import re
import subprocess

from typing import Optional


# - Utils


def bisect_left(a, x, lo=0, hi=None, *, key=None):
    """Source code from python 3.10 bisect module supporting key

    Return the index where to insert item x in list a, assuming a is sorted.
    The return value i is such that all e in a[:i] have e < x, and all e in
    a[i:] have e >= x.  So if x already appears in the list, a.insert(i, x) will
    insert just before the leftmost x already there.
    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """

    if lo < 0:
        raise ValueError("lo must be non-negative")
    if hi is None:
        hi = len(a)
    # Note, the comparison uses "<" to match the
    # __lt__() logic in list.sort() and in heapq
    if key is None:
        while lo < hi:
            mid = (lo + hi) // 2
            if a[mid] < x:
                lo = mid + 1
            else:
                hi = mid
    else:
        while lo < hi:
            mid = (lo + hi) // 2
            if key(a[mid]) < x:
                lo = mid + 1
            else:
                hi = mid
    return lo


# todo later: put into utils [@marklidenberg]
def execute_command(cmd):
    if isinstance(cmd, list):
        cmd = " ".join(cmd)
    return subprocess.check_output(cmd.split()).decode().strip()


# - Git Functions


def get_current_branch():
    return execute_command("git rev-parse --abbrev-ref HEAD")


def sanitize_branch(branch):
    return branch.replace("/", "-")


def get_commit_short_sha():
    return execute_command("git rev-parse --short HEAD")


def get_branches(branches_log: Optional[str] = None):
    """feature/add_linting
      feature/dev
    * master"""
    branches_log = branches_log or execute_command("git branch")
    return [branch for branch in re.findall(r"\S+", branches_log) if branch != "*"]


def get_master_branch():
    branches = get_branches()
    for variant in ["main", "master"]:
        if variant in branches:
            return variant

    raise Exception("Couldn't find master branch")


def get_commit_id(
    include_sha=True,
    include_commit_number=False,
    include_branch_prefix_for_side_branches=True,
    master_branch_alias="main",
):
    """
    Returns <branch_name>-<commit_number_from_master_or_root>-<short_sha>
    -------
    """

    # - Get branch name

    master_branch = get_master_branch()

    # - Get commits

    git_log = execute_command("git log")
    commits = re.findall(r"commit (\S+)", git_log)

    # - Find number of commits from branching root

    if get_current_branch() == master_branch:
        # [Master branch]

        commit_number = len(commits)
    else:
        # [Side branch]

        # - Find number of commits after branching from master branch

        def _is_master_branch_commit(commit):
            return master_branch in get_branches(execute_command(f"git branch --contains {commit}"))

        # map(_is_master_branch_commit, commits) = [0, 0, ..., 0, 1 (commit that we are looking for), 1, ..., 1]
        commit_number = bisect_left(commits, 1, key=lambda commit: int(_is_master_branch_commit(commit)))

    return "-".join(
        filter_true(
            [
                "branch" if get_current_branch() != master_branch and include_branch_prefix_for_side_branches else None,
                master_branch_alias
                if master_branch_alias and get_current_branch() == master_branch
                else sanitize_branch(get_current_branch()),
                str(commit_number) if include_commit_number else None,
                get_commit_short_sha() if include_sha else None,
            ]
        )
    )


def get_tags():
    return execute_command("git tag --points-at HEAD").split("\n")


def filter_true(values):
    return [value for value in values if value]


def get_image_name_by_alias():
    # - Assert required environment variables

    _required_envs = ["REGISTRY", "IMAGE_NAME", "DOCKER_DEFAULT_PLATFORM"]
    assert all(key in os.environ for key in _required_envs), f"Missing one of environment variables: {_required_envs}"

    # - Get tags for current commit

    image_names_by_alias = {
        "image_name_by_commit": "--".join(
            filter_true(
                [
                    f"{os.environ['REGISTRY']}/{os.environ['IMAGE_NAME']}:{get_commit_id()}",
                    os.environ["DOCKER_DEFAULT_PLATFORM"].replace("/", "."),
                    os.environ.get("IMAGE_SUFFIX"),
                ]
            )
        ),
        "image_name_latest": "--".join(
            filter_true(
                [
                    f"{os.environ['REGISTRY']}/{os.environ['IMAGE_NAME']}",
                    os.environ.get("IMAGE_SUFFIX"),
                ]
            )
        )
        + ":latest",
    }

    image_names_by_alias.update(
        {
            f"image_name_tag_{i}": "--".join(
                filter_true(
                    [
                        f"{os.environ['REGISTRY']}/{os.environ['IMAGE_NAME']}",
                        os.environ.get("IMAGE_SUFFIX"),
                    ]
                )
            )
            + f":{tag}"
            for i, tag in enumerate(filter_true(get_tags()))
        }
    )

    return image_names_by_alias


def export_docker_image_names():
    print(
        "{}".format(
            " ".join([f"{alias.upper()}={image_name}" for alias, image_name in get_image_name_by_alias().items()])
        )
    )


def example():
    os.environ["REGISTRY"] = "localhost"
    os.environ["IMAGE_NAME"] = "data-etl-python"
    os.environ["DOCKER_DEFAULT_PLATFORM"] = "linux/arm64/v8"

    export_docker_image_names()
    os.environ["IMAGE_SUFFIX"] = ""
    export_docker_image_names()


if __name__ == "__main__":
    example()
    # export_docker_image_names()
