# -*- coding:utf-8 -*-
import datetime

import pytest

from google.protobuf.descriptor import FieldDescriptor

from lessmore.utils.protobuf_to_dict import (
    FieldsMissing,
    datetime_to_timestamp,
    dict_to_protobuf,
    get_field_names_and_options,
    protobuf_to_dict,
    timestamp_to_datetime,
    validate_dict_for_required_pb_fields,
)
from lessmore.utils.protobuf_to_dict.tests import sample_pb2
from lessmore.utils.protobuf_to_dict.tests.sample_pb2 import MessageOfTypes


sample_datetime = datetime.datetime.strptime("2011-01-21 02:37:21", "%Y-%m-%d %H:%M:%S")


class TestProtoConvertor:
    def test_basics(self):
        m = self.populate_MessageOfTypes()
        d = protobuf_to_dict(m)
        self.compare(m, d, ["nestedRepeated", "nestedMap"])

        m2 = dict_to_protobuf(MessageOfTypes, d)
        assert m == m2

    def test_use_enum_labels(self):
        m = self.populate_MessageOfTypes()
        d = protobuf_to_dict(m, use_enum_labels=True)
        self.compare(m, d, ["enm", "enmRepeated", "nestedRepeated", "nestedMap"])
        assert d["enm"] == "C"
        assert d["enmRepeated"] == ["A", "C"]

        m2 = dict_to_protobuf(MessageOfTypes, d)
        assert m == m2

        d["enm"] = "MEOW"
        with pytest.raises(KeyError):
            dict_to_protobuf(MessageOfTypes, d)

        d["enm"] = "A"
        d["enmRepeated"] = ["B"]
        dict_to_protobuf(MessageOfTypes, d)

        d["enmRepeated"] = ["CAT"]
        with pytest.raises(KeyError):
            dict_to_protobuf(MessageOfTypes, d)

    def test_lowercase_enum_labels_work(self):
        m = self.populate_MessageOfTypes()
        d = protobuf_to_dict(m, use_enum_labels=True, lowercase_enum_labels=True)
        self.compare(m, d, ["enm", "enmRepeated", "nestedRepeated", "nestedMap"])
        assert d["enm"] == "c"
        assert d["enmRepeated"] == ["a", "c"]

        d["enm"] = "meow"
        d["enm"] = "a"
        d["enmRepeated"] = ["a", "c"]

        with pytest.raises(KeyError):
            dict_to_protobuf(MessageOfTypes, d)

        dict_to_protobuf(MessageOfTypes, d, strict=False)

    def test_repeated_enum(self):
        m = self.populate_MessageOfTypes()
        d = protobuf_to_dict(m, use_enum_labels=True)
        self.compare(m, d, ["enm", "enmRepeated", "nestedRepeated", "nestedMap"])
        assert d["enmRepeated"] == ["A", "C"]

        m2 = dict_to_protobuf(MessageOfTypes, d)
        assert m == m2

        d["enmRepeated"] = ["MEOW"]
        with pytest.raises(KeyError):
            dict_to_protobuf(MessageOfTypes, d)

    def test_nested_repeated(self):
        m = self.populate_MessageOfTypes()
        m.nestedRepeated.extend([MessageOfTypes.NestedType(req=str(i)) for i in range(10)])

        d = protobuf_to_dict(m)
        self.compare(m, d, exclude=["nestedRepeated", "nestedMap"])
        assert d["nestedRepeated"] == [{"req": str(i)} for i in range(10)]

        m2 = dict_to_protobuf(MessageOfTypes, d)
        assert m == m2

    def test_reverse(self):
        m = self.populate_MessageOfTypes()
        m2 = dict_to_protobuf(MessageOfTypes, protobuf_to_dict(m))
        assert m == m2
        m2.dubl = 0
        assert m2 != m

    def test_incomplete(self):
        m = self.populate_MessageOfTypes()
        d = protobuf_to_dict(m)
        d.pop("dubl")
        m2 = dict_to_protobuf(MessageOfTypes, d)
        assert m2.dubl == 0
        assert m != m2

    def test_pass_instance(self):
        m = self.populate_MessageOfTypes()
        d = protobuf_to_dict(m)
        d["dubl"] = 1
        m2 = dict_to_protobuf(m, d)
        assert m is m2
        assert m.dubl == 1

    def test_strict(self):
        m = self.populate_MessageOfTypes()
        d = protobuf_to_dict(m)
        d["meow"] = 1
        with pytest.raises(KeyError):
            m2 = dict_to_protobuf(MessageOfTypes, d)
        m2 = dict_to_protobuf(MessageOfTypes, d, strict=False)
        assert m == m2

    def test_nested_map(self):
        m = self.populate_MessageOfTypes()

        for i in range(10):
            m.nestedMap[str(i)].req = str(i**2)

        d = protobuf_to_dict(m)
        self.compare(m, d, exclude=["nestedRepeated", "nestedMap"])
        assert d["nestedMap"] == {str(i): {"req": str(i**2)} for i in range(10)}

        m2 = dict_to_protobuf(MessageOfTypes, d)
        assert m == m2

    def test_including_default_value_fields(self):
        m = MessageOfTypes()
        d = protobuf_to_dict(m)
        assert d == {}

        d = protobuf_to_dict(m, including_default_value_fields=True)
        expected_default_dict = {
            "dubl": 0.0,
            "flot": 0.0,
            "i32": 0,
            "i64": 0,
            "ui32": 0,
            "ui64": 0,
            "si32": 0,
            "si64": 0,
            "f32": 0,
            "f64": 0,
            "sf32": 0,
            "sf64": 0,
            "bol": False,
            "strng": "",
            "byts": b"",
            "nested": {"req": ""},
            "enm": 0,
            "nestedRepeated": [],
            "enmRepeated": [],
            "simpleMap": {},
            "nestedMap": {},
            "intMap": {},
        }
        assert d == expected_default_dict

        m2 = dict_to_protobuf(MessageOfTypes, d)
        assert m == m2

    def test_ignore_none(self):
        m = MessageOfTypes()
        d = protobuf_to_dict(m)
        assert d == {}

        for field in m.DESCRIPTOR.fields:
            d[field.name] = None

        m2 = dict_to_protobuf(MessageOfTypes, d, ignore_none=True)
        assert m == m2

    def test_nested_ignore_none(self):
        m = MessageOfTypes()
        m.nestedMap["123"].req = "42"

        d = protobuf_to_dict(m)
        d["nestedMap"]["123"]["req"] = None

        m2 = dict_to_protobuf(MessageOfTypes, d, ignore_none=True)
        assert m2.nestedMap["123"].req == ""

    def test_type_callable_map_used_for_maps(self):
        # we give a string key and value and ensure they get run through int()
        d = {}
        d["intMap"] = {}
        d["intMap"]["123"] = "456"

        type_callable_map = {FieldDescriptor.TYPE_INT32: int}
        m = dict_to_protobuf(MessageOfTypes, d, type_callable_map)

        assert m.intMap[123] == 456

    def populate_MessageOfTypes(self):  # NOQA
        m = MessageOfTypes()
        m.dubl = 1.7e308
        m.flot = 3.4e038
        m.i32 = 2**31 - 1  # 2147483647 #
        m.i64 = 2**63 - 1  # 0x7FFFFFFFFFFFFFFF
        m.ui32 = 2**32 - 1
        m.ui64 = 2**64 - 1
        m.si32 = -1 * m.i32
        m.si64 = -1 * m.i64
        m.f32 = m.i32
        m.f64 = m.i64
        m.sf32 = m.si32
        m.sf64 = m.si64
        m.bol = True
        m.strng = "string"
        m.byts = b"\n\x14\x1e"
        assert len(m.byts) == 3, len(m.byts)
        m.nested.req = "req"
        m.enm = MessageOfTypes.C  # @UndefinedVariable
        m.enmRepeated.extend([MessageOfTypes.A, MessageOfTypes.C])
        m.simpleMap["s1"] = 4.2
        m.simpleMap["s2"] = 42.0
        m.intMap[123] = 456
        return m

    def compare(self, m, d, exclude=None):
        i = 0
        exclude = ["byts", "nested"] + (exclude or [])
        for i, field in enumerate(MessageOfTypes.DESCRIPTOR.fields):  # @UndefinedVariable
            if field.name not in exclude:
                assert field.name in d, field.name
                assert d[field.name] == getattr(m, field.name), (field.name, d[field.name])
        assert i > 0
        assert m.byts == d["byts"]
        assert d["nested"] == {"req": m.nested.req}


