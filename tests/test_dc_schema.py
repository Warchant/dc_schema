from __future__ import annotations

import dataclasses
import datetime  # noqa: TCH003
import enum
import typing as t

import jsonschema
import pytest
from jsonschema.validators import Draft202012Validator

from dc_schema import (
    SchemaAnnotation,
    get_schema,
)


@dataclasses.dataclass
class DcPrimitives:
    b: bool
    i: int
    f: float
    s: str


def test_get_schema_primitives():
    schema = get_schema(DcPrimitives)
    print(schema)
    Draft202012Validator.check_schema(schema)
    assert schema == {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "title": "DcPrimitives",
        "properties": {
            "b": {"type": "boolean"},
            "i": {"type": "integer"},
            "f": {"type": "number"},
            "s": {"type": "string"},
        },
        "required": ["b", "i", "f", "s"],
    }


@dataclasses.dataclass
class DcOptional:
    a: int = 42
    b: int = dataclasses.field(default=42)
    c: int = dataclasses.field(default_factory=lambda: 42)
    d: str = "foo"
    e: bool = False
    f: None = None
    g: float = 1.1
    h: tuple[int, float] = (1, 1.1)


def test_get_schema_optional_fields():
    """optional field === field with a default (!== t.Optional)"""
    schema = get_schema(DcOptional)
    print(schema)
    Draft202012Validator.check_schema(schema)
    assert schema == {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "title": "DcOptional",
        "properties": {
            "a": {"type": "integer", "default": 42},
            "b": {"type": "integer", "default": 42},
            "c": {"type": "integer"},
            "d": {"type": "string", "default": "foo"},
            "e": {"type": "boolean", "default": False},
            "f": {"type": "null", "default": None},
            "g": {"type": "number", "default": 1.1},
            "h": {
                "type": "array",
                "prefixItems": [{"type": "integer"}, {"type": "number"}],
                "minItems": 2,
                "maxItems": 2,
                "default": [1, 1.1],
            },
        },
    }


@dataclasses.dataclass
class DcUnion:
    a: t.Union[int, str]


def test_get_schema_union():
    schema = get_schema(DcUnion)
    print(schema)
    Draft202012Validator.check_schema(schema)
    assert schema == {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "title": "DcUnion",
        "properties": {"a": {"anyOf": [{"type": "integer"}, {"type": "string"}]}},
        "required": ["a"],
    }


@dataclasses.dataclass
class DcNone:
    a: None
    b: t.Optional[int]
    c: t.Union[None, int]


def test_get_schema_nullable():
    schema = get_schema(DcNone)
    print(schema)
    Draft202012Validator.check_schema(schema)
    assert schema == {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "title": "DcNone",
        "properties": {
            "a": {"type": "null"},
            "b": {"anyOf": [{"type": "integer"}, {"type": "null"}]},
            "c": {"anyOf": [{"type": "null"}, {"type": "integer"}]},
        },
        "required": ["a", "b", "c"],
    }


@dataclasses.dataclass
class DcDict:
    a: dict
    b: dict[str, int]


def test_get_schema_dict():
    schema = get_schema(DcDict)
    print(schema)
    Draft202012Validator.check_schema(schema)
    assert schema == {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "title": "DcDict",
        "properties": {
            "a": {"type": "object"},
            "b": {"type": "object", "additionalProperties": {"type": "integer"}},
        },
        "required": ["a", "b"],
    }


@dataclasses.dataclass
class DcList:
    a: list
    b: list[bool]


def test_get_schema_list():
    schema = get_schema(DcList)
    print(schema)
    Draft202012Validator.check_schema(schema)
    assert schema == {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "title": "DcList",
        "properties": {
            "a": {"type": "array"},
            "b": {"type": "array", "items": {"type": "boolean"}},
        },
        "required": ["a", "b"],
    }


@dataclasses.dataclass
class DcTuple:
    a: tuple
    b: tuple[int, ...]
    c: tuple[int, bool, str]


def test_get_schema_tuple():
    schema = get_schema(DcTuple)
    print(schema)
    Draft202012Validator.check_schema(schema)
    assert schema == {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "title": "DcTuple",
        "properties": {
            "a": {"type": "array"},
            "b": {"type": "array", "items": {"type": "integer"}},
            "c": {
                "type": "array",
                "prefixItems": [
                    {"type": "integer"},
                    {"type": "boolean"},
                    {"type": "string"},
                ],
                "minItems": 3,
                "maxItems": 3,
            },
        },
        "required": ["a", "b", "c"],
    }


@dataclasses.dataclass
class DcRefsChild:
    c: str


@dataclasses.dataclass
class DcRefs:
    a: DcRefsChild
    b: list[DcRefsChild]


