import os


def get_file_type(filename):
    if "Dockerfile" in filename:
        return "Dockerfile"
    else:
        return os.path.splitext(filename)[-1]


type_config = {
    "py-like": {
        "file_types": [".py"],
        "wise_comments_config": {"single_comments": ("#",), "multi_comments": [('"""', '"""'), ("'''", "'''")]},
    },
    "c-like": {
        "file_types": [".c", ".cpp", ".go"],
        "wise_comments_config": {"single_comments": ("//",), "multi_comments": [("/*", "*/")]},
    },
    "bash-like": {
        "file_types": ["Dockerfile", ".sh"],
        "wise_comments_config": {"single_comments": ("#",)},
    },
}
