import sys

import pytest


def pytest_report_teststatus(report):
    """
    Override the default test status reporting to prevent any output.
    """
    if report.passed and report.when == "call":
        return ("Passed", None, None)


@pytest.hookimpl(tryfirst=True)
def pytest_exception_interact(node, call, report):
    if report.failed:
        print("\n", call.excinfo.getrepr(style="native"), file=sys.stderr)


def pytest_sessionstart(session):
    # - Get terminal reporter

    terminal_reporter = session.config.pluginmanager.getplugin("terminalreporter")

    # - Monkey patch the write method of the terminal reporter to prevent any output

    original_write = terminal_reporter._tw.write

    def custom_write(s, **kwargs):
        # leave only last line of the test summary
        if "::" in s and not s.startswith("FAILED"):
            original_write("-" * 80 + "\n[" + s.strip() + "]\n", **kwargs)
        elif " in " in s:
            original_write("-" * 80 + "\n")
            original_write(s.replace("=", "").strip(), **kwargs)  # 1 failed, 1 warning, 1 Passed in 0.04s

    terminal_reporter._tw.write = custom_write