def test_get_schema_refs():
    schema = get_schema(DcRefs)
    print(schema)
    Draft202012Validator.check_schema(schema)
    assert schema == {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "title": "DcRefs",
        "properties": {
            "a": {"allOf": [{"$ref": "#/$defs/DcRefsChild"}]},
            "b": {
                "type": "array",
                "items": {"allOf": [{"$ref": "#/$defs/DcRefsChild"}]},
            },
        },
        "required": ["a", "b"],
        "$defs": {
            "DcRefsChild": {
                "type": "object",
                "title": "DcRefsChild",
                "properties": {"c": {"type": "string"}},
                "required": ["c"],
            }
        },
    }


@dataclasses.dataclass
class DcRefsSelf:
    a: str
    b: t.Optional[DcRefsSelf]
    c: list[DcRefsSelf]


def test_get_schema_self_refs():
    schema = get_schema(DcRefsSelf)
    print(schema)
    Draft202012Validator.check_schema(schema)
    assert schema == {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "title": "DcRefsSelf",
        "properties": {
            "a": {"type": "string"},
            "b": {"anyOf": [{"allOf": [{"$ref": "#"}]}, {"type": "null"}]},
            "c": {"type": "array", "items": {"allOf": [{"$ref": "#"}]}},
        },
        "required": ["a", "b", "c"],
    }


@dataclasses.dataclass
class DcLiteral:
    a: t.Literal[1, "two", 3, None]
    b: t.Literal[42, 43] = 42


def test_get_schema_literal():
    schema = get_schema(DcLiteral)
    print(schema)
    Draft202012Validator.check_schema(schema)
    assert schema == {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "title": "DcLiteral",
        "properties": {
            "a": {"enum": [1, "two", 3, None]},
            "b": {"enum": [42, 43], "default": 42},
        },
        "required": ["a"],
    }


class MyEnum(enum.Enum):
    a = enum.auto()
    b = enum.auto()


@dataclasses.dataclass
class DcEnum:
    a: MyEnum
    b: MyEnum = MyEnum.a


def test_get_schema_enum():
    schema = get_schema(DcEnum)
    print(schema)
    Draft202012Validator.check_schema(schema)
    assert schema == {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "title": "DcEnum",
        "properties": {
            "a": {"allOf": [{"$ref": "#/$defs/MyEnum"}]},
            "b": {"allOf": [{"$ref": "#/$defs/MyEnum"}], "default": 1},
        },
        "required": ["a"],
        "$defs": {"MyEnum": {"title": "MyEnum", "enum": [1, 2]}},
    }


@dataclasses.dataclass
class DcSet:
    a: set
    b: set[int]


def test_get_schema_set():
    schema = get_schema(DcSet)
    print(schema)
    Draft202012Validator.check_schema(schema)
    assert schema == {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "title": "DcSet",
        "properties": {
            "a": {"type": "array", "uniqueItems": True},
            "b": {"type": "array", "items": {"type": "integer"}, "uniqueItems": True},
        },
        "required": ["a", "b"],
    }


@dataclasses.dataclass
class DcStrAnnotated:
    a: t.Annotated[str, SchemaAnnotation(min_length=3, max_length=5)]
    b: t.Annotated[
        str, SchemaAnnotation(format="date", pattern=r"^\d.*")
    ] = "2000-01-01"


def test_get_schema_str_annotation():
    schema = get_schema(DcStrAnnotated)
    print(schema)
    Draft202012Validator.check_schema(schema)
    assert schema == {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "title": "DcStrAnnotated",
        "properties": {
            "a": {"type": "string", "minLength": 3, "maxLength": 5},
            "b": {
                "type": "string",
                "default": "2000-01-01",
                "pattern": "^\\d.*",
                "format": "date",
            },
        },
        "required": ["a"],
    }


@dataclasses.dataclass
class DcNumberAnnotated:
    a: t.Annotated[int, SchemaAnnotation(minimum=1, exclusive_maximum=11)]
    b: list[t.Annotated[int, SchemaAnnotation(minimum=0)]]
    c: t.Optional[t.Annotated[int, SchemaAnnotation(minimum=0)]]
    d: t.Annotated[
        float, SchemaAnnotation(maximum=12, exclusive_minimum=17, multiple_of=5)
    ] = 33.1


def test_get_schema_number_annotation():
    schema = get_schema(DcNumberAnnotated)
    print(schema)
    Draft202012Validator.check_schema(schema)
    assert schema == {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "title": "DcNumberAnnotated",
        "properties": {
            "a": {"type": "integer", "minimum": 1, "exclusiveMaximum": 11},
            "b": {"type": "array", "items": {"type": "integer", "minimum": 0}},
            "c": {"anyOf": [{"type": "integer", "minimum": 0}, {"type": "null"}]},
            "d": {
                "type": "number",
                "default": 33.1,
                "maximum": 12,
                "exclusiveMinimum": 17,
                "multipleOf": 5,
            },
        },
        "required": ["a", "b", "c"],
    }


