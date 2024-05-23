# this util provides a simple way to save and load inputs for batch testing
import json
import os
import traceback

from tqdm import tqdm

from lessmore.utils.legacy.json_utils import read_jsons, to_json, write_jsons


class BatchTestsRunner:
    def __init__(self, formatter=None, errors_validator=None, is_raise=True):
        self.formatter = formatter
        self.errors_validator = errors_validator
        self.is_raise = is_raise

    # todo later: refactor, save_inputs -> write [@marklidenberg]
    def save_inputs(self, filename, inputs, outputs=None):
        # - Preprocess arguments

        if isinstance(inputs, str):
            inputs = read_jsons(inputs)
        outputs = outputs or ["" for _ in range(len(inputs))]

        assert len(inputs) == len(outputs), "inputs and outputs must have the same length"

        # - Write jsons

        write_jsons(
            filename, [{"input": input_, "output": output} for input_, output in zip(inputs, outputs)], default=str
        )

    def safe_run(self, function, *args, **kwargs):
        try:
            formatter = self.formatter or (lambda x: x)
            return formatter(function(*args, **kwargs))
        except Exception as e:
            if self.errors_validator and self.errors_validator(e):
                return {"error": str(e)}
            else:
                raise

    def run(self, filename, function, is_force_update=False, inputs=None):
        if inputs and (not os.path.exists(filename) or is_force_update):
            self.save_inputs(filename, inputs)

        values = read_jsons(filename)

        if any(value["output"] for value in values) and not is_force_update:
            self.run_batch_test(filename, function)
        else:
            self.update_outputs(filename, function)
        values = read_jsons(filename)

        return values

    def update_outputs(self, filename, function):
        values = read_jsons(filename)
        for i, value in tqdm(enumerate(values)):
            value["input"] = json.loads(value["input"]) if isinstance(value["input"], str) else value["input"]
            res = self.safe_run(function, **value["input"])
            value["output"] = res
        write_jsons(filename, values, default=str)

    def run_batch_test(self, filename, function):
        old_output_formatter = self.formatter or (lambda x: x)
        values = read_jsons(filename)

        counter = 0
        for value in tqdm(values):
            old_output = old_output_formatter(value["output"])
            new_output = None
            try:
                new_output = self.safe_run(function, **value["input"])
            except Exception as e:
                print("EXCEPTION")
                print(counter)
                print(value["input"])
                print(traceback.format_exc())
                print("---" * 20)

                if self.is_raise:
                    raise

            try:
                assert to_json(old_output) == to_json(new_output)
            except:
                counter += 1
                print(counter)
                print("Input data:")
                print(to_json(value["input"]))
                print("Before:")
                print(to_json(old_output))
                print(" After:")
                print(to_json(new_output))
                print("---" * 20)

                print("Compare results at http://text.num2word.ru/ or other service")

                if self.is_raise:
                    raise

            if counter > 10:
                raise Exception("Too many errors")
        if counter > 0:
            raise Exception("Some of the regression tests failed")


def run_batch_tests(inputs_and_outputs, function, is_force_update=False, **kwargs):
    runner = BatchTestsRunner(**kwargs)
    if isinstance(inputs_and_outputs, list):
        inputs, outputs = inputs_and_outputs
    else:
        inputs, outputs = None, inputs_and_outputs

    return runner.run(filename=outputs, function=function, inputs=inputs, is_force_update=is_force_update)


if __name__ == "__main__":
    test = BatchTestsRunner()
    test.save_inputs("asdf.csv", [{"a": 1}, {"a": 2}, {"a": 3}])

    print(read_jsons("asdf.csv"))
    test.update_outputs("asdf.csv", lambda a: 1)
    print(read_jsons("asdf.csv"))

    test.run_batch_test("asdf.csv", lambda a: 1)
    try:
        test.run_batch_test("asdf.csv", lambda a: 2)
        raise Exception("Should not happen")
    except AssertionError:
        print("AssertionError")
