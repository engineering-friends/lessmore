# - Create generic sql data_check

from datetime import datetime, timedelta

from lessmore.utils.sql_builder.add_suffix_and_prefix_to_aliases import add_suffix_and_prefix_to_aliases
from lessmore.utils.sql_builder.variables.create_constant_sql import create_constant_sql
from lessmore.utils.sql_builder.variables.create_time_aggregation_sql import create_time_aggregation_sql
from lessmore.utils.sql_builder.wrap_variable_sql import wrap_variable_sql


def create_generic_sql(variables_by_name, output, output_name="output"):
    # - Preprocess variables

    # add variable name to sql (0.8 -> 0.8 AS my_variable)
    variables_by_name = {
        name: wrap_variable_sql(sql=variable, name=name) for name, variable in variables_by_name.items()
    }

    # add suffix to all aliases (alias -> alias_my_variable)
    variables_by_name = {
        name: add_suffix_and_prefix_to_aliases(variable, suffix=f"{i}")
        for i, (name, variable) in enumerate(variables_by_name.items())
    }

    # add comma to all aliases for enforcing new lines in sql formatting (alias, -> alias, --)
    variables_by_name = {name: f"{variable}, --" for name, variable in variables_by_name.items()}

    # - Return sql

    return """
    WITH
          {variables}

          -- Evaluating output 

          {output} AS {output_name}

    SELECT
        {variable_names},
        {output_name}
    """.format(
        variables="\n".join([f"\n-- Evaluating {name}\n\n{variable}" for name, variable in variables_by_name.items()]),
        output=output,
        variable_names=",\n".join(variables_by_name.keys()),
        output_name=output_name,
    )


def test():
    import pyperclip

    print(
        create_generic_sql(
            variables_by_name={
                "threshold": create_constant_sql(value=0.8),
                "v1": create_time_aggregation_sql(
                    now=datetime.now(),
                    table="orrr.games",
                    aggregation="count(*)",
                    divide_by_days_in_period=True,
                    timestamp_column="StartedDateTime",
                    period_days=1,
                ),
                "v2": create_time_aggregation_sql(
                    now=datetime.now(),
                    table="orrr.games",
                    aggregation="count(*)",
                    divide_by_days_in_period=True,
                    timestamp_column="StartedDateTime",
                    period_days=7,
                    stop_at_last_timestamp=True,
                ),
            },
            output="v1 < threshold * v2",
            output_name="is_alert",
        )
    )


if __name__ == "__main__":
    test()
