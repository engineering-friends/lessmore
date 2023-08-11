import os
import re
import subprocess

from typing import Optional


# - Utils


def filter_true(values):
    return [value for value in values if value]


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


def get_branches(git_branch_output: Optional[str] = None):
    """feature/add_linting
      feature/dev
    * main"""
    git_branch_output = git_branch_output or execute_command("git branch")
    return [branch for branch in re.findall(r"\S+", git_branch_output) if branch != "*"]


def get_main_branch():
    if "MAIN_BRANCH" in os.environ:
        return os.environ["MAIN_BRANCH"]

    branches = get_branches()
    for variant in ["master", "main"]:
        if variant in branches:
            return variant

    raise Exception("Couldn't find main branch")


def get_tags():
    return filter_true(execute_command("git tag --points-at HEAD").split("\n"))


def get_image_names_by_alias():
    # - Assert required environment variables

    _required_envs = ["REGISTRY", "APP"]
    assert all(key in os.environ for key in _required_envs), f"Missing one of environment variables: {_required_envs}"

    # - Get git info

    main_branch = get_main_branch()
    current_branch = get_current_branch()
    short_sha = get_commit_short_sha()
    tags = get_tags()
    image_prefix = f"{os.environ['REGISTRY']}/{os.environ['APP']}"

    # - Set image names for main branch or custom branch

    image_names_by_alias = {}
    if main_branch == current_branch:
        image_names_by_alias["image_name_by_commit"] = f"{image_prefix}:main-{short_sha}"
        image_names_by_alias["image_name_latest"] = f"{image_prefix}:latest"
    else:
        # custom branch
        image_names_by_alias["image_name_by_commit"] = f"{image_prefix}:branch-{current_branch}-{short_sha}"
        image_names_by_alias["image_name_branch_latest"] = f"{image_prefix}:branch-{current_branch}"

    # - Set image name for tag

    if tags:
        assert len(tags) == 1, f"Expected only one tag, got {tags}"
        tag = tags[0]
        image_names_by_alias["image_name_tag"] = f"{image_prefix}:{tag}"

    return image_names_by_alias


def export_image_names_envs():
    print(
        "{}".format(
            " ".join([f"{alias.upper()}={image_name}" for alias, image_name in get_image_names_by_alias().items()])
        )
    )


def example():
    os.environ["REGISTRY"] = "localhost"
    os.environ["APP"] = "data-etl-python"

    export_image_names_envs()


if __name__ == "__main__":
    example()
    # export_docker_image_names()
