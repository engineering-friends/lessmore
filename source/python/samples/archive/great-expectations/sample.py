import great_expectations as gx


context = gx.get_context()

validator = context.sources.pandas_default.read_csv(
    "https://raw.githubusercontent.com/great-expectations/gx_tutorials/main/data/yellow_tripdata_sample_2019-01.csv"
)

validator.expect_column_values_to_not_be_null("pickup_datetime")
validator.expect_column_values_to_be_between("passenger_count", auto=True)

checkpoint = gx.checkpoint.SimpleCheckpoint(
    name="my_quickstart_checkpoint",
    data_context=context,
    validator=validator,
)

checkpoint_result = checkpoint.run()

validation_result_identifier = checkpoint_result.list_validation_result_identifiers()[0]
context.open_data_docs(resource_identifier=validation_result_identifier)
