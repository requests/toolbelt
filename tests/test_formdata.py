"""Test module for requests_toolbelt.utils.formdata."""
try:
    from urllib.parse import parse_qs, parse_qsl
    from urllib.parse import urlencode as standard_urlencode
except ImportError:
    from urlparse import parse_qs, parse_qsl
    from urllib import urlencode as standard_urlencode

from requests_toolbelt.utils.formdata import urlencode

import pytest

dict_query = {
    'first_nested': {
        'second_nested': {
            'third_nested': {
                'fourth0': 'fourth_value0',
                'fourth1': 'fourth_value1',
            },
            'third0': 'third_value0',
        },
        'second0': 'second_value0',
    },
    'outter': 'outter_value',
}

list_query = [
    ('first_nested', [
        ('second_nested', [
            ('third_nested', [
                ('fourth0', 'fourth_value0'),
                ('fourth1', 'fourth_value1'),
            ]),
            ('third0', 'third_value0'),
        ]),
        ('second0', 'second_value0'),
    ]),
    ('outter', 'outter_value'),
]

mixed_dict_query = {
    'first_nested': {
        'second_nested': [
            ('third_nested', {
                'fourth0': 'fourth_value0',
                'fourth1': 'fourth_value1',
            }),
            ('third0', 'third_value0'),
        ],
        'second0': 'second_value0',
    },
    'outter': 'outter_value',
}

expected_parsed_query = {
    'first_nested[second0]': ['second_value0'],
    'first_nested[second_nested][third0]': ['third_value0'],
    'first_nested[second_nested][third_nested][fourth0]': ['fourth_value0'],
    'first_nested[second_nested][third_nested][fourth1]': ['fourth_value1'],
    'outter': ['outter_value'],
}


@pytest.mark.parametrize("query", [dict_query, list_query, mixed_dict_query])
def test_urlencode_flattens_nested_structures(query):
    """Show that when parsed, the structure is conveniently flat."""
    parsed = parse_qs(urlencode(query))

    assert parsed == expected_parsed_query


def test_urlencode_catches_invalid_input():
    """Show that queries are loosely validated."""
    with pytest.raises(ValueError):
        urlencode(['fo'])

    with pytest.raises(ValueError):
        urlencode([('foo', 'bar', 'bogus')])


@pytest.mark.parametrize("doseq", [False, True])
@pytest.mark.parametrize("value", [1, 0, True, None, 1.25, b"abc", "abc"])
@pytest.mark.parametrize("as_mapping", [False, True])
@pytest.mark.parametrize("shape", ["flat", "leaf", "sibling", "deep_sibling"])
def test_urlencode_preserves_scalar_leaves(value, as_mapping, shape, doseq):
    """Nested containers must not change how scalar leaves are encoded."""
    query = [("page", value)]
    expected = [("page", value)]
    if shape == "leaf":
        query = [("filter", {"page": value})]
        expected = [("filter[page]", value)]
    elif shape == "sibling":
        query.append(("filter", {"name": "report"}))
        expected.append(("filter[name]", "report"))
    elif shape == "deep_sibling":
        query = [("filter", [("page", value), ("match", {"name": "report"})])]
        expected = [("filter[page]", value), ("filter[match][name]", "report")]
    if as_mapping:
        query = dict(query)

    actual_encoded = urlencode(query, doseq=doseq)
    expected_encoded = standard_urlencode(expected, doseq=doseq)
    assert parse_qsl(actual_encoded, keep_blank_values=True) == parse_qsl(
        expected_encoded, keep_blank_values=True
    )


class PairIterable(object):
    def __iter__(self):
        return iter([("name", "report")])


class PairSequence(object):
    def __getitem__(self, index):
        return [("name", "report")][index]


def user_dict():
    try:
        from collections import UserDict
    except ImportError:
        from UserDict import UserDict
    return UserDict({"name": "report"})


@pytest.mark.parametrize("factory", [
    user_dict, PairIterable, PairSequence,
    lambda: ((k, v) for k, v in [("name", "report")]),
])
def test_urlencode_preserves_existing_pair_iterables(factory):
    """Retain nonbuiltin pair containers when another value needs expansion."""
    query = [("filter", factory()), ("trigger", {"name": "other"})]
    assert parse_qs(urlencode(query)) == {
        "filter[name]": ["report"], "trigger[name]": ["other"],
    }


class BrokenItems(object):
    def items(self):
        raise TypeError("broken items")


class BrokenIter(object):
    def __iter__(self):
        raise TypeError("broken iter")


class BrokenNext(object):
    def __iter__(self):
        yield ("name", "report")
        raise TypeError("broken next")


@pytest.mark.parametrize("factory", [
    BrokenItems, BrokenIter, BrokenNext, lambda: iter([1]),
])
def test_urlencode_propagates_pair_container_errors(factory):
    """Do not silently convert broken pair containers to scalar strings."""
    query = [("filter", factory()), ("trigger", {"name": "other"})]
    with pytest.raises(TypeError):
        urlencode(query)