@dataclasses.dataclass
class DcDateTime:
    a: datetime.datetime
    b: datetime.date


def test_get_schema_date_time():
    schema = get_schema(DcDateTime)
    print(schema)
    Draft202012Validator.check_schema(schema)
    assert schema == {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "title": "DcDateTime",
        "properties": {
            "a": {"type": "string", "format": "date-time"},
            "b": {"type": "string", "format": "date"},
        },
        "required": ["a", "b"],
    }


@dataclasses.dataclass
class DcAnnotatedBook:
    title: t.Annotated[str, SchemaAnnotation(title="Title")]


class DcAnnotatedAuthorHobby(enum.Enum):
    CHESS = "chess"
    SOCCER = "soccer"


@dataclasses.dataclass
class DcAnnotatedAuthor:
    name: t.Annotated[
        str,
        SchemaAnnotation(
            description="the name of the author", examples=["paul", "alice"]
        ),
    ]
    books: t.Annotated[
        list[DcAnnotatedBook],
        SchemaAnnotation(description="all the books the author has written"),
    ]
    hobby: t.Annotated[DcAnnotatedAuthorHobby, SchemaAnnotation(deprecated=True)]
    age: t.Annotated[
        t.Union[int, float], SchemaAnnotation(description="age in years")
    ] = 42


def test_get_schema_annotation():
    schema = get_schema(DcAnnotatedAuthor)
    print(schema)
    Draft202012Validator.check_schema(schema)
    assert schema == {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "title": "DcAnnotatedAuthor",
        "properties": {
            "name": {
                "type": "string",
                "description": "the name of the author",
                "examples": ["paul", "alice"],
            },
            "books": {
                "type": "array",
                "items": {"allOf": [{"$ref": "#/$defs/DcAnnotatedBook"}]},
                "description": "all the books the author has written",
            },
            "hobby": {
                "allOf": [{"$ref": "#/$defs/DcAnnotatedAuthorHobby"}],
                "deprecated": True,
            },
            "age": {
                "anyOf": [{"type": "integer"}, {"type": "number"}],
                "default": 42,
                "description": "age in years",
            },
        },
        "required": ["name", "books", "hobby"],
        "$defs": {
            "DcAnnotatedBook": {
                "type": "object",
                "title": "DcAnnotatedBook",
                "properties": {"title": {"type": "string", "title": "Title"}},
                "required": ["title"],
            },
            "DcAnnotatedAuthorHobby": {
                "title": "DcAnnotatedAuthorHobby",
                "enum": ["chess", "soccer"],
            },
        },
    }


@dataclasses.dataclass
class DcSchemaConfigChild:
    a: int

    class SchemaConfig:
        annotation = SchemaAnnotation(title="a child")


@dataclasses.dataclass
class DcSchemaConfig:
    a: str
    child_1: DcSchemaConfigChild
    child_2: t.Annotated[DcSchemaConfigChild, SchemaAnnotation(title="2nd child")]
    friend: t.Annotated[DcSchemaConfig, SchemaAnnotation(title="a friend")]

    class SchemaConfig:
        annotation = SchemaAnnotation(title="root model")


def test_get_schema_config():
    schema = get_schema(DcSchemaConfig)
    print(schema)
    Draft202012Validator.check_schema(schema)
    assert schema == {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "title": "root model",
        "properties": {
            "a": {"type": "string"},
            "child_1": {"allOf": [{"$ref": "#/$defs/DcSchemaConfigChild"}]},
            "child_2": {
                "allOf": [{"$ref": "#/$defs/DcSchemaConfigChild"}],
                "title": "2nd child",
            },
            "friend": {"allOf": [{"$ref": "#"}], "title": "a friend"},
        },
        "required": ["a", "child_1", "child_2", "friend"],
        "$defs": {
            "DcSchemaConfigChild": {
                "type": "object",
                "title": "a child",
                "properties": {"a": {"type": "integer"}},
                "required": ["a"],
            }
        },
    }


@dataclasses.dataclass
class DcListAnnotation:
    a: t.Annotated[
        list[int], SchemaAnnotation(min_items=3, max_items=5, unique_items=True)
    ]
    b: t.Annotated[tuple[float, ...], SchemaAnnotation(min_items=3, max_items=10)] = ()


