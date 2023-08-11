"""
This is a template for creating custom QueryExpectations.
For detailed instructions on how to use it, please see:
    https://docs.greatexpectations.io/docs/guides/expectations/creating_custom_expectations/how_to_create_custom_query_expectations
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from great_expectations.core import ExpectationConfiguration  # noqa: TCH001
from great_expectations.core import ExpectationValidationResult  # noqa: TCH001
from great_expectations.core._docs_decorators import public_api
from great_expectations.core.expectation_configuration import ExpectationConfiguration
from great_expectations.core.metric_domain_types import MetricDomainTypes
from great_expectations.core.util import convert_to_json_serializable
from great_expectations.execution_engine import ExecutionEngine  # noqa: TCH001
from great_expectations.execution_engine import SparkDFExecutionEngine, SqlAlchemyExecutionEngine
from great_expectations.expectations.expectation import (
    ExpectationValidationResult,
    InvalidExpectationConfigurationError,
    QueryExpectation,
    TableExpectation,
    render_evaluation_parameter_string,
)
from great_expectations.expectations.metrics.metric_provider import metric_value
from great_expectations.expectations.metrics.query_metric_provider import QueryMetricProvider
from great_expectations.render import LegacyRendererType, RenderedStringTemplateContent
from great_expectations.render.renderer.renderer import renderer
from great_expectations.render.renderer_configuration import RendererConfiguration, RendererValueType
from great_expectations.render.util import substitute_none_for_missing


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
        print("123")
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
        """
        Validates that a configuration has been set, and sets a configuration if it has yet to be set. Ensures that
        necessary configuration arguments have been provided for the validation of the expectation.

        Args:
            configuration (OPTIONAL[ExpectationConfiguration]): \
                An optional Expectation Configuration entry that will be used to configure the expectation
        Returns:
            None. Raises InvalidExpectationConfigurationError if the config is not validated successfully
        """
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
                    "in": {"is_alert": False, "custom_metrics": {"metric1": 1, "metric2": 2}},
                    "out": {"success": True},
                },
            ],
        },
    ]

    # - Add custom name

    @classmethod
    def _prescriptive_template(
        cls,
        renderer_configuration: RendererConfiguration,
    ) -> RendererConfiguration:
        renderer_configuration.template_str = "Must have exactly rows."
        return renderer_configuration

    @classmethod
    @renderer(renderer_type=LegacyRendererType.PRESCRIPTIVE)
    @render_evaluation_parameter_string
    def _prescriptive_renderer(
        cls,
        configuration: Optional[ExpectationConfiguration] = None,
        result: Optional[ExpectationValidationResult] = None,
        runtime_configuration: Optional[dict] = None,
    ) -> List[RenderedStringTemplateContent]:
        renderer_configuration: RendererConfiguration = RendererConfiguration(
            configuration=configuration,
            result=result,
            runtime_configuration=runtime_configuration,
        )
        template_str = "Must have exactly rows."

        styling = runtime_configuration.get("styling", {}) if runtime_configuration else {}

        return [
            RenderedStringTemplateContent(
                **{  # type: ignore[arg-type]
                    "content_block_type": "string_template",
                    "string_template": {
                        "template": template_str,
                        "styling": styling,
                    },
                }
            )
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
