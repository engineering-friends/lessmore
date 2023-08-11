import os

import great_expectations as gx

from clickhouse_sample.clickhouse_connection_string import clickhouse_connection_string


def create_sample_data_source():
    # - Init data context

    data_context = gx.get_context()

    # - Add datasource

    data_context.add_datasource(
        **{
            "name": f"clickhouse.draft.case_param",
            "class_name": "Datasource",
            "module_name": "great_expectations.datasource",
            "execution_engine": {
                "class_name": "SqlAlchemyExecutionEngine",
                "module_name": "great_expectations.execution_engine",
                "connection_string": clickhouse_connection_string,
                "create_temp_table": False,
            },
            "data_connectors": {
                "connector_CASDC": {
                    "class_name": "ConfiguredAssetSqlDataConnector",
                    "assets": {
                        "case_param": {
                            "table_name": "case_param",
                            "schema_name": "draft",
                        },
                    },
                },
            },
        }
    )

    # - Check that datasource was added

    print(os.system("great_expectations datasource list"))
    """1 block config Datasource found:
    
     - name: clickhouse.draft.case_param
       class_name: Datasource
    """


if __name__ == "__main__":
    create_sample_data_source()
