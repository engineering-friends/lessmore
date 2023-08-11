from lessmore.flatten_objects.flatten_objects import flatten_objects


def unflatten_objects(value, validate_length=False):
    """{"a": 1, "b.foo": [1, 2], "b.bar": [3, 4]} ->  {"b": [{"foo": 1, "bar": 3}, {"foo": 2, "bar": 4}], "a": 1}"""
    res = {}

    # find object keys
    object_names = {k.split(".")[0] for k in value.keys() if "." in k}  # ['b']
    non_object_keys = [k for k in value.keys() if "." not in k]  # ['a']

    for object_name in object_names:
        res[object_name] = []
        object_keys = [k for k in value.keys() if k.startswith(object_name + ".")]  # ['b.foo', 'b.bar']
        sample_object_key = object_keys[0]  # 'b.foo'

        n_objects = len(value[sample_object_key])

        if validate_length:
            for object_key in object_keys:
                assert len(value[object_key]) == n_objects, "Different flatten lengths"

        if n_objects == 0:
            obj = {"stub": True}
            for object_key in object_keys:
                obj[object_key.split(".")[1]] = ""

            res[object_name].append(obj)
        else:
            for i in range(len(value[sample_object_key])):  # range(2)
                obj = {}
                for object_key in object_keys:
                    obj[object_key.split(".")[1]] = value[object_key][i]
                res[object_name].append(obj)

    for non_object_key in non_object_keys:
        res[non_object_key] = value[non_object_key]

    for k, v in dict(res).items():
        if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
            res[k] = [{k_ if k_ != "stub" else "stub": v_ for k_, v_ in x.items()} for x in v]

    return res


def test():
    flattened = {"a": 1, "b.foo": [1, 2], "b.bar": [3, 4], "c.a": [], "c.b": []}
    unflattened = {"b": [{"foo": 1, "bar": 3}, {"foo": 2, "bar": 4}], "a": 1, "c": [{"a": "", "b": "", "stub": True}]}

    assert unflatten_objects(flattened) == unflattened

    flattened_error_length = {"a": 1, "b.foo": [1, 2, 3], "b.bar": [3, 4], "c.a": [], "c.b": []}
    try:
        unflatten_objects(flattened_error_length, validate_length=True)
    except AssertionError as e:
        assert str(e) == "Different flatten lengths"


if __name__ == "__main__":
    test()
