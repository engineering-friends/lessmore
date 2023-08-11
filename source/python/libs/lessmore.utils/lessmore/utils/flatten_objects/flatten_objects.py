# todo later: move to unified_dict [@marklidenberg]


def flatten_objects(value):
    """{"b": [{"foo": 1, "bar": 3}, {"foo": 2, "bar": 4}], "a": 1} -> {"a": 1, "b.foo": [1, 2], "b.bar": [3, 4]} ->"""
    res = {}
    for k, v in value.items():
        if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):

            # - Collect all keys for objects (["foo", "bar"])

            objects = v
            keys_set = set(sum([list(object.keys()) for object in objects], []))

            # - Get sample object

            sample_object = objects[0]

            # - Set flattened values

            if len(v) == 1 and sample_object.get("stub"):

                # 'c'
                for object_key in keys_set:
                    if object_key == "stub":
                        continue
                    res[k + "." + object_key] = []
            else:

                # 'b'
                for object_key in keys_set:
                    res[k + "." + object_key] = [object.get(object_key) for object in objects]
        else:

            # 'a'
            res[k] = v

    return res



def test():
    flattened = {"a": 1, "b.foo": [1, 2], "b.bar": [3, 4], "c.a": [], "c.b": []}
    unflattened = {"b": [{"foo": 1, "bar": 3}, {"foo": 2, "bar": 4}], "a": 1, "c": [{"a": "", "b": "", "stub": True}]}
    assert flatten_objects(unflattened) == flattened


if __name__ == "__main__":
    test()
