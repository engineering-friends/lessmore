import os

import great_expectations as gx

from clickhouse_sample.great_expectations.plugins.expectations.expect_expected import ExpectExpected
from great_expectations.core.yaml_handler import YAMLHandler


def create_sample_checkpoint():
    # - Init data context

    data_context = gx.get_context()

    # - Add checkpoint

    data_context.add_or_update_checkpoint(
        **YAMLHandler().load(
            f"""
    name: clickhouse.draft.case_param.checkpoint
    config_version: 1
    class_name: Checkpoint
    validations:
      - batch_request:
          datasource_name: clickhouse.draft.case_param
          data_connector_name: connector_CASDC
          data_asset_name: case_param
        expectation_suite_name: clickhouse.draft.case_param.suite
        action_list:
          - name: store_validation_result
            action:
              class_name: StoreValidationResultAction
          - name: store_evaluation_params
            action:
              class_name: StoreEvaluationParametersAction
          - name: update_data_docs
            action:
              class_name: UpdateDataDocsAction
          - name: datahub_action
            action:
              module_name: datahub.integrations.great_expectations.action
              class_name: DataHubValidationAction
              server_url: https://gms.datahub.data.deeplay.io
              env: PROD
              graceful_exceptions: false
              convert_urns_to_lowercase: true
              token: <token>    """
        )
    )

    # - Run checkpoint

    data_context.run_checkpoint(checkpoint_name=f"clickhouse.draft.case_param.checkpoint")

    # - Check that checkpoint was added

    print(os.system("great_expectations checkpoint list"))


if __name__ == "__main__":
    create_sample_checkpoint()