def test_get_schema_list_annotation():
    schema = get_schema(DcListAnnotation)
    print(schema)
    Draft202012Validator.check_schema(schema)
    assert schema == {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "title": "DcListAnnotation",
        "properties": {
            "a": {
                "type": "array",
                "items": {"type": "integer"},
                "minItems": 3,
                "maxItems": 5,
                "uniqueItems": True,
            },
            "b": {
                "type": "array",
                "items": {"type": "number"},
                "default": [],
                "minItems": 3,
                "maxItems": 10,
            },
        },
        "required": ["a"],
    }


class EnumStr(enum.Enum):
    A = "a"
    B = "b"


@dataclasses.dataclass
class DC:
    a: EnumStr
    b: EnumStr = dataclasses.field(default=EnumStr.A)
    c: EnumStr = dataclasses.field(default_factory=lambda: EnumStr.A)


def test_enum_string():
    schema = get_schema(DC)
    Draft202012Validator.check_schema(schema)
    assert schema == {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "title": "DC",
        "properties": {
            "a": {
                "allOf": [{"$ref": "#/$defs/EnumStr"}],
            },
            "b": {"allOf": [{"$ref": "#/$defs/EnumStr"}], "default": "a"},
            "c": {
                "allOf": [{"$ref": "#/$defs/EnumStr"}],
            },
        },
        "required": ["a"],
        "$defs": {"EnumStr": {"title": "EnumStr", "enum": ["a", "b"]}},
    }


def test_schema_for_any():
    @dataclasses.dataclass
    class DCAny:
        a: t.Any
        b: t.Any = None
        c: t.Any = 1
        d: t.Any = "s"
        e: t.Any = dataclasses.field(default_factory=lambda: DC(EnumStr.A))
        f: t.Any = dataclasses.field(default_factory=lambda: [1, "a"])

    schema = get_schema(DCAny)
    print(schema)
    Draft202012Validator.check_schema(schema)
    assert schema == {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "title": "DCAny",
        "properties": {
            "a": {
                "type": [
                    "null",
                    "string",
                    "boolean",
                    "integer",
                    "number",
                    "object",
                    "array",
                ]
            },
            "b": {
                "type": [
                    "null",
                    "string",
                    "boolean",
                    "integer",
                    "number",
                    "object",
                    "array",
                ],
                "default": None,
            },
            "c": {
                "type": [
                    "null",
                    "string",
                    "boolean",
                    "integer",
                    "number",
                    "object",
                    "array",
                ],
                "default": 1,
            },
            "d": {
                "type": [
                    "null",
                    "string",
                    "boolean",
                    "integer",
                    "number",
                    "object",
                    "array",
                ],
                "default": "s",
            },
            "e": {
                "type": [
                    "null",
                    "string",
                    "boolean",
                    "integer",
                    "number",
                    "object",
                    "array",
                ]
            },
            "f": {
                "type": [
                    "null",
                    "string",
                    "boolean",
                    "integer",
                    "number",
                    "object",
                    "array",
                ]
            },
        },
        "required": ["a"],
    }


def test_schema_additiona_properties_are_not_allowed():
    @dataclasses.dataclass
    class DC:
        a: int

        class SchemaConfig:
            annotation = SchemaAnnotation(additional_properties=False)

    schema = get_schema(DC)
    print(schema)
    Draft202012Validator.check_schema(schema)

    assert schema == {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "title": "DC",
        "additionalProperties": False,
        "properties": {"a": {"type": "integer"}},
        "required": ["a"],
    }


def test_object_pattern_properties():
    @dataclasses.dataclass
    class DC:
        a: t.Annotated[
            dict[str, t.Union[int, str]],
            SchemaAnnotation(
                additional_properties=False,
                pattern_properties={
                    "^I_.*$": {"type": "integer"},
                    "^S_.*$": {"type": "string"},
                },
            ),
        ]

    schema = get_schema(DC)
    print(schema)
    Draft202012Validator.check_schema(schema)

    assert schema == {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "title": "DC",
        "properties": {
            "a": {
                "type": "object",
                "additionalProperties": False,
                "patternProperties": {
                    "^I_.*$": {"type": "integer"},
                    "^S_.*$": {"type": "string"},
                },
            }
        },
        "required": ["a"],
    }

    # valid
    jsonschema.validate({"a": {"I_a": 1, "S_b": "foo"}}, schema=schema)

    with pytest.raises(jsonschema.ValidationError):
        # because abc is not defined in pattern_properties
        jsonschema.validate({"a": {"abc": "1"}}, schema=schema)

    with pytest.raises(jsonschema.ValidationError):
        # raises because I_a expects an integer
        jsonschema.validate({"a": {"I_a": "1", "S_b": "foo"}}, schema=schema)

    with pytest.raises(jsonschema.ValidationError):
        # raises because S_b expects a string
        jsonschema.validate({"a": {"S_b": 123}}, schema=schema)
