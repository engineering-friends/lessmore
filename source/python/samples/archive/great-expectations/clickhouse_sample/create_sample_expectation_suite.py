import os

import great_expectations as gx

from clickhouse_sample.great_expectations.plugins.expectations.expect_expected import ExpectExpected
from great_expectations.core.batch import BatchRequest


def create_sample_expectation_suite():
    # - Init context

    data_context = gx.get_context()

    # - Create batch request for data asset

    batch_request = BatchRequest(
        datasource_name="clickhouse.draft.case_param",
        data_connector_name="connector_CASDC",
        data_asset_name="case_param",
    )

    # - Init expectation suite

    data_context.add_or_update_expectation_suite(expectation_suite_name="clickhouse.draft.case_param.suite")

    # - Get validator and add expectation

    validator = data_context.get_validator(
        batch_request=batch_request,
        expectation_suite_name="clickhouse.draft.case_param.suite",
    )
    validator.expect_expected(is_alert=False)

    # - Update expectation suite

    validator.save_expectation_suite(discard_failed_expectations=False)

    # - Check that expectation suite was added

    print(os.system("great_expectations suite list"))


if __name__ == "__main__":
    create_sample_expectation_suite()