class TestDateTime:
    def test_datetime_to_timestamp_and_back(self):
        timestamp = datetime_to_timestamp(sample_datetime)
        result_sample_datetime = timestamp_to_datetime(timestamp)
        assert sample_datetime == result_sample_datetime

    def test_pb_convert_to_dict_with_datetime_and_back(self):
        now = datetime.datetime.utcnow()
        timestamp = datetime_to_timestamp(now)
        obj1 = sample_pb2.Obj(item_id="item id", transacted_at=timestamp)

        pb_dict = protobuf_to_dict(obj1)
        assert pb_dict["transacted_at"] == now

        obj1_again = dict_to_protobuf(sample_pb2.Obj, values=pb_dict)
        assert obj1 == obj1_again

    def test_dict_to_protobuf_with_param_use_date_parser_for_fields(self):
        dt = datetime.datetime.utcnow() - datetime.timedelta(days=365)
        dt_iso_str = dt.isoformat()
        ts = datetime_to_timestamp(dt)

        obj = sample_pb2.Obj(item_id="item id", transacted_at=ts, status=sample_pb2.Status.OK)
        dict_obj = {"item_id": "item id", "transacted_at": dt_iso_str, "status": 0}

        obj_again = dict_to_protobuf(sample_pb2.Obj, values=dict_obj, use_date_parser_for_fields=["transacted_at"])
        assert obj == obj_again


class TestOptions:
    def test_get_field_name_and_options(self):
        for field, field_name, field_options in get_field_names_and_options(sample_pb2.Obj):
            if field_name == "id":
                assert field_options == {"is_optional": True}

    @pytest.mark.parametrize(
        "test_input",
        [
            {"id": 1, "item_id": 2, "transacted_at": datetime.datetime.now(), "status": 0},
            {"item_id": 2, "transacted_at": datetime.datetime.now(), "status": 0},
        ],
    )
    def test_validate_dict_for_required_pb_fields_has_all_required_fields(self, test_input):
        validate_dict_for_required_pb_fields(pb=sample_pb2.Obj, dic=test_input)

    def test_validate_dict_for_required_pb_fields_has_missing_required_fields(self):
        dic = {"id": 1, "item_id": 2}
        with pytest.raises(FieldsMissing) as e:
            validate_dict_for_required_pb_fields(pb=sample_pb2.Obj, dic=dic)

        assert str(e.value) == "Missing fields: transacted_at, status"


if __name__ == "__main__":
    pytest.main()
