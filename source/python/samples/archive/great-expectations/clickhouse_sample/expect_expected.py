"""
This is a template for creating custom QueryExpectations.
For detailed instructions on how to use it, please see:
    https://docs.greatexpectations.io/docs/guides/expectations/creating_custom_expectations/how_to_create_custom_query_expectations
"""


from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from great_expectations.core.expectation_configuration import ExpectationConfiguration
from great_expectations.core.metric_domain_types import MetricDomainTypes
from great_expectations.core.util import convert_to_json_serializable
from great_expectations.execution_engine import ExecutionEngine, SparkDFExecutionEngine, SqlAlchemyExecutionEngine
from great_expectations.expectations.expectation import (
    ExpectationValidationResult,
    QueryExpectation,
    render_evaluation_parameter_string,
)
from great_expectations.expectations.metrics.metric_provider import metric_value
from great_expectations.expectations.metrics.query_metric_provider import QueryMetricProvider


class StubMetric(QueryMetricProvider):
    metric_name = "query.stub_metric"
    value_keys = ("query",)

    # <snippet>
    @metric_value(engine=SqlAlchemyExecutionEngine)
    def _sqlalchemy(  # noqa: PLR0913
        cls,
        execution_engine: SqlAlchemyExecutionEngine,
        metric_domain_kwargs: dict,
        metric_value_kwargs: dict,
        metrics: Dict[str, Any],
        runtime_configuration: dict,
    ) -> List[dict]:
        return []

    @metric_value(engine=SparkDFExecutionEngine)
    def _spark(  # noqa: PLR0913
        cls,
        execution_engine: SparkDFExecutionEngine,
        metric_domain_kwargs: dict,
        metric_value_kwargs: dict,
        metrics: Dict[str, Any],
        runtime_configuration: dict,
    ) -> List[dict]:
        return []


class ExpectExpected(QueryExpectation):
    """A stub expectation. It will return True/False as an argument along with input metrics in dictionary."""

    # - No builtin metrics are used for this expectation

    metric_dependencies = ("query.stub_metric",)  # no request will be made

    # - Stub query to be executed

    query = """ SELECT 1 """

    # - List of parameters that affect the expectation evaluation

    success_keys = ("is_alert", "query")

    domain_keys = ("batch_id", "row_condition", "condition_parser")

    # - Create default values for needed parameters

    default_kwarg_values = {
        "result_format": "BASIC",
        "include_config": True,
        "catch_exceptions": False,
        "meta": None,
        "query": query,
    }

    def validate_configuration(self, configuration: Optional[ExpectationConfiguration]) -> None:
        super().validate_configuration(configuration)
        configuration = configuration or self.configuration

        assert "is_alert" in configuration["kwargs"], "Must provide is_alert"

    def _validate(
        self,
        configuration: ExpectationConfiguration,
        metrics: dict,
        runtime_configuration: dict = None,
        execution_engine: ExecutionEngine = None,
    ) -> Union[ExpectationValidationResult, dict]:
        return {
            "success": not configuration["kwargs"]["is_alert"],
            "result": {"observed_value": 1000, "some_other_value": 2000},
        }

    # - Add examples

    examples = [
        {
            "data": [
                {
                    "data": {
                        "col1": [1, 2, 2, 3, 4],
                        "col2": ["a", "a", "b", "b", "a"],
                    },
                },
            ],
            "tests": [
                {
                    "title": "basic_positive_test",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"is_alert": False},
                    "out": {"success": True},
                },
            ],
        },
    ]

    # - Add library metadata

    library_metadata = {
        "tags": [],
        "contributors": [
            "@marklidenberg",
        ],
    }


if __name__ == "__main__":
    # ExpectExpected().print_diagnostic_checklist()
    ExpectExpected().run_diagnostics()
