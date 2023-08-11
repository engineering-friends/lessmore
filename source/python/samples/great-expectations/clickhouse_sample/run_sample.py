import os
import sys

from clickhouse_sample.create_sample_checkpoint import create_sample_checkpoint
from clickhouse_sample.create_sample_data_source import create_sample_data_source
from clickhouse_sample.create_sample_expectation_suite import create_sample_expectation_suite
from clickhouse_sample.test_connection import test_connection


# init great expectations

os.system("great_expectations init")
os.system("cp expect_expected.py great_expectations/plugins/expectations/expect_expected.py")

test_connection()
create_sample_data_source()
create_sample_expectation_suite()
create_sample_checkpoint()
